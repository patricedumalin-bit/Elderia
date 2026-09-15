from elderia.data.tables import FINS_MAJEURES
from elderia.core.ending_variants import normaliser_trait


SUCCES_NARRATIFS = {
    "pain_chaud": "Le pain est encore chaud",
    "montagne_respire": "Une montagne respire encore",
    "fleche_retenue": "La flèche n'est pas partie",
    "masque_repondu": "Le masque a répondu",
    "couronne_connait": "La couronne a appris votre nom",
    "porte_fermee": "Une porte reste fermée",
    "cendre_change": "La cendre a changé de camp",
    "dernier_geolier": "Le dernier geôlier demeure",
    "temps_repare": "Le Temps a accepté la nuance",
    "verite_pardon": "La vérité a précédé le pardon",
    "lecteur_cendres": "Les cendres ont laissé une phrase",
    "mira_confiance": "Mira vous a cru avant le monde",
    "gardien_lettres": "Une lettre n'a pas brûlé",
}


RELIQUES_DE_FIN = {
    "Fin du Sacrifice": "Cendre chaude du Sceau",
    "Fin du Roi": "Anneau sans couronne",
    "Fin du Gardien": "Éclat immobile",
    "Fin du Héros": "Fragment sans magie",
    "Fin du Tyran": "Sceau noirci",
    "Fin Secrète": "Fil du Temps restauré",
    "Fin d'Ashkar Préservée": "Pierre verte d'Ashkar",
    "Fin de la Coalition Brisée": "Bannière sans maître",
    "Fin des Cristaux Scellés": "Rivet de fer froid",
    "Fin du Geôlier Maintenu": "Clef qui refuse de tourner",
}


def ajouter_unique(liste, valeur):
    if valeur not in liste:
        liste.append(valeur)
        return True
    return False


def statut_compagnon(joueur, nom):
    score = joueur.loyautes.get(nom, 0)
    present = nom in joueur.compagnons
    if nom == "Lyra":
        if joueur.variables.get("lyra_garde_fou"):
            return "garde-fou"
        if score >= 60:
            return "alliée fidèle"
        if score < 0:
            return "rupture"
        return "alliée prudente" if present else "absente"
    if nom == "Garrick":
        if score >= 60:
            return "père reconnu"
        if joueur.variables.get("garrick_sauve"):
            return "mentor sauvé"
        return "mentor absent" if not present else "mentor coupable"
    if nom == "Borin":
        if score >= 40:
            return "frère d'armes"
        return "allié nain" if present else "absent"
    if nom == "Morvayn":
        if joueur.variables.get("morvayn_recrute"):
            return "allié impossible"
        if joueur.variables.get("morvayn_epargne"):
            return "épargné"
        if joueur.variables.get("morvayn_tue"):
            return "absent"
        return "ennemi"
    if nom == "Kael":
        if score >= 50:
            return "garde du corps loyal"
        return "espion retourné" if present else "absent"
    if nom == "Selene":
        if score >= 50:
            return "conseillère de confiance"
        return "sorcière alliée" if present else "absente"
    if nom == "Elara":
        if score >= 50:
            return "amie fidèle"
        return "rescapée reconnaissante" if present else "absente"
    if nom == "Mira aux Corbeaux":
        if score >= 50:
            return "informatrice dévouée"
        return "alliée des rues" if present else "absente"
    return "inconnu"


def statuts_compagnons(joueur):
    return {nom: statut_compagnon(joueur, nom) for nom in ["Garrick", "Lyra", "Borin", "Morvayn", "Kael", "Selene", "Elara", "Mira aux Corbeaux"]}


def ajouter_blessure(joueur, blessure):
    if not hasattr(joueur, "blessures_narratives"):
        joueur.blessures_narratives = []
    if ajouter_unique(joueur.blessures_narratives, blessure):
        joueur.journal.append(f"Blessure narrative : {blessure}.")
        return True
    return False


def reparer_blessure(joueur, blessure, trace):
    if blessure in getattr(joueur, "blessures_narratives", []):
        joueur.blessures_narratives.remove(blessure)
        ajouter_unique(joueur.traits_route, trace)
        joueur.journal.append(f"Blessure apaisée : {blessure}.")
        return True
    return False


def actualiser_blessures(joueur):
    if joueur.tension_fragment >= 10:
        ajouter_blessure(joueur, "Cicatrice temporelle")
    if joueur.variables.get("poids_solitaire_cristaux"):
        ajouter_blessure(joueur, "Solitude du Porteur")
    if joueur.variables.get("cristaux_utilises_dangereusement"):
        ajouter_blessure(joueur, "Honte des Cristaux")
    if joueur.reputation_criminelle >= 3:
        ajouter_blessure(joueur, "Méfiance d'Aldor")
    if joueur.allie_politique == "Ligue de Varken":
        ajouter_blessure(joueur, "Dette de Varken")

    if joueur.variables.get("renonce_tyrannie"):
        reparer_blessure(joueur, "Solitude du Porteur", "Solitude refusée")
    if joueur.variables.get("commandement_compatissant"):
        reparer_blessure(joueur, "Honte des Cristaux", "Pouvoir retenu")


def ajouter_reve_dynamique(joueur, reve):
    if ajouter_unique(joueur.reves, reve):
        joueur.journal.append(f"Écho de rêve : {reve}.")
        return True
    return False


def actualiser_reves_dynamiques(joueur):
    if joueur.variables.get("nouvelle_route_plus"):
        ajouter_reve_dynamique(joueur, "Une version de vous connaît déjà le chemin de Brumebois")
    if joueur.variables.get("morvayn_recrute"):
        ajouter_reve_dynamique(joueur, "Une cendre refuse de tomber")
    if joueur.variables.get("cristal_prioritaire") == "Cristal des Ombres":
        ajouter_reve_dynamique(joueur, "Une cité morte sans lumière")
    if joueur.variables.get("cristal_prioritaire") == "Cristal des Esprits":
        ajouter_reve_dynamique(joueur, "Des morts qui attendent votre réponse")
    if joueur.variables.get("cristal_prioritaire") == "Cristal des Marées":
        ajouter_reve_dynamique(joueur, "Une mer au-dessus des montagnes")
    if joueur.variables.get("commandement_efficace"):
        ajouter_reve_dynamique(joueur, "Des soldats sans visage avancent au même pas")
    if "Le pain chaud de Mira" in getattr(joueur, "souvenirs", []):
        ajouter_reve_dynamique(joueur, "Du pain chaud dans une maison en flammes")


def attribuer_succes_narratifs(joueur):
    succes = getattr(joueur, "succes_narratifs", [])
    traits = {normaliser_trait(trait) for trait in getattr(joueur, "traits_route", [])}
    if "Le pain chaud de Mira" in getattr(joueur, "souvenirs", []):
        ajouter_unique(succes, SUCCES_NARRATIFS["pain_chaud"])
    if joueur.variables.get("garrick_sauve"):
        ajouter_unique(succes, SUCCES_NARRATIFS["couronne_connait"])
    if joueur.variables.get("renonce_tyrannie"):
        ajouter_unique(succes, SUCCES_NARRATIFS["fleche_retenue"])
    if joueur.variables.get("morvayn_recrute"):
        ajouter_unique(succes, SUCCES_NARRATIFS["cendre_change"])
    elif joueur.variables.get("morvayn_epargne"):
        ajouter_unique(succes, SUCCES_NARRATIFS["masque_repondu"])
    if joueur.fin_majeure == "Fin d'Ashkar Préservée" or "La cicatrice d'Ashkar" in getattr(joueur, "souvenirs", []):
        ajouter_unique(succes, SUCCES_NARRATIFS["montagne_respire"])
    if joueur.fin_majeure == "Fin du Geôlier Maintenu":
        ajouter_unique(succes, SUCCES_NARRATIFS["dernier_geolier"])
    if joueur.fin_majeure == "Fin Secrète":
        ajouter_unique(succes, SUCCES_NARRATIFS["temps_repare"])
    if getattr(joueur, "portes_fermees", []):
        ajouter_unique(succes, SUCCES_NARRATIFS["porte_fermee"])
    if normaliser_trait("Vérité avant pardon") in traits:
        ajouter_unique(succes, SUCCES_NARRATIFS["verite_pardon"])
    if normaliser_trait("Lecteur des cendres") in traits or normaliser_trait("Piste de Morvayn") in traits:
        ajouter_unique(succes, SUCCES_NARRATIFS["lecteur_cendres"])
    if normaliser_trait("Écouté par Mira") in traits or normaliser_trait("Confiance de Mira") in traits:
        ajouter_unique(succes, SUCCES_NARRATIFS["mira_confiance"])
    if normaliser_trait("Gardien des lettres") in traits:
        ajouter_unique(succes, SUCCES_NARRATIFS["gardien_lettres"])
    joueur.succes_narratifs = succes
    return succes


def ajouter_relique_de_fin(joueur):
    relique = RELIQUES_DE_FIN.get(joueur.fin_majeure)
    if not relique:
        return False
    if not hasattr(joueur, "reliques_run"):
        joueur.reliques_run = []
    if ajouter_unique(joueur.reliques_run, relique):
        joueur.journal.append(f"Relique de run : {relique}.")
        return True
    return False


def score_completion(joueur):
    from elderia.core.codex import CODEX_ENTRIES, SOUVENIRS_ENTRIES

    total = len(FINS_MAJEURES) + len(CODEX_ENTRIES) + len(SOUVENIRS_ENTRIES) + len(SUCCES_NARRATIFS)
    courant = (
        len(getattr(joueur, "fins_atteintes", []))
        + len(getattr(joueur, "codex", {}))
        + len(getattr(joueur, "souvenirs", []))
        + len(getattr(joueur, "succes_narratifs", []))
    )
    return round((courant / total) * 100) if total else 0


def enregistrer_run(joueur):
    if not joueur.fin_majeure:
        return False
    if not hasattr(joueur, "historique_runs"):
        joueur.historique_runs = []
    signature = {
        "fin": joueur.fin_majeure,
        "classe": joueur.classe,
        "allie": joueur.allie_politique,
        "cristal": joueur.variables.get("cristal_prioritaire"),
    }
    for run in joueur.historique_runs:
        if all(run.get(cle) == valeur for cle, valeur in signature.items()):
            return False
    resume = {
        **signature,
        "traits": list(getattr(joueur, "traits_route", [])[-8:]),
    }
    joueur.historique_runs.append(resume)
    return True


def actualiser_meta_progression(joueur):
    actualiser_blessures(joueur)
    actualiser_reves_dynamiques(joueur)
    attribuer_succes_narratifs(joueur)
    if joueur.fin_majeure:
        ajouter_relique_de_fin(joueur)
        enregistrer_run(joueur)


def resume_meta(joueur):
    actualiser_meta_progression(joueur)
    lignes = [
        f"Découverte globale : {score_completion(joueur)} %.",
        f"Histoires achevées : {len(getattr(joueur, 'historique_runs', []))}.",
        f"Succès narratifs : {len(getattr(joueur, 'succes_narratifs', []))} / {len(SUCCES_NARRATIFS)}.",
        f"Blessures narratives : {', '.join(getattr(joueur, 'blessures_narratives', [])) if getattr(joueur, 'blessures_narratives', []) else 'aucune'}.",
        f"Reliques de run : {', '.join(getattr(joueur, 'reliques_run', [])) if getattr(joueur, 'reliques_run', []) else 'aucune'}.",
    ]
    return "\n".join(lignes)