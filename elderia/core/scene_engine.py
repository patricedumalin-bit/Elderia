from elderia.core.io import demander_choix, illustrer, raconter
from elderia.data.tables import ARMES, ARMURES


def afficher_options(options):
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")


def choisir(choices, scene_key, prompt, group="options"):
    options = list(choices[scene_key][group])
    afficher_options(options)
    return demander_choix(prompt, options)


def choisir_nom(choices, scene_key, prompt, group="options"):
    options = list(choices[scene_key][group])
    afficher_options(options)
    return options[demander_choix(prompt, options)]


def texte(outcomes, key):
    return outcomes[key]


def retry_scene(scene, joueur, on_failure):
    while not scene(joueur):
        if not on_failure(joueur):
            return False
    return True


def dire(outcomes, key):
    raconter(outcomes[key])


def transition(outcomes, key):
    raconter("\n" + outcomes[key])

def resonance_temporelle(joueur, vision_key, seuil=2):
    """Affiche un écho du futur si la connaissance temporelle est suffisante."""
    if joueur.connaissance_temporelle >= seuil:
        raconter("\n⏳ [RÉSONANCE TEMPORELLE]")
        raconter(f"Vos sens se brouillent. Une vision fragmentée du futur s'impose à vous :")
        raconter(f"« {vision_key} »")
        raconter("Le présent reprend sa place, mais le poids de l'avenir pèse sur votre cœur.\n")
        return True
    return False

def murmure_corruption(joueur, texte, seuil=15):
    """Insère un murmure hallucinatoire si la corruption est élevée."""
    if joueur.corruption >= seuil:
        raconter(f"\n💀 [MURMURE DES CENDRES] « {texte} »")
        return True
    return False

def fin_prematuree(joueur, outcomes, key, nom_fin):
    from elderia.core.narrative_state import bilan_narratif
    from elderia.core.meta_progression import actualiser_meta_progression
    from elderia.core.options import option_active

    if option_active("confirmer_fins_prematurees"):
        options = ["Confirmer cette fin", "Revenir sur cette décision"]
        afficher_options(options)
        if demander_choix("Fin prématurée > ", options, interaction=True) != 0:
            raconter("Vous retenez ce choix au bord de l'irréversible. L'histoire continue, mais elle se souviendra de cette hésitation.")
            return False

    raconter(bilan_narratif(joueur))
    raconter("\n" + outcomes[key])
    joueur.fin_majeure = nom_fin
    joueur.enregistrer_fin_atteinte()
    actualiser_meta_progression(joueur)
    joueur.acte_courant = "Épilogue"
    joueur.journal.append(f"Épilogue prématuré : {nom_fin}.")
    return True


def consequence(joueur, outcomes, key):
    joueur.ajouter_consequence(outcomes[key])


def secret(joueur, outcomes, key):
    joueur.secrets.append(outcomes[key])


def journal(joueur, outcomes, key):
    joueur.journal.append(outcomes[key])


def reve(joueur, outcomes, key):
    joueur.reves.append(outcomes[key])


def item(joueur, objet):
    if not joueur.ajouter_objet(objet):
        return False
    if objet in ARMES and joueur.arme_est_meilleure(objet):
        joueur.equiper_arme(objet)
    elif objet in ARMURES and joueur.armure_est_meilleure(objet):
        joueur.equiper_armure(objet)
    return True


def recruter(joueur, compagnon):
    if compagnon in joueur.compagnons:
        return False
    joueur.compagnons.append(compagnon)
    return True


def obtenir_cristal(joueur, cristal):
    if cristal in joueur.cristaux:
        return False
    joueur.cristaux.append(cristal)
    return True


def quete(joueur, outcomes, key):
    joueur.terminer_quete(outcomes[key])


def porte_fermee(joueur, outcomes, key):
    joueur.fermer_porte(outcomes[key])


def apply_effects(joueur, outcomes, effects):
    for effect in effects:
        kind = effect[0]
        if kind == "response":
            dire(outcomes, effect[1])
        elif kind == "consequence":
            consequence(joueur, outcomes, effect[1])
        elif kind == "secret":
            secret(joueur, outcomes, effect[1])
        elif kind == "journal":
            journal(joueur, outcomes, effect[1])
        elif kind == "dream":
            reve(joueur, outcomes, effect[1])
        elif kind == "item":
            item(joueur, effect[1])
        elif kind == "companion":
            recruter(joueur, effect[1])
        elif kind == "crystal":
            obtenir_cristal(joueur, effect[1])
        elif kind == "quest":
            quete(joueur, outcomes, effect[1])
        elif kind == "locked_path":
            porte_fermee(joueur, outcomes, effect[1])
        elif kind == "faction":
            joueur.modifier_faction(effect[1], effect[2])
        elif kind == "score":
            setattr(joueur, effect[1], getattr(joueur, effect[1], 0) + effect[2])
        elif kind == "stat":
            setattr(joueur, effect[1], getattr(joueur, effect[1]) + effect[2])
        elif kind == "set":
            setattr(joueur, effect[1], effect[2])
        else:
            raise ValueError(f"Effet de scène inconnu : {kind}")