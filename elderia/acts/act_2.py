from elderia.content.act_2_choices import ACT_2_CHOICES
from elderia.content.act_2_scenes import ACT_2_SCENE_TEXTS
from elderia.core import story_state
from elderia.core.combat import creer_ennemi, lancer_combat, lancer_combat_vague
from elderia.core.codex import ajouter_souvenir, decouvrir_codex
from elderia.core.gameplay import interjection_compagnon, ravitaillement, repos_de_camp
from elderia.core.io import demander_choix, illustrer, raconter
from elderia.core.narrative_state import afficher_bilan_acte, ajouter_trait_route
from elderia.core.save import sauvegarder as sauvegarder_partie
from elderia.core.scene_engine import item, afficher_options, choisir, consequence, dire, journal, murmure_corruption, porte_fermee, quete, recruter, resonance_temporelle, retry_scene, reve, secret, transition
from elderia.core.systems import MARCHAND_STOCK_ACTE_2, ecran_game_over, recruter_compagnon, tester_stat, visiter_marchand
from elderia.core.procedural import lancer_evenement_aleatoire
from elderia.data.tables import XP_ENNEMIS
from elderia.content.act_2_outcomes import ACT_2_OUTCOMES

sauvegarder = sauvegarder_partie

def scene_13_arrivee_aldorath(joueur):
    illustrer("assets/images/backgrounds/S02_main_menu.png") # Placeholder pour cité
    raconter(ACT_2_SCENE_TEXTS['scene_13_arrivee_aldorath'])

    # [NARRATIF] Interjection
    interjection_compagnon(joueur, "Lyra", "Aldorath... les pierres ici ont oublié le goût du vent des forêts.")

    decouvrir_codex(joueur, "aldorath")
    a_le_medaillon = "Médaillon Royal" in joueur.inventaire
    options = []
    if a_le_medaillon:
        options.append("Montrer le médaillon royal aux gardes")
    options.append("Entrer discrètement avec Lyra")
    options.append("Passer par les égouts sous les murailles")
    afficher_options(options)
    choix_nom = options[demander_choix("Aux portes d'Aldorath > ", options)]

    if choix_nom == "Montrer le médaillon royal aux gardes":
        joueur.modifier_faction("Aldor", 10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_consequence_1')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_response_1')
    elif choix_nom == "Entrer discrètement avec Lyra":
        joueur.modifier_faction("Cités Libres", 5)
        joueur.modifier_faction("Aldor", -5)
        joueur.reputation_criminelle += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_consequence_3')
        if joueur.reputation >= 2:
            dire(ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_response_3')
        else:
            dire(ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_response_4')
    else:
        joueur.modifier_faction("Cités Libres", 5)
        item(joueur, "Bague de cuivre ancienne")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_consequence_4')
        dire(ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_response_2')
        if tester_stat(joueur, "agilite", 11):
            joueur.ajouter_xp(50)
            raconter("Vous traversez les égouts sans transformer chaque bruit dans l'eau noire en combat inutile.")
        else:
            joueur.pv = max(1, joueur.pv - 4)
            raconter("Les égouts vous coûtent du sang et une ration trempée, mais vous atteignez la ville sans alerter la garde.")

    quete(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_13_arrivee_aldorath_journal_1')

def scene_13d_fille_aux_corbeaux(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_13d_fille_aux_corbeaux'])
    choix = choisir(ACT_2_CHOICES, 'scene_13d_fille_aux_corbeaux', "Mira aux Corbeaux > ")

    sujets = [
        "Parler de Garrick immédiatement",
        "Proposer un marché honnête",
        "Tester sa loyauté envers la Basse-Ville",
    ]
    for index, sujet in enumerate(sujets, 1):
        print(f"{index}. {sujet}")
    sujet = demander_choix("Que lui dites-vous ensuite ? ", sujets)

    if choix == 0:
        recruter(joueur, "Mira aux Corbeaux")
        joueur.loyautes["Mira aux Corbeaux"] += 15 if sujet == 1 else 10
        joueur.modifier_faction("Cités Libres", 10)
        item(joueur, "Carte du marché noir")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_consequence_1')
        secret(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_secret_1')
        if sujet == 0:
            quete(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_quest_1')
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_1')
        elif sujet == 1:
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_3')
        else:
            joueur.modifier_faction("Cités Libres", 5)
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_4')
    elif choix == 1:
        if tester_stat(joueur, "charisme", 13) or tester_stat(joueur, "force", 13):
            secret(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_secret_2')
            quete(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_quest_2')
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_5')
        else:
            consequence(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_consequence_4')
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_6')
        joueur.loyautes["Mira aux Corbeaux"] -= 10 if sujet == 0 else 20
        joueur.modifier_faction("Cités Libres", -5)
    else:
        joueur.modifier_faction("Aldor", 5)
        joueur.modifier_faction("Cités Libres", -15)
        joueur.or_poches += 100
        joueur.loyautes["Mira aux Corbeaux"] = -100
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_consequence_2')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_consequence_3')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_locked_path_1')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_locked_path_2')
        if sujet == 2:
            consequence(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_consequence_5')
            dire(ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_response_2')
    journal(joueur, ACT_2_OUTCOMES, 'scene_13d_fille_aux_corbeaux_journal_1')


def scene_13e_taverne_dragon_gris(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_13e_taverne_dragon_gris'])
    if joueur.a_consequence("Marek vous respecte") or joueur.a_consequence("Marek respecte votre courage"):
        dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_1')
    elif joueur.a_consequence("Marek se souviendra") or joueur.a_consequence("dette joyeuse"):
        dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_2')
    choix = choisir(ACT_2_CHOICES, 'scene_13e_taverne_dragon_gris', "Dragon Gris > ")

    if choix == 0:
        if joueur.or_poches >= 10:
            joueur.or_poches -= 10
            consequence(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_consequence_1')
            dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_3')
        else:
            dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_4')
    elif choix == 1:
        joueur.variables["transfert_nord_connu"] = True
        ajouter_trait_route(joueur, "Piste du nord")
        secret(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_secret_1')
        quete(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_quest_1')
        dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_5')
    elif choix == 2:
        joueur.reputation += 1
        quete(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_quest_2')
        secret(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_secret_2')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_6')
    else:
        if tester_stat(joueur, "force", 13):
            joueur.reputation += 1
            item(joueur, "Faveur du Dragon Gris")
            consequence(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_consequence_3')
            dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_7')
        else:
            joueur.pv = max(1, joueur.pv - 4)
            dire(ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_response_8')

    journal(joueur, ACT_2_OUTCOMES, 'scene_13e_taverne_dragon_gris_journal_1')


def scene_13a_quartiers_aldorath(joueur):
    dire(ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_response_1')
    options = [
        "Explorer le Port Fluvial et ses rumeurs",
        "Aller au Temple de l'Aube où les disparus sont nommés",
        "Descendre dans la Basse Ville parmi les réfugiés",
    ]
    afficher_options(options)
    choix = demander_choix("Quel quartier découvrez-vous ? ", options)

    if choix == 0:
        joueur.quartiers_visites.append("Port Fluvial")
        joueur.modifier_faction("Ligue de Varken", 5)
        secret(joueur, ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_secret_1')
        dire(ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_response_2')
    elif choix == 1:
        joueur.quartiers_visites.append("Temple de l'Aube")
        quete(joueur, ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_quest_1')
        joueur.modifier_faction("Aldor", 5)
        dire(ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_response_3')
    else:
        joueur.quartiers_visites.append("Basse Ville")
        joueur.modifier_faction("Cités Libres", 5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_response_4')

    journal(joueur, ACT_2_OUTCOMES, 'scene_13a_quartiers_aldorath_journal_1')

def scene_13b_disparus_aldorath(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_13a_quartiers_aldorath'])
    choix = choisir(ACT_2_CHOICES, 'scene_13a_quartiers_aldorath', "Les Disparus > ")

    if choix == 0:
        joueur.tension_fragment += 2
        reve(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_dream_1')
        dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_1')
        difficulte = 15 if joueur.tension_fragment < 5 else 17
        if tester_stat(joueur, "volonte", difficulte) or tester_stat(joueur, "intelligence", difficulte):
            joueur.ajouter_xp(XP_ENNEMIS["Rafleur temporel"])
            item(joueur, "Fragment Temporel Mineur")
            secret(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_secret_1')
            dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_2')
        else:
            joueur.tension_fragment += 1
            joueur.pv = max(1, joueur.pv - 6)
            dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_5')
    elif choix == 1:
        if tester_stat(joueur, "intelligence", 15):
            joueur.connaissance_temporelle += 1
            secret(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_secret_2')
            joueur.ajouter_xp(500)
            dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_4')
        else:
            joueur.tension_fragment += 1
            dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_5')
    else:
        joueur.modifier_faction("Aldor", 10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_response_3')

    quete(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_13b_disparus_aldorath_journal_1')
def scene_13c_oeil_aeternis(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_13b_disparus_aldorath'])
    choix = choisir(ACT_2_CHOICES, 'scene_13b_disparus_aldorath', "L'Œil d'Aeternis > ")

    if choix == 0:
        joueur.artefacts.append("Œil d'Aeternis")
        joueur.pm = max(0, joueur.pm - 2)
        joueur.tension_fragment += 1
        joueur.modifier_faction("Aldor", 5)
        secret(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_secret_1')
        dire(ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_response_1')
    elif choix == 1:
        joueur.modifier_faction("Aldor", 10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_response_2')
    else:
        joueur.artefacts.append("Œil d'Aeternis")
        joueur.pm = max(0, joueur.pm - 2)
        joueur.tension_fragment += 2
        joueur.modifier_faction("Aldor", -10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_consequence_2')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_locked_path_1')
        dire(ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_response_3')

    if "Œil d'Aeternis" in joueur.artefacts:
        quete(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_quest_1')
    else:
        joueur.quetes["Obtenir l'Œil d'Aeternis"] = False
    journal(joueur, ACT_2_OUTCOMES, 'scene_13c_oeil_aeternis_journal_1')


def scene_14_conseil_royal(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_14_conseil_royal'])
    if story_state.est_recherche_par_aldor(joueur):
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_2_OUTCOMES, 'story_state_aldor_criminal_consequence_1')
        dire(ACT_2_OUTCOMES, 'story_state_aldor_criminal_response_1')
    if tester_stat(joueur, "charisme", 14):
        joueur.modifier_faction("Aldor", 5)
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_1')
    else:
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_2')
    choix = choisir(ACT_2_CHOICES, 'scene_14_conseil_royal', "Devant le Conseil > ")

    demandes = list(ACT_2_CHOICES['scene_14_conseil_royal']['demandes'])
    for index, demande in enumerate(demandes, 1):
        print(f"{index}. {demande}")
    demande = demander_choix("Votre exigence > ", demandes)

    if choix == 0:
        joueur.modifier_faction("Aldor", 15)
        joueur.influences["Militaire"] += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_3')
    elif choix == 1:
        joueur.modifier_faction("Aldor", 5)
        joueur.influences["Religieuse"] += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_5')
    else:
        joueur.modifier_faction("Aldor", 5)
        joueur.influences["Politique"] += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_4')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_6')

    if demande == 0:
        quete(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_quest_1')
        joueur.variables["garrick_recherche"] = True
        joueur.modifier_faction("Aldor", 5)
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_4')
    elif demande == 1:
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_5')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_locked_path_1')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_7')
    else:
        joueur.modifier_faction("Aldor", -5)
        joueur.modifier_faction("Cités Libres", 5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_consequence_6')
        dire(ACT_2_OUTCOMES, 'scene_14_conseil_royal_response_8')

    journal(joueur, ACT_2_OUTCOMES, 'scene_14_conseil_royal_journal_1')


def scene_14c_archives_aldor(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_14c_archives_aldor'])
    if tester_stat(joueur, "intelligence", 15):
        secret(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_secret_1')
        secret(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_secret_2')
        quete(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_quest_1')
        dire(ACT_2_OUTCOMES, 'scene_14c_archives_aldor_response_1')
    else:
        joueur.tension_fragment += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_14c_archives_aldor_response_2')

    choix = choisir(ACT_2_CHOICES, 'scene_14c_archives_aldor', "Archives d'Aldor > ")

    if choix == 0:
        joueur.ajouter_xp(500)
        joueur.talents.append("Chercheur : +10 % connaissances historiques")
        dire(ACT_2_OUTCOMES, 'scene_14c_archives_aldor_response_3')
    elif choix == 1:
        joueur.loyautes["Lyra"] += 10
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_14c_archives_aldor_response_4')
    else:
        joueur.variables["archives_cachees_aux_compagnons"] = True
        ajouter_trait_route(joueur, "Gardien de secrets")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_14c_archives_aldor_response_5')

    journal(joueur, ACT_2_OUTCOMES, 'scene_14c_archives_aldor_journal_1')


def scene_14b_fragments_du_mensonge(joueur):
    dire(ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_response_1')
    choix = choisir(ACT_2_CHOICES, 'scene_14b_fragments_du_mensonge', "Fragments du Mensonge > ")

    if choix == 0:
        joueur.modifier_faction("Aldor", 5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_response_2')
    elif choix == 1:
        joueur.modifier_faction("Ellorien", 5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_response_3')
    else:
        joueur.modifier_faction("Ligue de Varken", -10)
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_response_4')

    quete(joueur, ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_14b_fragments_du_mensonge_journal_1')


def scene_15_marche_varken(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_15_marche_varken'])
    prix_registre = 10 if joueur.a_consequence("Mira aux Corbeaux vous doit") else 15
    if "Port Fluvial" in joueur.quartiers_visites:
        prix_registre = max(5, prix_registre - 3)
        raconter("Vos repères pris au Port Fluvial vous font reconnaître deux visages autour de l'étal d'Ysilde : le prix en devient plus négociable.")
    options = [
        f"Payer Ysilde pour le registre ({prix_registre} or)",
        "La convaincre que Garrick vaut plus vivant que vendu",
        "Voler la page pendant que Lyra détourne l'attention",
    ]
    afficher_options(options)
    choix = demander_choix("Marché de Varken > ", options)

    if choix == 0 and joueur.or_poches >= prix_registre:
        joueur.or_poches -= prix_registre
        joueur.modifier_faction("Ligue de Varken", 10)
        item(joueur, "Registre gratté de Varken")
        if prix_registre < 15:
            dire(ACT_2_OUTCOMES, 'scene_15_marche_varken_response_1')
        else:
            dire(ACT_2_OUTCOMES, 'scene_15_marche_varken_response_2')
    elif choix == 1:
        if tester_stat(joueur, "charisme", 14):
            joueur.modifier_faction("Ligue de Varken", 10)
            item(joueur, "Registre gratté de Varken")
            dire(ACT_2_OUTCOMES, 'scene_15_marche_varken_response_4')
        else:
            joueur.modifier_faction("Ligue de Varken", -5)
            dire(ACT_2_OUTCOMES, 'scene_15_marche_varken_response_5')
    else:
        joueur.modifier_faction("Ligue de Varken", -10)
        joueur.modifier_faction("Ellorien", -5)
        item(joueur, "Page volée de Varken")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_15_marche_varken_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_15_marche_varken_response_3')

    quete(joueur, ACT_2_OUTCOMES, 'scene_15_marche_varken_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_15_marche_varken_journal_1')

def scene_15b_lettre_cachee(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_15b_lettre_cachee'])
    if any("trouvé dans la neige" in secret for secret in joueur.secrets):
        dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_2')
        if any("prépare votre départ depuis des années" in secret for secret in joueur.secrets):
            dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_4')
        secret(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_secret_1')
    quete(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_quest_1')
    item(joueur, "Médaillon des Veilleurs")
    joueur.volonte += 5
    joueur.energie_max = joueur.calculer_energie_max()
    joueur.energie = min(joueur.energie_max, joueur.energie + 5)
    consequence(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_consequence_1')
    choix = choisir(ACT_2_CHOICES, 'scene_15b_lettre_cachee', "Lettres de Garrick > ")

    if choix == 0:
        joueur.loyautes["Lyra"] += 10
        consequence(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_3')
    elif choix == 1:
        joueur.variables["lettres_garrick_detruites"] = True
        ajouter_trait_route(joueur, "Brûleur de secrets")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_5')
    else:
        joueur.variables["lettres_garrick_cachees"] = True
        ajouter_trait_route(joueur, "Gardien des lettres")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_consequence_4')
        dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_6')
    dire(ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_response_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_15b_lettre_cachee_journal_1')

def scene_16_prison_des_cendres(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16_prison_des_cendres'])
    choix = choisir(ACT_2_CHOICES, 'scene_16_prison_des_cendres', "Prison des Cendres > ")

    objectifs = list(ACT_2_CHOICES['scene_16_prison_des_cendres']['objectifs'])
    for index, objectif in enumerate(objectifs, 1):
        print(f"{index}. {objectif}")
    objectif = demander_choix("Priorité dans le donjon > ", objectifs)

    if choix == 0:
        joueur.variables["morvayn_alerte"] = True
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_response_1')
        victoire = lancer_combat_vague(joueur, [creer_ennemi("Garde Cendreux") for _ in range(4)])
        if victoire:
            item(joueur, "Clé des geôles")
            if objectif == 1:
                joueur.reputation += 1
                consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_3')
    elif choix == 1:
        if tester_stat(joueur, "agilite", 15):
            joueur.reputation_criminelle += 5
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_4')
            dire(ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_response_2')
            victoire = True
            if objectif == 2:
                item(joueur, "Plan des Archives Interdites")
                consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_5')
        else:
            joueur.reputation_criminelle += 2
            dire(ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_response_3')
            victoire = lancer_combat_vague(joueur, [
                creer_ennemi("Garde Cendreux", pv=32, force=9, armure=4, xp=80, **{"or": 2})
                for _ in range(2)
            ])
    else:
        if tester_stat(joueur, "charisme", 17):
            secret(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_secret_1')
            joueur.variables["garrick_localise"] = True
            dire(ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_response_4')
            victoire = True
            if objectif == 0:
                quete(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_quest_2')
                consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_6')
        else:
            joueur.variables["morvayn_alerte"] = True
            dire(ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_response_5')
            victoire = lancer_combat(joueur, creer_ennemi("Garde Cendreux"))
    if victoire:
        quete(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_quest_1')
        joueur.variables["garrick_recherche"] = True
        if objectif == 2:
            joueur.variables["secret_arthen"] += 1
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_consequence_2')
        journal(joueur, ACT_2_OUTCOMES, 'scene_16_prison_des_cendres_journal_1')
    return victoire


def scene_16a_cellules_abandonnees(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16a_cellules_abandonnees'])
    choix = choisir(ACT_2_CHOICES, 'scene_16a_cellules_abandonnees', "Cellules abandonnées > ")

    if choix == 0:
        recruter(joueur, "Elara")
        joueur.loyautes["Elara"] += 20
        joueur.variables["elara_sauvee"] = True
        joueur.intelligence += 5
        joueur.actualiser_mana_max()
        dire(ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_response_1')
    else:
        joueur.variables["elara_abandonnee"] = True
        ajouter_trait_route(joueur, "Savoir abandonné")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_response_3')
        secret(joueur, ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_secret_1')
        joueur.variables["secret_arthen"] += 1
        dire(ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_response_4')

    victoire = lancer_combat(joueur, {
        "nom": "Spectre Enchaîné",
        "pv": 60,
        "force": 12,
        "agilite": 4,
        "armure": 3,
        "arme": 6,
        "xp": 250,
        "or": 0,
    })
    if victoire:
        item(joueur, "Pierre Spectrale")
        joueur.agilite = max(1, joueur.agilite - 2)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_response_2')
    journal(joueur, ACT_2_OUTCOMES, 'scene_16a_cellules_abandonnees_journal_1')

def scene_16b_borin_prisonnier(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16b_borin_prisonnier'])
    choix = choisir(ACT_2_CHOICES, 'scene_16b_borin_prisonnier', "Borin > ")

    if choix == 0:
        recruter_compagnon(joueur, "Borin")
        joueur.modifier_faction("Royaumes Nains", 10)
        joueur.modifier_faction("Aldor", -5)
        secret(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_secret_1')
        dire(ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_response_1')
    elif choix == 1:
        joueur.variables["borin_connait_forgeron_serments"] = True
        ajouter_trait_route(joueur, "Nom nain de Garrick")
        secret(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_secret_2')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_response_2')
    elif choix == 2:
        joueur.modifier_faction("Aldor", 5)
        joueur.modifier_faction("Royaumes Nains", -10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_consequence_2')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_locked_path_1')
        dire(ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_response_3')
    else:
        joueur.variables["borin_libere_sans_recrutement"] = True
        joueur.modifier_faction("Royaumes Nains", 5)
        secret(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_secret_3')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_response_4')

    quete(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_16b_borin_prisonnier_journal_1')


def scene_16c_registres_interdits(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16c_registres_interdits'])
    choix = choisir(ACT_2_CHOICES, 'scene_16c_registres_interdits', "Registres Interdits > ")

    if choix == 0:
        item(joueur, "Copie des Registres Interdits")
        secret(joueur, ACT_2_OUTCOMES, 'scene_16c_registres_interdits_secret_1')
        joueur.variables["secret_malakar"] += 1
        joueur.variables["secret_morvayn"] += 1
        joueur.loyautes["Lyra"] += 10
        dire(ACT_2_OUTCOMES, 'scene_16c_registres_interdits_response_1')
    else:
        secret(joueur, ACT_2_OUTCOMES, 'scene_16c_registres_interdits_secret_2')
        joueur.modifier_faction("Aldor", 15)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16c_registres_interdits_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_16c_registres_interdits_response_2')
        joueur.variables["secret_arthen"] += 1
        joueur.variables["secret_malakar"] += 1
        joueur.variables["secret_morvayn"] += 1
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16c_registres_interdits_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_16c_registres_interdits_response_3')

    journal(joueur, ACT_2_OUTCOMES, 'scene_16c_registres_interdits_journal_1')


def scene_16d_prisonnier_sans_age(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16d_prisonnier_sans_age'])
    choix = choisir(ACT_2_CHOICES, 'scene_16d_prisonnier_sans_age', "Prisonnier sans âge > ")

    if choix == 0:
        secret(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_secret_1')
        joueur.variables["ancien_allie"] = True
        joueur.variables["secret_arthen"] += 1
        joueur.talents.append("Vision Temporelle : +5 à un test une fois par chapitre")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_consequence_1')
        joueur.tension_fragment += 1
        dire(ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_response_1')
    else:
        joueur.variables["prisonnier_sans_age_rejete"] = True
        ajouter_trait_route(joueur, "Raison contre le Temps")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_response_2')
        joueur.variables["prisonnier_libere"] = True
        secret(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_secret_2')
        quete(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_quest_1')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_response_3')

    journal(joueur, ACT_2_OUTCOMES, 'scene_16d_prisonnier_sans_age_journal_1')

def scene_16e_evasion_prison(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_16e_evasion_prison'])
    choix = choisir(ACT_2_CHOICES, 'scene_16e_evasion_prison', "Bourreau des Cendres > ")

    if choix == 1:
        if tester_stat(joueur, "charisme", 16) or tester_stat(joueur, "volonte", 16):
            joueur.variables["garrick_localise"] = True
            secret(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_secret_1')
            dire(ACT_2_OUTCOMES, 'scene_16e_evasion_prison_response_1')
        else:
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_3')
            joueur.pv = max(1, joueur.pv - 6)
    elif choix == 2:
        if tester_stat(joueur, "agilite", 18) and tester_stat(joueur, "volonte", 18):
            joueur.variables["bourreau_capture"] = True
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_5')
            dire(ACT_2_OUTCOMES, 'scene_16e_evasion_prison_response_2')
        else:
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_6')
    victoire = lancer_combat(joueur, creer_ennemi("Bourreau des Cendres"))
    if victoire:
        item(joueur, "Hache des Cendres")
        if choix == 0:
            joueur.ajouter_xp(max(0, 750 - XP_ENNEMIS["Bourreau des Cendres"]))
            consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_4')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_1')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_consequence_2')
        journal(joueur, ACT_2_OUTCOMES, 'scene_16e_evasion_prison_journal_1')
    return victoire


def scene_17_ambassade_elfique(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_17_ambassade_elfique'])
    if joueur.a_consequence("Lyra commence à vous voir comme plus qu'une mission"):
        dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_1')
    elif joueur.a_consequence("Lyra sait que vous pourriez devenir une menace"):
        dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_3')
    choix = choisir(ACT_2_CHOICES, 'scene_17_ambassade_elfique', "Ambassade d'Ellorien > ")

    if choix == 0:
        joueur.loyautes["Lyra"] += 10
        joueur.modifier_faction("Ellorien", -10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_2')
    elif choix == 1:
        if tester_stat(joueur, "agilite", 15):
            secret(joueur, ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_secret_1')
            joueur.ajouter_xp(500)
            dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_5')
        else:
            joueur.modifier_faction("Ellorien", -15)
            dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_6')
    else:
        joueur.loyautes["Lyra"] += 5
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_response_4')

    journal(joueur, ACT_2_OUTCOMES, 'scene_17_ambassade_elfique_journal_1')

def scene_17b_nuit_des_masques(joueur):
    illustrer("assets/images/backgrounds/S05_act_transition.png")
    raconter(ACT_2_SCENE_TEXTS['scene_17b_nuit_des_masques'])

    # [NARRATIF] Résonance
    resonance_temporelle(joueur, "Un masque d'or se brise sur un sol de marbre ensanglanté.")

    if "Mira aux Corbeaux" in joueur.compagnons:
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_response_1')
    choix = choisir(ACT_2_CHOICES, 'scene_17b_nuit_des_masques', "Nuit des Masques > ")

    if choix == 0:
        joueur.modifier_faction("Aldor", 15)
        joueur.influences["Militaire"] += 1
        quete(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_quest_2')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_response_2')
    elif choix == 1:
        joueur.influences["Politique"] += 1
        joueur.talents.append("Réseau d'Informateurs Royaux")
        dire(ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_response_3')
    else:
        joueur.influences["Religieuse"] += 1
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_locked_path_1')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_response_4')

    quete(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_17b_nuit_des_masques_journal_1')

def scene_17c_visage_de_morvayn(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_17c_visage_de_morvayn'])
    decouvrir_codex(joueur, "morvayn")
    ajouter_souvenir(joueur, "masque_morvayn")
    choix = choisir(ACT_2_CHOICES, 'scene_17c_visage_de_morvayn', "Masque de Morvayn > ")

    if choix == 0:
        joueur.variables["morvayn_defie_au_bal"] = True
        ajouter_trait_route(joueur, "Courage devant Morvayn")
        joueur.respect_morvayn += 5
        dire(ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_response_1')
    elif choix == 1:
        joueur.variables["morvayn_cycles_reveles"] = True
        ajouter_trait_route(joueur, "Auditeur de Morvayn")
        secret(joueur, ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_secret_2')
        dire(ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_response_2')
    else:
        joueur.ajouter_xp(700)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_response_3')
        secret(joueur, ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_secret_1')
        journal(joueur, ACT_2_OUTCOMES, 'scene_17c_visage_de_morvayn_journal_1')


def scene_17d_philosophie_du_feu(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_17d_philosophie_du_feu'])
    choix = choisir(ACT_2_CHOICES, 'scene_17d_philosophie_du_feu', "Philosophie du Feu > ")

    if choix == 0:
        joueur.alignement += 1
        dire(ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_response_1')
    elif choix == 1:
        secret(joueur, ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_secret_1')
        joueur.tension_fragment += 1
        dire(ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_response_2')
    else:
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_consequence_1')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_locked_path_1')
        dire(ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_response_3')

    journal(joueur, ACT_2_OUTCOMES, 'scene_17d_philosophie_du_feu_journal_1')

def scene_18_attentat_morvayn(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_18_attentat_morvayn'])
    if joueur.a_consequence("Varos vous haïra"):
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_consequence_1')
        dire(ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_response_1')
    ennemi = {
        "nom": "Assassin de Morvayn",
        "pv": 20,
        "force": 7,
        "agilite": 7,
        "armure": 2,
        "arme": 4,
        "xp": XP_ENNEMIS["Assassin de Morvayn"],
        "or": 12,
    }
    if story_state.morvayn_est_alerte(joueur):
        ennemi["agilite"] += 2
        ennemi["force"] += 1
        dire(ACT_2_OUTCOMES, 'story_state_morvayn_alert_response_1')
    soin = max(0, joueur.pv_max - joueur.pv)
    if soin:
        joueur.pv = joueur.pv_max
        raconter(f"Avant l'embuscade, Lyra resserre vos bandages. Vous récupérez {soin} PV.")
    victoire = lancer_combat(joueur, ennemi)
    if victoire:
        quete(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_quest_1')
        xp_manquant = max(0, joueur.xp_prochain_niveau - joueur.xp)
        if xp_manquant:
            joueur.ajouter_xp(xp_manquant)
        secret(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_secret_1')
        secret(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_secret_2')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_consequence_2')
        journal(joueur, ACT_2_OUTCOMES, 'scene_18_attentat_morvayn_journal_1')
        if recruter(joueur, "Kael"):
            raconter("Un second assassin surgit de l'ombre après le combat — non pour vous frapper, mais pour se poster à vos côtés. \"Kael\", dit-il simplement. \"On m'avait chargé de vous surveiller. Vous venez de me convaincre que je devais plutôt vous suivre.\"")
    return victoire


def scene_18b_document_des_porteurs(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_18b_document_des_porteurs'])
    secret(joueur, ACT_2_OUTCOMES, 'scene_18b_document_des_porteurs_secret_1')
    consequence(joueur, ACT_2_OUTCOMES, 'scene_18b_document_des_porteurs_consequence_1')
    if story_state.elara_est_sauvee(joueur):
        joueur.variables["secret_arthen"] += 1
        dire(ACT_2_OUTCOMES, 'story_state_document_elara_response_1')
    if story_state.prisonnier_sans_age_libere(joueur):
        joueur.connaissance_temporelle += 1
        dire(ACT_2_OUTCOMES, 'story_state_document_prisonnier_response_1')
    if story_state.bourreau_est_capture(joueur):
        joueur.modifier_faction("Aldor", 10)
        dire(ACT_2_OUTCOMES, 'story_state_bourreau_capture_response_1')
    quete(joueur, ACT_2_OUTCOMES, 'scene_18b_document_des_porteurs_quest_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_18b_document_des_porteurs_journal_1')


def scene_18c_sang_des_porteurs(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_18c_sang_des_porteurs'])
    decouvrir_codex(joueur, "porteurs")
    joueur.tension_fragment += 1
    quete(joueur, ACT_2_OUTCOMES, 'scene_18c_sang_des_porteurs_quest_1')
    secret(joueur, ACT_2_OUTCOMES, 'scene_18c_sang_des_porteurs_secret_1')
    consequence(joueur, ACT_2_OUTCOMES, 'scene_18c_sang_des_porteurs_consequence_1')
    reve(joueur, ACT_2_OUTCOMES, 'scene_18c_sang_des_porteurs_dream_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_18c_sang_des_porteurs_journal_1')

def scene_19_tour_du_soleil(joueur):
    raconter(ACT_2_SCENE_TEXTS['scene_19_tour_du_soleil'])
    choix = choisir(ACT_2_CHOICES, 'scene_19_tour_du_soleil', "Tour du Soleil > ")

    if choix == 0:
        joueur.tension_fragment += 1
        dire(ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_response_1')
    elif choix == 1:
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_consequence_1')
        joueur.pv = min(joueur.pv_max, joueur.pv + 6)
        dire(ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_response_2')
    elif choix == 2:
        if "Œil d'Aeternis" in joueur.artefacts and joueur.pm >= 2:
            joueur.pm -= 2
            consequence(joueur, ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_consequence_2')
            dire(ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_response_3')
        else:
            joueur.tension_fragment += 1
            dire(ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_response_4')
    else:
        joueur.loyautes["Lyra"] += 5
        joueur.energie = min(joueur.energie_max, joueur.energie + 5)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_response_5')
    journal(joueur, ACT_2_OUTCOMES, 'scene_19_tour_du_soleil_journal_1')


def scene_20_confrontation_morvayn(joueur):
    from elderia.core.io import illustrer
    illustrer("assets/images/portraits/P07_lyra.png")
    raconter(ACT_2_SCENE_TEXTS['scene_20_confrontation_morvayn'])
    if joueur.classe == "Guerrier":
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_2')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_2')
    elif joueur.classe == "Rôdeur":
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_6')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_8')
    elif joueur.classe == "Mage":
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_8')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_11')
    elif joueur.classe == "Paladin":
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_12')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_16')
    elif joueur.classe == "Nécromancien":
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_20')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_20')
    soin = max(0, joueur.pv_max - joueur.pv)
    if soin:
        joueur.pv = joueur.pv_max
        raconter(f"Le Fragment du Temps se fissure de lumière et referme vos blessures les plus récentes. Vous récupérez {soin} PV.")

    dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_1')
    choix_tactique = choisir(ACT_2_CHOICES, 'scene_20_confrontation_morvayn', "Tactique phase 1 > ")
    bonus_phase_1 = 0
    if choix_tactique == 0:
        bonus_phase_1 = 4
        joueur.pv = max(1, joueur.pv - 4)
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_3')
    elif choix_tactique == 1:
        joueur.pv = min(joueur.pv_max, joueur.pv + 4)
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_9')
    else:
        if "Œil d'Aeternis" in joueur.artefacts and joueur.pm >= 2:
            joueur.pm -= 2
            bonus_phase_1 = 6
            consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_9')
            dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_12')
        else:
            joueur.tension_fragment += 1
            dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_13')
    victoire = lancer_combat(joueur, {
        "nom": "Morvayn, lame obscure",
        "pv": max(16, 32 - bonus_phase_1),
        "force": 10,
        "agilite": 8,
        "armure": 4,
        "arme": 6,
        "xp": 0,
        "or": 0,
    })
    if not victoire:
        return False

    raconter(ACT_2_SCENE_TEXTS['scene_20_confrontation_morvayn_2'])
    choix_tactique = choisir(ACT_2_CHOICES, 'scene_20_confrontation_morvayn', "Tactique phase 2 > ", group="options_2")
    joueur.tension_fragment += 2
    reve(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_dream_1')
    if choix_tactique == 0:
        joueur.pv = min(joueur.pv_max, joueur.pv + 8)
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_4')
    else:
        joueur.pv = max(1, joueur.pv - 8)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_3')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_5')
    victoire = lancer_combat(joueur, {
        "nom": "Écho du Temps",
        "pv": 24 if choix_tactique == 0 else 12,
        "force": 8,
        "agilite": 6,
        "armure": 3,
        "arme": 4,
        "xp": 0,
        "or": 0,
    })
    if not victoire:
        return False

    raconter(ACT_2_SCENE_TEXTS['scene_20_confrontation_morvayn_3'])
    if not tester_stat(joueur, "volonte", 14):
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_4')
        joueur.pv = max(1, joueur.pv - 6)
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_6')
        joueur.pv = min(joueur.pv_max, joueur.pv + 8)
    victoire = lancer_combat(joueur, {
        "nom": "Morvayn marqué",
        "pv": 34,
        "force": 11,
        "agilite": 8,
        "armure": 4,
        "arme": 7,
        "xp": XP_ENNEMIS["Morvayn"],
        "or": 0,
    })
    if not victoire:
        return False

    choix_final = choisir(ACT_2_CHOICES, 'scene_20_confrontation_morvayn', "Morvayn tombe à moins de 10 PV > ", group="options_3")

    if choix_final == 0:
        joueur.variables["morvayn_tue"] = True
        joueur.talents.append("Porteur Victorieux")
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_5')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_7')
    elif choix_final == 1:
        joueur.variables["morvayn_epargne"] = True
        joueur.variables["secret_malakar"] += 2
        joueur.modifier_faction("Ellorien", 20)
        secret(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_secret_5')
        consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_7')
        dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_10')
    else:
        redemption_possible = joueur.loyautes["Lyra"] >= 80 and joueur.volonte >= 15 and story_state.connait_assez_morvayn(joueur)
        if redemption_possible and (tester_stat(joueur, "volonte", 18) or tester_stat(joueur, "charisme", 18)):
            joueur.variables["morvayn_recrute"] = True
            joueur.loyautes["Morvayn"] = 10
            consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_10')
            dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_14')
        else:
            joueur.variables["morvayn_tue"] = True
            consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_11')
            dire(ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_response_15')

    raconter(ACT_2_SCENE_TEXTS['scene_20_confrontation_morvayn_4'])
    if story_state.morvayn_est_recrute(joueur):
        dire(ACT_2_OUTCOMES, 'story_state_morvayn_recrute_response_1')
    elif story_state.morvayn_est_epargne(joueur):
        dire(ACT_2_OUTCOMES, 'story_state_morvayn_epargne_response_1')
    elif story_state.morvayn_est_tue(joueur):
        dire(ACT_2_OUTCOMES, 'story_state_morvayn_tue_response_1')
    quete(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_quest_1')
    joueur.or_poches += 500
    joueur.reputation += 10
    joueur.modifier_faction("Aldor", 15)
    joueur.fragments_temps = min(25, joueur.fragments_temps + 5)
    item(joueur, "Fragment Temporel Majeur")
    item(joueur, "Sceau des Porteurs")
    joueur.talents.append("Vision d'Avenir : une relance par chapitre")
    secret(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_secret_1')
    secret(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_secret_2')
    joueur.variables["secret_morvayn"] += 1
    secret(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_secret_3')
    secret(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_secret_4')
    decouvrir_codex(joueur, "malakar")
    consequence(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_consequence_1')
    journal(joueur, ACT_2_OUTCOMES, 'scene_20_confrontation_morvayn_journal_1')
    joueur.acte_courant = "Acte III - La Chasse aux Cristaux"
    afficher_bilan_acte_2(joueur)
    return True


def afficher_bilan_acte_2(joueur):
    afficher_bilan_acte(joueur, "ACTE II - LES ROYAUMES DÉCHIRÉS")
    print("\n" + "=" * 60)
    print("BILAN DE L'ACTE II - LES ROYAUMES DÉCHIRÉS")
    print("=" * 60)
    print(f"Niveau atteint : {joueur.niveau} | PV {joueur.pv}/{joueur.pv_max} | Or {joueur.or_poches}g")
    print(f"Allié politique choisi : {joueur.allie_politique or 'Aucun'}")
    print("\nCompagnons recrutés :")
    if joueur.compagnons:
        for compagnon in joueur.compagnons:
            print(f"- {compagnon} (loyauté {joueur.loyautes.get(compagnon, 0)}/100)")
    else:
        print("- Aucun")
    print("\nQuêtes accomplies :")
    quetes_terminees = [nom for nom, fait in joueur.quetes.items()
    if fait]
    if quetes_terminees:
        for nom in quetes_terminees:
            print(f"- {nom}")
    else:
        print("- Aucune")
    print("\nSecrets majeurs découverts :")
    if joueur.secrets:
        for secret in joueur.secrets[-5:]:
            print(f"- {secret}")
        if len(joueur.secrets) > 5:
            print(f"... et {len(joueur.secrets) - 5} autre(s) secret(s) dans votre fiche complète.")
    else:
        print("- Aucun")
    print("=" * 60)


def scene_19_choix_faction(joueur):
    dire(ACT_2_OUTCOMES, 'scene_19_choix_faction_response_1')
    options = [
        "Soutenir provisoirement la couronne d'Aldor",
        "Marcher avec les réseaux de Varken pour retrouver Garrick",
        "Faire confiance à Lyra et chercher l'appui d'Ellorien",
        "Refuser les maîtres et partir vers les Cités Libres",
    ]
    afficher_options(options)
    choix = demander_choix("Premier allié politique > ", options)

    if choix == 0:
        joueur.allie_politique = "Aldor"
        joueur.variables["alliance_choisie"] = "Aldor"
        joueur.talents.append("Commandement I : +10 % dégâts alliés")
        item(joueur, "Armure Royale")
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_1')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_2')
        joueur.modifier_faction("Aldor", 20)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_consequence_1')
    elif choix == 1:
        joueur.allie_politique = "Ligue de Varken"
        joueur.variables["alliance_choisie"] = "Ligue de Varken"
        joueur.talents.append("Influence Marchande : prix -20 %")
        joueur.or_poches += 100
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_3')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_4')
        joueur.modifier_faction("Ligue de Varken", 20)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_consequence_2')
    elif choix == 2:
        joueur.allie_politique = "Ellorien"
        joueur.variables["alliance_choisie"] = "Ellorien"
        joueur.talents.append("Sagesse Antique : +10 Mana")
        joueur.pm_max += 10
        joueur.pm += 10
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_5')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_6')
        joueur.modifier_faction("Ellorien", 20)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_consequence_3')
    else:
        joueur.allie_politique = "Cités Libres"
        joueur.variables["alliance_choisie"] = "Cités Libres"
        joueur.talents.append("Réseau d'Informateurs : révèle les quêtes cachées")
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_7')
        porte_fermee(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_locked_path_8')
        joueur.modifier_faction("Cités Libres", 20)
        joueur.modifier_faction("Aldor", -10)
        consequence(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_consequence_4')
        quete(joueur, ACT_2_OUTCOMES, 'scene_19_choix_faction_quest_1')
    joueur.journal.append(f"Fin provisoire de l'Acte II : vous choisissez {joueur.allie_politique}, fermant d'autres routes vers Garrick et les Cristaux.")


def jouer_acte_2(joueur):
    sauvegarder(joueur)
    scene_13_arrivee_aldorath(joueur)
    transition(ACT_2_OUTCOMES, 'transition_13_to_13a')
    lancer_evenement_aleatoire(joueur)
    scene_13a_quartiers_aldorath(joueur)
    transition(ACT_2_OUTCOMES, 'transition_13a_to_13d')
    scene_13d_fille_aux_corbeaux(joueur)
    transition(ACT_2_OUTCOMES, 'transition_13d_to_13e')
    scene_13e_taverne_dragon_gris(joueur)
    ravitaillement(joueur, "Taverne du Dragon Gris")
    visiter_marchand(joueur, MARCHAND_STOCK_ACTE_2, "\nUn armurier d'Aldorath étale sa marchandise récupérée sur les Cendreux.", palier="mineur")
    transition(ACT_2_OUTCOMES, 'transition_13e_to_14')
    scene_14_conseil_royal(joueur)
    transition(ACT_2_OUTCOMES, 'transition_14_to_14b')
    scene_14b_fragments_du_mensonge(joueur)
    transition(ACT_2_OUTCOMES, 'transition_14b_to_14c')
    scene_14c_archives_aldor(joueur)
    transition(ACT_2_OUTCOMES, 'transition_14c_to_17')
    scene_17_ambassade_elfique(joueur)
    transition(ACT_2_OUTCOMES, 'transition_17_to_13b')
    scene_13b_disparus_aldorath(joueur)
    transition(ACT_2_OUTCOMES, 'transition_13b_to_17b')
    scene_17b_nuit_des_masques(joueur)
    transition(ACT_2_OUTCOMES, 'transition_17b_to_17c')
    scene_17c_visage_de_morvayn(joueur)
    transition(ACT_2_OUTCOMES, 'transition_17c_to_17d')
    scene_17d_philosophie_du_feu(joueur)
    transition(ACT_2_OUTCOMES, 'transition_17d_to_15')
    scene_15_marche_varken(joueur)
    transition(ACT_2_OUTCOMES, 'transition_15_to_15b')
    scene_15b_lettre_cachee(joueur)
    transition(ACT_2_OUTCOMES, 'transition_15b_to_16')
    sauvegarder(joueur)
    if not retry_scene(scene_16_prison_des_cendres, joueur, ecran_game_over):
        return
    transition(ACT_2_OUTCOMES, 'transition_16_to_16a')
    scene_16a_cellules_abandonnees(joueur)
    transition(ACT_2_OUTCOMES, 'transition_16a_to_16d')
    scene_16d_prisonnier_sans_age(joueur)
    transition(ACT_2_OUTCOMES, 'transition_16d_to_16c')
    scene_16c_registres_interdits(joueur)
    transition(ACT_2_OUTCOMES, 'transition_16c_to_16b')
    scene_16b_borin_prisonnier(joueur)
    transition(ACT_2_OUTCOMES, 'transition_16b_to_16e')
    if not retry_scene(scene_16e_evasion_prison, joueur, ecran_game_over):
        return
    repos_de_camp(joueur, "Refuge sous l'ancien aqueduc")
    transition(ACT_2_OUTCOMES, 'transition_16e_to_19_choix')
    scene_19_choix_faction(joueur)
    transition(ACT_2_OUTCOMES, 'transition_19_choix_to_13c')
    scene_13c_oeil_aeternis(joueur)
    transition(ACT_2_OUTCOMES, 'transition_13c_to_18c')
    scene_18c_sang_des_porteurs(joueur)
    transition(ACT_2_OUTCOMES, 'transition_18c_to_18')
    sauvegarder(joueur)
    if not retry_scene(scene_18_attentat_morvayn, joueur, ecran_game_over):
        return
    transition(ACT_2_OUTCOMES, 'transition_18_to_18b')
    scene_18b_document_des_porteurs(joueur)
    transition(ACT_2_OUTCOMES, 'transition_18b_to_19')
    scene_19_tour_du_soleil(joueur)
    transition(ACT_2_OUTCOMES, 'transition_19_to_20')
    if not retry_scene(scene_20_confrontation_morvayn, joueur, ecran_game_over):
        return

def jouer(joueur=None, sauvegarder=True):
    if joueur is None:
        from elderia.core.runtime import charger_ou_preparer

        joueur = charger_ou_preparer(2)
    joueur.acte_courant = "Acte II - Les Royaumes D?chir?s"
    if joueur.pv > 0:
        jouer_acte_2(joueur)
    if sauvegarder and joueur.pv > 0:
        sauvegarder_partie(joueur)
    return joueur
