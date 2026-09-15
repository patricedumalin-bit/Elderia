from elderia.core.io import afficher_titre
from elderia.core.options import appliquer_options, charger_options
from elderia.core.save import charger, sauvegarder
from elderia.core.systems import afficher_prologue, afficher_structure_campagne, creer_personnage
from elderia.core.tome import preparer_heros_acte_3


def afficher_entete():
    afficher_titre()
    afficher_structure_campagne()


def charger_ou_preparer(acte):
    options = charger_options()
    joueur = charger()
    if joueur is not None:
        joueur.options = {**getattr(joueur, "options", {}), **options}
        appliquer_options(joueur.options)
        joueur.acte_courant = _nom_acte(acte)
        return joueur
    if acte == 1:
        afficher_titre()
        afficher_prologue()
        afficher_structure_campagne()
        joueur = creer_personnage()
        joueur.options = dict(options)
        appliquer_options(joueur.options)
        return joueur
    joueur = preparer_heros_acte_3()
    joueur.options = dict(options)
    appliquer_options(joueur.options)
    joueur.acte_courant = _nom_acte(acte)
    return joueur


def _nom_acte(acte):
    noms = {
        1: "Acte I - L'Éveil",
        2: "Acte II - Les Royaumes Déchirés",
        3: "Acte III - La Chasse aux Cristaux",
        4: "Acte IV - La Guerre du Crépuscule",
        5: "Acte V - Le Dernier Âge",
    }
    return noms[acte]


def sauvegarder_fin_acte(joueur):
    sauvegarder(joueur)
    return joueur
