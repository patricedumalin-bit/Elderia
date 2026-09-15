from elderia.core.io import demander_choix, raconter
from elderia.data.tables import BANTERS_COMPAGNONS


RECOMPENSES_BILAN_ACTE = {
    "ACTE I": {"xp": 500, "or": 40},
    "ACTE II": {"xp": 2500, "or": 120},
    "ACTE III": {"xp": 3500, "or": 90},
    "ACTE IV": {"xp": 4500, "or": 60},
}


def accorder_recompense_bilan(joueur, titre_acte):
    for prefixe, recompense in RECOMPENSES_BILAN_ACTE.items():
        if titre_acte != prefixe and not titre_acte.startswith(f"{prefixe} -"):
            continue
        cle = f"recompense_bilan_{prefixe.lower().replace(' ', '_').replace('é', 'e')}"
        if joueur.variables.get(cle):
            return False
        joueur.variables[cle] = True
        xp = recompense.get("xp", 0)
        or_gagne = recompense.get("or", 0)
        if xp:
            joueur.ajouter_xp(xp)
        if or_gagne:
            joueur.or_poches += or_gagne
            raconter(f"Votre route vous rapporte {or_gagne} pièces d'or en ressources, faveurs et ravitaillement.")
        return True
    return False


def interaction_compagnons(joueur):
    """Fait dialoguer deux compagnons entre eux, pas seulement avec le joueur, s'ils sont tous deux présents.
    Réutilisable à la fois au camp et dans des scènes d'histoire précises pour répartir ces interactions."""
    presents = set(joueur.compagnons)
    vus = joueur.variables.setdefault("banters_vus", [])
    for paire, dialogue in BANTERS_COMPAGNONS.items():
        cle = " & ".join(sorted(paire))
        if paire <= presents and cle not in vus:
            vus.append(cle)
            return dialogue
    return None

def interjection_compagnon(joueur, nom_compagnon, texte):
    """Fait réagir un compagnon spécifique s'il est dans le groupe."""
    if nom_compagnon in joueur.compagnons:
        raconter(f"\n💬 {nom_compagnon} : « {texte} »")
        return True
    return False

def repos_de_camp(joueur, nom_camp):
    raconter(f"\n🏕️ {nom_camp}")
    options = [
        "Soigner les blessures et reprendre des forces",
        "Réparer l'équipement et préparer les armes",
        "Méditer sur le Fragment du Temps",
        "Parler aux compagnons et resserrer les liens",
    ]
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    choix = demander_choix("Repos > ", options, interaction=True)
    if choix == 0:
        soin = max(6, joueur.pv_max // 2)
        joueur.pv = min(joueur.pv_max, joueur.pv + soin)
        joueur.energie = joueur.energie_max
        joueur.pm = min(joueur.pm_max, joueur.pm + max(2, joueur.pm_max // 2))
        raconter("Les soins, le sommeil et la chaleur du camp vous rendent assez de force pour continuer.")
    elif choix == 1:
        joueur.energie = joueur.energie_max
        joueur.ajouter_objet("Ration")
        raconter("Vous préparez votre équipement et ajoutez une ration utilisable à votre sac.")
    elif choix == 2:
        joueur.tension_fragment = max(0, joueur.tension_fragment - 2)
        joueur.connaissance_temporelle += 1
        raconter("Le Fragment se calme légèrement, mais vous comprenez un peu mieux la forme de ses fractures.")
    else:
        for compagnon in joueur.compagnons:
            joueur.loyautes[compagnon] = joueur.loyautes.get(compagnon, 0) + 3
        dialogue = interaction_compagnons(joueur)
        if dialogue:
            raconter(dialogue)
        else:
            raconter("Les conversations ne règlent pas la guerre, mais elles empêchent votre groupe de devenir seulement une escorte.")


def ravitaillement(joueur, nom_lieu):
    raconter(f"\n🧰 Ravitaillement - {nom_lieu}")
    options = [
        ("Acheter deux rations", 8, "rations"),
        ("Acheter une potion de soin", 10, "potion"),
        ("Financer des éclaireurs", 25, "espionnage"),
        ("Payer des soins de camp", 20, "soins"),
        ("Ne rien acheter", 0, "rien"),
    ]
    for index, (label, prix, _) in enumerate(options, 1):
        cout = f" ({prix}g)" if prix else ""
        print(f"{index}. {label}{cout}")
    label, prix, effet = options[demander_choix("Ravitaillement > ", options, interaction=True)]
    if prix and joueur.or_poches < prix:
        raconter("Votre bourse ne suffit pas. Vous gardez votre or pour une autre occasion.")
        return False
    joueur.or_poches -= prix
    if effet == "rations":
        joueur.ajouter_objet("Ration")
        joueur.ajouter_objet("Ration")
        raconter("Deux rations rejoignent votre sac.")
    elif effet == "potion":
        joueur.ajouter_objet("Potion de soin")
        raconter("Une potion de soin rejoint votre inventaire.")
    elif effet == "espionnage":
        joueur.espionnage = getattr(joueur, "espionnage", 0) + 1
        raconter("Les éclaireurs promettent des cartes, des rumeurs et parfois la vérité entre les deux.")
    elif effet == "soins":
        joueur.pv = joueur.pv_max
        joueur.energie = joueur.energie_max
        raconter("Les soigneurs remettent bandages, attelles et courage à peu près en place.")
    else:
        raconter("Vous gardez vos ressources pour plus tard.")
    return True