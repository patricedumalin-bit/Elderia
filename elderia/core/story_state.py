def a_lien_avec_marek(joueur):
    return joueur.a_consequence("Marek vous respecte") or joueur.a_consequence("Marek respecte votre courage")


def a_baume_de_mira(joueur):
    return "Baume de Mira" in joueur.inventaire


def fragment_instable(joueur):
    return joueur.tension_fragment >= 5


def fragment_sous_pression(joueur):
    return joueur.tension_fragment >= 3


def comprend_arthen(joueur):
    return joueur.connaissance_temporelle >= 3 or joueur.variables.get("secret_arthen", 0) >= 2


def morvayn_respecte_le_joueur(joueur):
    return joueur.respect_morvayn >= 1


def faction_dominante(joueur):
    if not joueur.factions:
        return None
    faction = max(joueur.factions, key=joueur.factions.get)
    return faction if joueur.factions[faction] > 0 else None


def voie_alignement(joueur):
    if joueur.alignement >= 3:
        return "lumiere"
    if joueur.alignement <= -3:
        return "ombre"
    return "neutre"


def est_recherche_par_aldor(joueur):
    return joueur.reputation_criminelle >= 3 or "Protection publique de la couronne" in joueur.portes_fermees


def morvayn_est_alerte(joueur):
    return joueur.variables.get("morvayn_alerte", False)


def garrick_est_localise(joueur):
    return joueur.variables.get("garrick_localise", False)


def garrick_est_recherche(joueur):
    return joueur.variables.get("garrick_recherche", False)


def garrick_est_sauve(joueur):
    return joueur.variables.get("garrick_sauve", False)


def a_choisi_alliance(joueur):
    return joueur.variables.get("alliance_choisie") is not None or joueur.allie_politique is not None


def elara_est_sauvee(joueur):
    return joueur.variables.get("elara_sauvee", False)


def prisonnier_sans_age_libere(joueur):
    return joueur.variables.get("prisonnier_libere", False)


def ancien_allie_temporel(joueur):
    return joueur.variables.get("ancien_allie", False)


def bourreau_est_capture(joueur):
    return joueur.variables.get("bourreau_capture", False)


def morvayn_est_tue(joueur):
    return joueur.variables.get("morvayn_tue", False)


def morvayn_est_epargne(joueur):
    return joueur.variables.get("morvayn_epargne", False)


def morvayn_est_recrute(joueur):
    return joueur.variables.get("morvayn_recrute", False)


def connait_assez_malakar(joueur):
    return joueur.variables.get("secret_malakar", 0) >= 2


def connait_assez_morvayn(joueur):
    return joueur.variables.get("secret_morvayn", 0) >= 2
