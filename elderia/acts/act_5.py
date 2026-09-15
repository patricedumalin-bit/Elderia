from elderia.content.act_5_choices import ACT_5_CHOICES
from elderia.content.act_5_scenes import ACT_5_SCENE_TEXTS
from elderia.core import story_state
from elderia.core.combat import lancer_combat
from elderia.core.codex import ajouter_souvenir, decouvrir_codex
from elderia.core.ending_variants import normaliser_trait, texte_variantes_fin
from elderia.core.gameplay import interaction_compagnons, interjection_compagnon, ravitaillement, repos_de_camp
from elderia.core.io import demander_choix, illustrer, raconter
from elderia.core.meta_progression import actualiser_meta_progression, actualiser_reves_dynamiques
from elderia.core.narrative_state import afficher_bilan_acte, bilan_narratif, signature_classe_finale
from elderia.core.systems import tester_stat
from elderia.core.tome import XP_TOME_2, chapitre_final_tome_2, valider_quete
from elderia.core.runtime import charger_ou_preparer, sauvegarder_fin_acte
from elderia.content.act_5_outcomes import ACT_5_OUTCOMES
from elderia.core.scene_engine import afficher_options, choisir, consequence, dire, fin_prematuree, journal, resonance_temporelle, reve, secret, transition


def scene_28_fracture_du_temps(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28_fracture_du_temps'])
    joueur.tension_fragment += 2
    actualiser_reves_dynamiques(joueur)
    reve(joueur, ACT_5_OUTCOMES, 'scene_28_fracture_du_temps_dream_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28_fracture_du_temps_journal_1')


def scene_28a_dernier_camp(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28a_dernier_camp'])
    if story_state.garrick_est_sauve(joueur):
        dire(ACT_5_OUTCOMES, 'story_state_garrick_response_1')
    if joueur.variables.get("commandement_efficace") or joueur.variables.get("commandement_compatissant") or joueur.variables.get("commandement_equilibre"):
        dire(ACT_5_OUTCOMES, 'story_state_commandement_response_1')
    if tester_stat(joueur, "charisme", 16):
        joueur.reputation += 1
        raconter("Votre présence rassure le camp plus que vous ne l'auriez cru.")
    choix = choisir(ACT_5_CHOICES, 'scene_28a_dernier_camp', "Dernier camp > ")

    if choix == 0:
        joueur.reputation += 1
        dire(ACT_5_OUTCOMES, 'scene_28a_dernier_camp_response_1')
    else:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 5
        dire(ACT_5_OUTCOMES, 'scene_28a_dernier_camp_response_2')
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_28a_dernier_camp_response_3')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28a_dernier_camp_journal_1')


def scene_28b_voix_des_compagnons(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28b_voix_des_compagnons'])
    dialogue = interaction_compagnons(joueur)
    if dialogue:
        raconter(dialogue)
    if joueur.variables.get("lyra_garde_fou") or joueur.variables.get("compagnons_garde_fou"):
        dire(ACT_5_OUTCOMES, 'story_state_lyra_garde_fou_response_1')
    choix = choisir(ACT_5_CHOICES, 'scene_28b_voix_des_compagnons', "Voix des compagnons > ")

    if choix == 0:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        dire(ACT_5_OUTCOMES, 'scene_28b_voix_des_compagnons_response_1')
    elif choix == 1:
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        joueur.variables["lyra_garde_fou"] = True
        dire(ACT_5_OUTCOMES, 'scene_28b_voix_des_compagnons_response_2')
    else:
        joueur.variables["serment_final_compagnons"] = True
        joueur.reputation += 1
        dire(ACT_5_OUTCOMES, 'scene_28b_voix_des_compagnons_response_3')
    consequence(joueur, ACT_5_OUTCOMES, 'scene_28b_voix_des_compagnons_consequence_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28b_voix_des_compagnons_journal_1')


def scene_28c_portes_du_sceau(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28c_portes_du_sceau'])
    choix = choisir(ACT_5_CHOICES, 'scene_28c_portes_du_sceau', "Portes du Sceau > ")

    if choix == 0:
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_response_1')
    elif choix == 1:
        joueur.connaissance_temporelle += 1
        secret(joueur, ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_secret_1')
        dire(ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_response_2')
    elif choix == 2:
        joueur.tension_fragment += 2
        joueur.fragments_temps = min(25, joueur.fragments_temps + 1)
        dire(ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_response_3')
    else:
        joueur.reputation -= 1
        joueur.tension_fragment += 1
        joueur.variables["portes_forcees_par_larmee"] = True
        dire(ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_response_4')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28c_portes_du_sceau_journal_1')


def scene_28d_tribunal_des_cristaux(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28d_tribunal_des_cristaux'])
    raconter(signature_classe_finale(joueur))
    traits = {normaliser_trait(trait) for trait in joueur.traits_route}
    if normaliser_trait("Silence de Brumebois") in traits:
        raconter("Le Tribunal vous montre aussi le silence gardé autour de la flamme bleue. Certains secrets ont protégé le village ; d'autres ont seulement retardé la peur.")
    if normaliser_trait("Lecteur des cendres") in traits:
        raconter("Les ordres brûlés reviennent dans la lumière des Cristaux, preuve que même les fragments sauvés au milieu de l'incendie peuvent peser sur le dernier jugement.")
    choix = choisir(ACT_5_CHOICES, 'scene_28d_tribunal_des_cristaux', "Tribunal des Cristaux > ")

    if choix == 0:
        joueur.alignement += 1
        dire(ACT_5_OUTCOMES, 'scene_28d_tribunal_des_cristaux_response_1')
    else:
        joueur.alignement -= 1
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_28d_tribunal_des_cristaux_response_2')
        joueur.variables["compagnons_dans_vision_finale"] = True
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_5_OUTCOMES, 'scene_28d_tribunal_des_cristaux_response_3')
    consequence(joueur, ACT_5_OUTCOMES, 'scene_28d_tribunal_des_cristaux_consequence_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28d_tribunal_des_cristaux_journal_1')


def scene_28e_ombre_derriere_le_temps(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_28e_ombre_derriere_le_temps'])
    decouvrir_codex(joueur, "devoreur")
    choix = choisir(ACT_5_CHOICES, 'scene_28e_ombre_derriere_le_temps', "Ombre derrière le Temps > ")

    if choix == 0:
        joueur.reputation += 1
        dire(ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_response_1')
    elif choix == 1:
        joueur.connaissance_temporelle += 1
        dire(ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_response_2')
    elif choix == 2:
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_response_3')
    else:
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        joueur.variables["refus_de_savoir_devoreur"] = True
        dire(ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_response_4')
    joueur.variables["secret_de_voreur"] = True
    secret(joueur, ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_secret_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_28e_ombre_derriere_le_temps_journal_1')


def scene_28f_manifestation_du_devoreur(joueur):
    raconter("\nAvant Malakar, quelque chose passe sa main à travers la fracture. Ce n'est pas encore le Dévoreur des Âges, seulement une manifestation de sa faim : assez réelle pour saigner, assez ancienne pour faire trembler les Cristaux.")
    victoire = lancer_combat(joueur, {
        "nom": "Manifestation du Dévoreur",
        "pv": 115,
        "force": 20,
        "agilite": 8,
        "armure": 10,
        "arme": 9,
        "xp": 420,
        "or": 0,
    })
    if victoire:
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment += 1
    return victoire


def scene_29_malakar(joueur):
    illustrer("assets/images/backgrounds/S01_master_key.png")
    raconter(ACT_5_SCENE_TEXTS['scene_29_malakar'])

    # [NARRATIF] Résonance ultime
    resonance_temporelle(joueur, "Un monde figé dans un instant de glace et de feu, pour l'éternité.", seuil=5)

    traits = {normaliser_trait(trait) for trait in joueur.traits_route}
    if normaliser_trait("Auditeur de Morvayn") in traits:
        raconter("Vous avez assez écouté Morvayn pour reconnaître la faille dans la voix de Malakar : ce n'est pas la vérité qui lui manque, mais le courage de la laisser survivre à son empire.")
    if normaliser_trait("Courage devant Morvayn") in traits:
        raconter("Le courage montré face au masque de Morvayn ne vous donne pas de certitude, mais il vous empêche de confondre la peur de Malakar avec une autorité naturelle.")
    if story_state.connait_assez_malakar(joueur):
        dire(ACT_5_OUTCOMES, 'story_state_malakar_secret_response_1')
    if story_state.morvayn_est_recrute(joueur):
        dire(ACT_5_OUTCOMES, 'story_state_morvayn_recrute_response_1')
    elif story_state.morvayn_est_epargne(joueur):
        dire(ACT_5_OUTCOMES, 'story_state_morvayn_epargne_response_1')
    elif story_state.morvayn_est_tue(joueur):
        dire(ACT_5_OUTCOMES, 'story_state_morvayn_tue_response_1')
    if joueur.respect_morvayn >= 6:
        joueur.alignement += 1
        raconter("Le respect que Morvayn vous porte depuis vos premières rencontres pèse sur cette confrontation : il choisit, une dernière fois, de vous faire confiance plutôt que de trancher.")
    choix = choisir(ACT_5_CHOICES, 'scene_29_malakar', "Face à Malakar > ")

    if choix == 0:
        joueur.alignement += 1
        consequence(joueur, ACT_5_OUTCOMES, 'scene_29_malakar_consequence_1')
    elif choix == 1:
        secret(joueur, ACT_5_OUTCOMES, 'scene_29_malakar_secret_1')
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_29_malakar_response_1')
    else:
        joueur.alignement -= 1
        secret(joueur, ACT_5_OUTCOMES, 'scene_29_malakar_secret_2')
        consequence(joueur, ACT_5_OUTCOMES, 'scene_29_malakar_consequence_2')


def scene_29m_morvayn_exclusif(joueur):
    if story_state.morvayn_est_recrute(joueur):
        raconter(ACT_5_SCENE_TEXTS['scene_29m_morvayn_recrute'])
        joueur.connaissance_temporelle += 1
        joueur.variables["morvayn_affronte_malakar"] = True
        if "Kael" in joueur.compagnons:
            raconter("Kael observe Morvayn rejoindre vos rangs sans un mot, mais sa main reste un instant de trop près de sa lame.")
        journal(joueur, ACT_5_OUTCOMES, 'scene_29m_morvayn_recrute_journal_1')
    elif story_state.morvayn_est_epargne(joueur):
        raconter(ACT_5_SCENE_TEXTS['scene_29m_morvayn_epargne'])
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        joueur.variables["morvayn_hesite_final"] = True
        if "Lyra" in joueur.compagnons:
            raconter("Lyra regarde Morvayn s'éloigner, libre. \"On m'avait confié la même mission que la sienne, autrefois\", dit-elle enfin. \"Je suis contente qu'il ait eu le choix que je n'étais pas sûre d'avoir.\"")
        journal(joueur, ACT_5_OUTCOMES, 'scene_29m_morvayn_epargne_journal_1')
    elif story_state.morvayn_est_tue(joueur):
        raconter(ACT_5_SCENE_TEXTS['scene_29m_morvayn_tue'])
        joueur.alignement += 1
        joueur.variables["absence_morvayn_finale"] = True
        if "Kael" in joueur.compagnons:
            raconter("Kael ne dit rien devant l'absence de Morvayn, mais il resserre sa prise sur son arme — rappel silencieux de ce qui attend ceux qui échouent leur mission.")
        journal(joueur, ACT_5_OUTCOMES, 'scene_29m_morvayn_tue_journal_1')


def scene_29a_avatar_de_malakar(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_29a_avatar_de_malakar'])
    victoire = lancer_combat(joueur, {
        "nom": "Avatar de Malakar",
        "pv": 140,
        "force": 23,
        "agilite": 10,
        "armure": 11,
        "arme": 10,
        "xp": XP_TOME_2["Avatar de Malakar"],
        "or": 0,
    })
    if victoire:
        journal(joueur, ACT_5_OUTCOMES, 'scene_29a_avatar_de_malakar_journal_1')
    return victoire


def scene_29b_chambre_du_sceau(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_29b_chambre_du_sceau'])
    choix = choisir(ACT_5_CHOICES, 'scene_29b_chambre_du_sceau', "Chambre du Sceau > ")

    if choix == 0:
        joueur.alignement += 1
        joueur.variables["malakar_acheve"] = True
        dire(ACT_5_OUTCOMES, 'scene_29b_chambre_du_sceau_response_1')
    elif choix == 1:
        joueur.connaissance_temporelle += 1
        joueur.variables["malakar_transmet_savoir"] = True
        dire(ACT_5_OUTCOMES, 'scene_29b_chambre_du_sceau_response_2')
    elif choix == 2:
        joueur.alignement -= 1
        joueur.variables["malakar_temoin_final"] = True
        dire(ACT_5_OUTCOMES, 'scene_29b_chambre_du_sceau_response_3')
    else:
        fin_prematuree(joueur, ACT_5_OUTCOMES, 'ending_premature_geolier_maintenu', "Fin du Geôlier Maintenu")
        return
    consequence(joueur, ACT_5_OUTCOMES, 'scene_29b_chambre_du_sceau_consequence_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_29b_chambre_du_sceau_journal_1')


def scene_29c_dernieres_voix(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_29c_dernieres_voix'])
    ajouter_souvenir(joueur, "voix_finales")
    choix = choisir(ACT_5_CHOICES, 'scene_29c_dernieres_voix', "Dernières voix > ")

    if choix == 0:
        joueur.alignement += 1
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_5_OUTCOMES, 'scene_29c_dernieres_voix_response_1')
    elif choix == 1:
        joueur.connaissance_temporelle += 1
        dire(ACT_5_OUTCOMES, 'scene_29c_dernieres_voix_response_2')
    else:
        joueur.variables["choix_final_solitaire"] = True
        joueur.tension_fragment += 1
        dire(ACT_5_OUTCOMES, 'scene_29c_dernieres_voix_response_3')
    journal(joueur, ACT_5_OUTCOMES, 'scene_29c_dernieres_voix_journal_1')


def peut_devenir_tyran(joueur):
    if joueur.variables.get("renonce_tyrannie", False):
        return False
    return (
        joueur.alignement <= -2
        or joueur.variables.get("cristaux_utilises_dangereusement", False)
        or joueur.variables.get("poids_solitaire_cristaux", False)
        or joueur.variables.get("commandement_efficace", False)
        or joueur.variables.get("choix_final_solitaire", False)
    )


def peut_restaurer_temps(joueur):
    connait_la_prison = joueur.variables.get("secret_de_voreur", False)
    possede_les_cristaux = len(joueur.cristaux) >= 2
    connait_malakar = joueur.variables.get("malakar_transmet_savoir", False) or joueur.variables.get("secret_malakar", 0) >= 2
    comprend_le_temps = joueur.connaissance_temporelle >= 4
    garde_fou_humain = (
        joueur.variables.get("lyra_garde_fou", False)
        or joueur.variables.get("compagnons_garde_fou", False)
        or joueur.variables.get("serment_final_compagnons", False)
        or joueur.variables.get("compagnons_dans_vision_finale", False)
    )
    return connait_la_prison and possede_les_cristaux and connait_malakar and comprend_le_temps and garde_fou_humain


def scene_29d_lyra_garde_fou(joueur):
    if not peut_devenir_tyran(joueur):
        return
    if not (joueur.variables.get("lyra_garde_fou", False) or joueur.variables.get("compagnons_garde_fou", False)):
        return
    raconter(ACT_5_SCENE_TEXTS['scene_29d_lyra_garde_fou'])
    choix = choisir(ACT_5_CHOICES, 'scene_29d_lyra_garde_fou', "Garde-fou de Lyra > ")

    if choix == 0:
        joueur.variables["renonce_tyrannie"] = True
        joueur.alignement += 1
        joueur.tension_fragment = max(0, joueur.tension_fragment - 2)
        dire(ACT_5_OUTCOMES, 'scene_29d_lyra_garde_fou_response_1')
    else:
        joueur.variables["choisit_tyrannie_malgre_lyra"] = True
        joueur.alignement -= 1
        dire(ACT_5_OUTCOMES, 'scene_29d_lyra_garde_fou_response_2')
    consequence(joueur, ACT_5_OUTCOMES, 'scene_29d_lyra_garde_fou_consequence_1')
    journal(joueur, ACT_5_OUTCOMES, 'scene_29d_lyra_garde_fou_journal_1')


def fins_disponibles(joueur):
    fins = [
        ("Fin du Sacrifice", "Se sacrifier pour refermer le Sceau", 'ending_fin_du_sacrifice'),
        ("Fin du Roi", "Unifier le continent sous votre autorité", 'ending_fin_du_roi'),
        ("Fin du Héros", "Détruire les Cristaux pour libérer le monde de leur dette", 'ending_fin_du_heros'),
    ]
    if len(joueur.cristaux) >= 2:
        fins.append(("Fin du Gardien", "Devenir le Gardien des Cristaux", 'ending_fin_du_gardien'))
    if peut_devenir_tyran(joueur):
        fins.append(("Fin du Tyran", "Prendre le Sceau et imposer votre propre ordre", 'ending_fin_du_tyran'))
    if peut_restaurer_temps(joueur):
        fins.append(("Fin Secrète", "Tenter de restaurer totalement le Temps", 'ending_fin_secrete'))
    return fins


def scene_30_choix_final(joueur):
    raconter(ACT_5_SCENE_TEXTS['scene_30_choix_final'])
    raconter(bilan_narratif(joueur))
    fins = fins_disponibles(joueur)
    options = [option for _, option, _ in fins]
    afficher_options(options)
    choix = demander_choix("Dernier choix > ", options)

    joueur.fin_majeure = fins[choix][0]
    joueur.enregistrer_fin_atteinte()
    actualiser_meta_progression(joueur)
    dire(ACT_5_OUTCOMES, fins[choix][2])
    variantes = texte_variantes_fin(joueur)
    if variantes:
        raconter(variantes)
    journal(joueur, ACT_5_OUTCOMES, 'scene_30_choix_final_journal_1')
    joueur.acte_courant = "Épilogue"
    valider_quete(joueur, "Conclure le Dernier Âge")
    joueur.journal.append(f"Épilogue : {joueur.fin_majeure}.")


def jouer_acte_5(joueur):
    scene_28_fracture_du_temps(joueur)
    transition(ACT_5_OUTCOMES, 'transition_28_to_28a')
    scene_28a_dernier_camp(joueur)
    repos_de_camp(joueur, "Dernier camp")
    ravitaillement(joueur, "Dernier camp")
    transition(ACT_5_OUTCOMES, 'transition_28a_to_28b')
    scene_28b_voix_des_compagnons(joueur)
    transition(ACT_5_OUTCOMES, 'transition_28b_to_28c')
    scene_28c_portes_du_sceau(joueur)
    transition(ACT_5_OUTCOMES, 'transition_28c_to_28d')
    scene_28d_tribunal_des_cristaux(joueur)
    transition(ACT_5_OUTCOMES, 'transition_28d_to_28e')
    scene_28e_ombre_derriere_le_temps(joueur)
    if not scene_28f_manifestation_du_devoreur(joueur):
        return
    transition(ACT_5_OUTCOMES, 'transition_28e_to_29')
    scene_29_malakar(joueur)
    scene_29m_morvayn_exclusif(joueur)
    transition(ACT_5_OUTCOMES, 'transition_29_to_29a')
    if not scene_29a_avatar_de_malakar(joueur):
        return
    transition(ACT_5_OUTCOMES, 'transition_29a_to_29b')
    scene_29b_chambre_du_sceau(joueur)
    if joueur.acte_courant == "Épilogue":
        return
    transition(ACT_5_OUTCOMES, 'transition_29b_to_29c')
    scene_29c_dernieres_voix(joueur)
    scene_29d_lyra_garde_fou(joueur)
    transition(ACT_5_OUTCOMES, 'transition_29c_to_30')
    scene_30_choix_final(joueur)


def jouer(joueur=None, sauvegarder=True):
    if joueur is None:
        joueur = charger_ou_preparer(5)
    joueur.acte_courant = "Acte V - Le Dernier Âge"
    if joueur.pv > 0:
        jouer_acte_5(joueur)
    if joueur.acte_courant == "Épilogue":
        afficher_bilan_acte(joueur, "ACTE V - LE DERNIER ÂGE")
    chapitre_final_tome_2(joueur)
    if sauvegarder and joueur.pv > 0:
        sauvegarder_fin_acte(joueur)
    return joueur
