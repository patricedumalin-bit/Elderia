import random

from elderia.core.io import demander_choix, effet_combat, lancer_de, maj_combat, raconter
from elderia.core.equipment import (
    generer_variante_arme,
    generer_variante_armure,
    generer_variante_bouclier,
    generer_variante_bijou,
    palier_ennemi,
)
from elderia.data.tables import ARMES, ARMURES, BOUCLIERS, BIJOUX, CAPACITES_SPECIALES, COMPAGNONS_STATS, COMPETENCES, ENNEMIS, LOOTS

def creer_ennemi(cle, **modifications):
    if cle not in ENNEMIS:
        raise ValueError(f"Ennemi inconnu : {cle}")
    ennemi = dict(ENNEMIS[cle])
    ennemi.update(modifications)
    ennemi.setdefault("type", cle)
    return ennemi


def type_ennemi(ennemi):
    nom = ennemi.get("type", ennemi.get("nom", ""))
    if nom in ENNEMIS:
        return nom
    for cle in ENNEMIS:
        if cle in nom:
            return cle
    return nom


def capacite_speciale_ennemi(nom):
    for cle, capacite in CAPACITES_SPECIALES.items():
        if cle in nom:
            return capacite
    return None


def donner_loot(joueur, ennemi):
    cle = type_ennemi(ennemi)
    objets = LOOTS.get(cle, [])
    if not objets:
        return
    objet = random.choice(objets)
    if not objet:
        return
    palier = palier_ennemi(ennemi)
    effet_bijou, valeur_bijou = joueur.effet_bijou
    bonus_rarete = valeur_bijou / 100 if effet_bijou == "bonus_loot" else 0.0
    if objet in ARMES:
        objet, _ = generer_variante_arme(objet, palier, joueur.difficulte, bonus_rarete)
    elif objet in ARMURES:
        objet, _ = generer_variante_armure(objet, palier, joueur.difficulte, bonus_rarete)
    elif objet in BOUCLIERS:
        objet, _ = generer_variante_bouclier(objet, palier, joueur.difficulte, bonus_rarete)
    elif objet in BIJOUX:
        objet, _ = generer_variante_bijou(objet, palier, joueur.difficulte, bonus_rarete)
    if not joueur.ajouter_objet(objet):
        return
    raconter(f"🎁 Butin obtenu : {objet}.")
    if objet in ARMES and joueur.arme_est_meilleure(objet):
        joueur.equiper_arme(objet)
    elif objet in ARMURES and joueur.armure_est_meilleure(objet):
        joueur.equiper_armure(objet)
    elif objet in BOUCLIERS and joueur.bouclier_est_meilleure(objet):
        joueur.equiper_bouclier(objet)
    elif objet in BIJOUX and joueur.bijou_est_meilleur(objet):
        joueur.equiper_bijou(objet)


def attaque_compagnons(joueur, ennemi):
    degats_total = 0
    defense_ennemi = defense_totale(ennemi)
    # Les compagnons montent en puissance avec le héros (+15 % tous les 5 niveaux) pour rester utiles en fin d'histoire.
    facteur_niveau = 1 + (joueur.niveau // 5) * 0.15
    for compagnon in joueur.compagnons:
        stats = COMPAGNONS_STATS.get(compagnon)
        if stats:
            # La loyauté (0-100) ajoute jusqu'à +50 % de dégâts à un compagnon pleinement fidèle.
            facteur_loyaute = 1 + joueur.loyautes.get(compagnon, 0) / 200
            facteur = facteur_niveau * facteur_loyaute
            force_effective = round(stats["force"] * facteur)
            naturel, attaque = lancer_attaque(force_effective)
            if naturel == 1 or attaque < defense_ennemi:
                raconter(f"{compagnon} attaque mais rate sa cible.")
                continue
            degats = max(1, round(stats["degats"] * facteur) + force_effective // 2 - ennemi.get("armure", 0))
            degats_total += degats
            raconter(f"{compagnon} inflige {degats} dégâts.")
    if joueur.a_talent("Commandement I"):
        degats_total = round(degats_total * 1.1)
    bonus_compagnons = joueur.effets_talents_arbre().get("bonus_compagnons", {}).get("valeur", 0)
    if bonus_compagnons:
        degats_total = round(degats_total * (1 + bonus_compagnons))

    # Soutien passif basé sur le Lien
    for compagnon in joueur.compagnons:
        lien = joueur.niveau_lien(compagnon)
        if lien >= 2 and random.random() < 0.2: # 20% de chance de soutien
            soutien_compagnon(joueur, compagnon, lien)

    return degats_total

def soutien_compagnon(joueur, compagnon, lien):
    """Actions de soutien basées sur le niveau de lien."""
    if lien == 2: # Compagnon d'arme
        soin = 3 + joueur.niveau // 2
        joueur.pv = min(joueur.pv_max, joueur.pv + soin)
        raconter(f"🛡️ {compagnon} vous protège ! (+{soin} PV)")
    elif lien == 3: # Allié fidèle
        joueur.energie = min(joueur.energie_max, joueur.energie + 2)
        raconter(f"⚡ {compagnon} vous encourage ! (+2 Énergie)")
    elif lien >= 4: # Âme soeur
        soin = 10 + joueur.niveau
        joueur.pv = min(joueur.pv_max, joueur.pv + soin)
        joueur.pm = min(joueur.pm_max, joueur.pm + 5)
        raconter(f"✨ {compagnon} libère une onde de choc curative ! (+{soin} PV, +5 PM)")


def lancer_attaque(bonus_attaque, avantage=False, desavantage=False):
    naturel = lancer_de(20, avantage=avantage, desavantage=desavantage)
    return naturel, naturel + bonus_attaque


def defense_totale(defenseur):
    return 10 + defenseur.get("agilite", 0) + defenseur.get("armure", defenseur.get("defense", 0))


def defense_totale_joueur(joueur):
    return 10 + joueur.defense_combat


def calculer_degats(degats_arme, force_attaquant, armure_cible, bonus=0, critique=False, ignore_armure=False):
    reduction = 0 if ignore_armure else armure_cible
    degats = degats_arme + force_attaquant + bonus - reduction
    if critique:
        degats *= 2
    return max(1, degats)


def depenser_energie(joueur, cout):
    if joueur.energie < cout:
        raconter("❌ Pas assez d'énergie.")
        return False
    joueur.energie -= cout
    return True


def bonus_degats_talents(joueur, ennemi, critique=False):
    """Bonus de dégâts issus de l'arbre de talents de classe, selon le contexte du combat."""
    effets = joueur.effets_talents_arbre()
    bonus = 0
    degats_pv_bas = effets.get("degats_pv_bas")
    if degats_pv_bas and joueur.pv <= joueur.pv_max // 3:
        bonus += degats_pv_bas["valeur"]
    bonus_arme_type = effets.get("bonus_arme_type")
    if bonus_arme_type and bonus_arme_type["mot_cle"] in joueur.arme:
        bonus += bonus_arme_type["valeur"]
    bonus_armure_cible = effets.get("bonus_armure_cible")
    if bonus_armure_cible and ennemi.get("armure", 0) >= 6:
        bonus += bonus_armure_cible["valeur"]
    if critique:
        crit_bonus = effets.get("crit_bonus")
        if crit_bonus:
            bonus += crit_bonus["valeur"]
    return bonus


def peut_utiliser_competence(joueur):
    competence = COMPETENCES.get(joueur.competence)
    if not competence:
        return False
    if competence.get("ressource") == "energie":
        return joueur.energie >= competence["cout"]
    return joueur.pm >= competence["cout"]


def attaquer_joueur(joueur, ennemi, gratuit=False, reduction_blocage=0):
    if gratuit:
        raconter(f"⚠️ Échec critique : {ennemi['nom']} obtient une contre-attaque gratuite !")

    # [WARHAMMER] Les ennemis profitent de votre corruption
    desavantage_joueur = joueur.corruption >= 25
    naturel, attaque = lancer_attaque(ennemi["force"])

    defense_joueur = defense_totale_joueur(joueur)
    if naturel == 1:
        raconter(f"{ennemi['nom']} trébuche et perd son attaque.")
        return
    if naturel == 20 or attaque >= defense_joueur:
        critique = naturel == 20
        blessure = calculer_degats(
            ennemi.get("arme", 2),
            ennemi["force"],
            joueur.defense,
            critique=critique,
            ignore_armure=critique,
        )
        blessure = max(1, round(blessure * joueur.modificateurs["degats_ennemis"]))
        reduction_talent = joueur.effets_talents_arbre().get("reduction_degats", {}).get("valeur", 0)
        if reduction_talent:
            blessure = max(1, blessure - reduction_talent)
        effet_bijou, valeur_bijou = joueur.effet_bijou
        if effet_bijou == "reduction_degats":
            blessure = max(1, blessure - valeur_bijou)
        if reduction_blocage:
            blessure = max(0, blessure - reduction_blocage)
            raconter(f"Votre bouclier absorbe {reduction_blocage} dégâts.")
        joueur.pv = max(0, joueur.pv - blessure)
        suffixe = " Coup critique !" if critique else ""
        raconter(f"Vous subissez {blessure} dégâts.{suffixe}")
        effet_combat("critique" if critique else "joueur_touche")

        if joueur.pv <= 0:
            # [D&D/WARHAMMER] Blessures Graves à 0 PV
            blessures_possibles = ["Côtes fêlées (-1 END)", "Main tremblante (-1 FOR)", "Traumatisme (-1 VOL)"]
            blessure_g = random.choice(blessures_possibles)
            joueur.subir_blessure_grave(blessure_g)
    else:
        raconter(f"Vous évitez l'attaque ({attaque}) contre votre défense {defense_joueur}.")


def utiliser_competence(joueur, ennemi):
    effets = joueur.effets_talents_arbre()
    bonus_competence = effets.get("bonus_competence_degats", {}).get("valeur", 0)
    reduction_cout = effets.get("reduction_cout_competence", {}).get("valeur", 0)
    bonus_soin = effets.get("bonus_soin", {}).get("valeur", 0)

    if joueur.competence == "Coup Puissant":
        competence = COMPETENCES[joueur.competence]
        if not depenser_energie(joueur, competence["cout"]):
            return 0
        degats = calculer_degats(joueur.bonus_arme["degats"], joueur.force_totale, ennemi["armure"], bonus=competence["degats_bonus"] + bonus_degats_talents(joueur, ennemi) + bonus_competence)
        raconter(f"💥 Coup Puissant inflige {degats} dégâts.")
        return degats

    if joueur.competence == "Tir Rapide":
        competence = COMPETENCES[joueur.competence]
        if not depenser_energie(joueur, competence["cout"]):
            return 0
        force_tir = joueur.force_totale + joueur.agilite_totale // 2
        degats = (calculer_degats(joueur.bonus_arme["degats"], force_tir, ennemi["armure"]) + bonus_degats_talents(joueur, ennemi) + bonus_competence) * competence["attaques"]
        raconter(f"🏹 Tir Rapide inflige {degats} dégâts en deux attaques.")
        return degats

    if joueur.competence == "Boule de Feu":
        competence = COMPETENCES[joueur.competence]
        cout = max(1, competence["cout"] - reduction_cout) if reduction_cout else competence["cout"]
        if joueur.pm < cout:
            raconter("❌ Pas assez de mana.")
            return 0

        # [WARHAMMER] Fiasco Magique sur 1 naturel
        de_lancer = lancer_de(20)
        if de_lancer == 1:
            raconter("✨ [FIASCO MAGIQUE] L'énergie arcanique se retourne contre vous !")
            joueur.pv -= 5
            joueur.ajouter_corruption(2)
            return 0

        joueur.pm -= cout
        degats = sum(lancer_de(de) for de in competence["des"]) + bonus_competence + joueur.intelligence_totale // 2
        raconter(f"🔥 Boule de Feu inflige {degats} dégâts.")
        return degats

    if joueur.competence == "Réveil des Cendres":
        competence = COMPETENCES[joueur.competence]
        cout = max(1, competence["cout"] - reduction_cout) if reduction_cout else competence["cout"]
        if joueur.pm < cout:
            raconter("❌ Pas assez de mana.")
            return 0
        joueur.pm -= cout
        degats = sum(lancer_de(de) for de in competence["des"]) + bonus_competence + joueur.volonte // 2
        raconter(f"💀 Réveil des Cendres inflige {degats} dégâts.")
        return degats

    if joueur.competence == "Lumière Sacrée":
        competence = COMPETENCES[joueur.competence]
        if joueur.pm < competence["cout"]:
            raconter("❌ Pas assez de mana.")
            return 0
        joueur.pm -= competence["cout"]
        soin = sum(lancer_de(de) for de in competence["soin_des"]) + bonus_soin + joueur.volonte // 2
        joueur.pv = min(joueur.pv_max, joueur.pv + soin)
        raconter(f"✨ Lumière Sacrée rend {soin} PV.")
        return 0

    return 0


def lancer_combat(joueur, ennemi):
    if isinstance(ennemi, str):
        ennemi = creer_ennemi(ennemi)
    nom = ennemi["nom"]
    pv_ennemi = ennemi["pv"]
    raconter(f"\n⚔️ {nom} vous attaque !")

    initiative_joueur = lancer_de(20) + joueur.agilite_totale
    initiative_ennemi = lancer_de(20) + ennemi.get("agilite", 0)
    raconter(f"Initiative : vous {initiative_joueur}, {nom} {initiative_ennemi}.")
    if initiative_ennemi > initiative_joueur:
        print(f"\n⚡ {nom} agit le premier !")
        attaquer_joueur(joueur, ennemi)

    while pv_ennemi > 0 and joueur.pv > 0:
        effet_bijou, valeur_bijou = joueur.effet_bijou
        if effet_bijou == "regen_pv" and joueur.pv < joueur.pv_max:
            soin_bijou = min(valeur_bijou, joueur.pv_max - joueur.pv)
            joueur.pv += soin_bijou
            raconter(f"💍 {joueur.bijou} vous régénère {soin_bijou} PV.")
        elif effet_bijou == "regen_ressource":
            ressource = COMPETENCES.get(joueur.competence, {}).get("ressource", "mana")
            if ressource == "energie" and joueur.energie < joueur.energie_max:
                gain_bijou = min(valeur_bijou, joueur.energie_max - joueur.energie)
                joueur.energie += gain_bijou
                raconter(f"💍 {joueur.bijou} restaure {gain_bijou} énergie.")
            elif ressource != "energie" and joueur.pm < joueur.pm_max:
                gain_bijou = min(valeur_bijou, joueur.pm_max - joueur.pm)
                joueur.pm += gain_bijou
                raconter(f"💍 {joueur.bijou} restaure {gain_bijou} mana.")
        joueur.afficher_statistiques()
        print(f"👹 {nom} | PV {pv_ennemi}/{ennemi['pv']} | AGI {ennemi['agilite']} | Armure {ennemi['armure']}")
        maj_combat(joueur, ennemi, pv_ennemi)
        actions = ["Attaquer"]
        if peut_utiliser_competence(joueur):
            actions.append(f"Utiliser {joueur.competence}")
        actions.append("Boire une potion")
        actions.append("Manger une ration")
        if joueur.bouclier:
            actions.append("Bloquer")
        for index, action in enumerate(actions, 1):
            print(f"{index}. {action}")
        action_choisie = actions[demander_choix("Action > ", actions, combat=True)]

        if action_choisie == "Attaquer":
            # [D&D] Avantage si l'ennemi est surpris ou via talent (exemple ici simplifié)
            avantage = "Précision" in joueur.traits_route
            naturel, attaque = lancer_attaque(joueur.force_totale, avantage=avantage)
            if naturel == 1:
                raconter("Votre attaque manque totalement sa cible.")
                attaquer_joueur(joueur, ennemi, gratuit=True)
            elif naturel == 20 or attaque >= defense_totale(ennemi):
                critique = naturel == 20
                if not critique and effet_bijou == "bonus_critique" and random.random() < valeur_bijou / 100:
                    critique = True
                degats = calculer_degats(
                    joueur.bonus_arme["degats"],
                    joueur.force_totale,
                    ennemi["armure"],
                    bonus=bonus_degats_talents(joueur, ennemi, critique=critique),
                    critique=critique,
                    ignore_armure=critique,
                )
                pv_ennemi -= degats
                suffixe = " Coup critique !" if critique else ""
                raconter(f"Vous touchez ({attaque}) et infligez {degats} dégâts.{suffixe}")
                effet_combat("critique" if critique else "ennemi_touche")
                if effet_bijou == "vol_vie":
                    soin_vol = max(0, round(degats * valeur_bijou / 100))
                    if soin_vol:
                        joueur.pv = min(joueur.pv_max, joueur.pv + soin_vol)
                        raconter(f"🩸 {joueur.bijou} vous rend {soin_vol} PV.")
            else:
                raconter(f"Votre attaque ({attaque}) ne dépasse pas la défense {defense_totale(ennemi)}.")
        elif action_choisie == f"Utiliser {joueur.competence}":
            degats_competence = utiliser_competence(joueur, ennemi)
            if degats_competence > 0:
                effet_combat("ennemi_touche")
            pv_ennemi -= degats_competence
        elif action_choisie == "Boire une potion":
            joueur.utiliser_potion()
        elif action_choisie == "Manger une ration":
            joueur.utiliser_ration()
        else:
            bonus_bouclier = joueur.bonus_bouclier["blocage"]
            reduction_blocage = lancer_de(6) + bonus_bouclier
            raconter(f"Vous levez {joueur.bouclier} et préparez un blocage de {reduction_blocage} dégâts.")
            effet_combat("bloque")

        if pv_ennemi > 0:
            pv_ennemi -= attaque_compagnons(joueur, ennemi)

        if pv_ennemi <= 0:
            raconter(f"🏆 {nom} est vaincu !")
            effet_combat("victoire")
            or_gagne = round(ennemi.get("or", 0) * joueur.modificateurs["or"])
            if joueur.a_talent("Porteur Victorieux"):
                or_gagne = round(or_gagne * 1.15)
            if or_gagne:
                joueur.or_poches += or_gagne
                raconter(f"Vous trouvez {or_gagne} pièces d'or.")
            donner_loot(joueur, ennemi)
            joueur.ajouter_xp(ennemi["xp"])
            return True

        print(f"\n⚡ {nom} riposte !")
        capacite = capacite_speciale_ennemi(nom)
        if capacite and random.random() < capacite["chance"]:
            degats_speciaux = max(1, round(sum(lancer_de(de) for de in capacite["des"]) * joueur.modificateurs["degats_ennemis"]))
            joueur.pv = max(0, joueur.pv - degats_speciaux)
            raconter(f"{nom} utilise {capacite['nom']} et inflige {degats_speciaux} dégâts !")
            effet_combat("critique")
            if capacite.get("vol_vie"):
                pv_ennemi = min(ennemi["pv"], pv_ennemi + degats_speciaux // 2)
                raconter(f"{nom} se soigne de {degats_speciaux // 2} PV.")
            if joueur.pv <= 0:
                break
        attaquer_joueur(joueur, ennemi, reduction_blocage=reduction_blocage if action_choisie == "Bloquer" else 0)

    return False


def lancer_combat_vague(joueur, ennemis):
    """Enchaîne plusieurs combats à la suite ; s'arrête dès que le joueur perd."""
    for ennemi in ennemis:
        if not lancer_combat(joueur, ennemi):
            return False
    return True

__all__ = [
    "creer_ennemi",
    "type_ennemi",
    "donner_loot",
    "attaque_compagnons",
    "lancer_attaque",
    "defense_totale",
    "defense_totale_joueur",
    "calculer_degats",
    "depenser_energie",
    "peut_utiliser_competence",
    "attaquer_joueur",
    "utiliser_competence",
    "lancer_combat",
]
