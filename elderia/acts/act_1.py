from elderia.content.act_1_choices import ACT_1_CHOICES
from elderia.content.act_1_scenes import ACT_1_SCENE_TEXTS
from elderia.core.combat import creer_ennemi, lancer_combat
from elderia.core.codex import ajouter_souvenir, decouvrir_codex
from elderia.core.gameplay import interaction_compagnons, interjection_compagnon, ravitaillement, repos_de_camp
from elderia.core.io import demander_choix, lancer_de, raconter, illustrer
from elderia.core.narrative_state import afficher_bilan_acte, ajouter_trait_route
from elderia.core.save import sauvegarder as sauvegarder_partie
from elderia.core.scene_engine import item, afficher_options, choisir, consequence, dire, journal, porte_fermee, quete, resonance_temporelle, retry_scene, reve, secret, transition
from elderia.core import story_state
from elderia.content.act_1_outcomes import ACT_1_OUTCOMES
from elderia.core.systems import (
    afficher_prologue,
    afficher_structure_campagne,
    ajouter_fragment_temps,
    creer_personnage,
    ecran_game_over,
    recruter_compagnon,
    tester_stat,
    visiter_marchand,
)
from elderia.core.procedural import lancer_evenement_aleatoire
from elderia.data.tables import BIJOUX, BOUCLIERS, SAUVEGARDE_FICHIER, XP_ENNEMIS

sauvegarder = sauvegarder_partie

def scene_1a_vie_quotidienne(joueur):
    illustrer("assets/images/backgrounds/S02_main_menu.png")
    raconter(ACT_1_SCENE_TEXTS['scene_1a_vie_quotidienne'])
    decouvrir_codex(joueur, "brumebois")
    ajouter_souvenir(joueur, "pain_mira")
    if joueur.variables.get("nouvelle_route_plus"):
        raconter("Pendant un instant, le matin du festival vous paraît déjà vécu. Vous ne savez pas ce qui va arriver, seulement que certaines phrases ont laissé une trace plus profonde que la mémoire.")

    # [AMÉLIORATION NARRATIVE] Choix d'Origine
    options = list(ACT_1_CHOICES['scene_1a_vie_quotidienne']['options'])
    if joueur.origine == "Noble Déchu":
        options.append("[Noble] Rappeler la grandeur passée d'Elderia lors du discours")
    elif joueur.origine == "Érudit Errant":
        options.append("[Érudit] Analyser les runes gravées sur l'autel du festival")
    elif joueur.origine == "Enfant des Rues":
        options.append("[Enfant des Rues] Repérer un pickpocket dans la foule et le prendre la main dans le sac")

    choix = demander_choix("Avant le discours du chef > ", options)

    if choix == 0:
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_consequence_1')
        journal(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_journal_1')
        dire(ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_response_1')
    elif choix == 1:
        # [D&D] Utilisation de l'avantage si le héros est un Ancien Soldat
        avantage = joueur.origine == "Ancien Soldat"
        if tester_stat(joueur, "force", 13, avantage=avantage):
            joueur.reputation += 1
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_consequence_3')
            dire(ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_response_3')
        else:
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_consequence_4')
            dire(ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_response_4')
        journal(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_journal_2')
    elif choix == 2:
        joueur.reputation += 1
        joueur.alignement += 1
        item(joueur, "Baume de Mira")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_consequence_2')
        journal(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_journal_3')
        dire(ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_response_2')
    elif choix == 3: # Option Noble, Érudit ou Enfant des Rues
        if joueur.origine == "Noble Déchu":
            raconter("Votre voix résonne avec une autorité naturelle. Les villageois se redressent, inspirés par votre évocation des temps anciens.")
            joueur.reputation += 2
            joueur.alignement += 1
        elif joueur.origine == "Érudit Errant":
            raconter("En étudiant l'autel, vous remarquez que les runes de protection sont inhabituellement ternes, comme si une force les drainait.")
            joueur.connaissance_temporelle += 1
            decouvrir_codex(joueur, "magie_ancienne")
        elif joueur.origine == "Enfant des Rues":
            raconter("Vos vieux réflexes ne vous ont pas quitté : vous repérez la main baladeuse avant même qu'elle n'atteigne sa cible, et retournez la leçon contre son auteur.")
            gain = 8
            joueur.or_poches += gain
            joueur.reputation += 1
            raconter(f"Vous récupérez {gain} pièces d'or et un peu de respect de la foule amusée.")

    quete(joueur, ACT_1_OUTCOMES, 'scene_1a_vie_quotidienne_quest_1')

def scene_1b_atelier_garrick(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_1b_atelier_garrick'])
    sujets = list(ACT_1_CHOICES['scene_1b_atelier_garrick']['sujets'])
    for _ in range(2):
        print("\nGarrick attend. Pour une fois, il ne fuit pas la conversation.")
        for index, sujet in enumerate(sujets, 1):
            print(f"{index}. {sujet}")
        sujet = sujets.pop(demander_choix("Sujet > ", sujets))
        if "trouvé" in sujet:
            joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
            secret(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_secret_2')
            dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_2')
        elif "première arme" in sujet:
            joueur.force += 1
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_consequence_2')
            dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_5')
        elif "cauchemars" in sujet:
            quete(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_quest_2')
            secret(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_secret_4')
            dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_6')
        else:
            joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_consequence_3')
            dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_7')

    choix = choisir(ACT_1_CHOICES, 'scene_1b_atelier_garrick', "Dans l'atelier > ")

    if choix == 0:
        secret(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_secret_1')
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_1')
    elif choix == 1:
        joueur.variables["cherche_serviteurs_malakar"] = True
        ajouter_trait_route(joueur, "Chasseur des Cendres")
        quete(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_quest_1')
        secret(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_secret_3')
        dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_3')
    else:
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_response_4')

    journal(joueur, ACT_1_OUTCOMES, 'scene_1b_atelier_garrick_journal_1')


def scene_1c_maison_de_mira(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_1c_maison_de_mira'])
    choix = choisir(ACT_1_CHOICES, 'scene_1c_maison_de_mira', "Chez Mira > ")

    if choix == 0:
        item(joueur, "Baume de Mira")
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_response_1')
    else:
        secret(joueur, ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_secret_1')
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        joueur.variables["vision_mira_profondie"] = True
        ajouter_trait_route(joueur, "Écouté par Mira")
        dire(ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_response_2')
        reve(joueur, ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_dream_1')
        quete(joueur, ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_quest_1')
        dire(ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_response_3')
        journal(joueur, ACT_1_OUTCOMES, 'scene_1c_maison_de_mira_journal_1')
def scene_1d_jeux_du_festival(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_1d_jeux_du_festival'])
    choix = choisir(ACT_1_CHOICES, 'scene_1d_jeux_du_festival', "Jeux du festival > ")

    if choix == 0:
        if tester_stat(joueur, "force", 13):
            joueur.reputation += 1
            ajouter_souvenir(joueur, "rire_marek")
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_consequence_1')
            dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_1')
        else:
            ajouter_souvenir(joueur, "rire_marek")
            consequence(joueur, ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_consequence_2')
            dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_2')
    elif choix == 1:
        if tester_stat(joueur, "agilite", 13):
            item(joueur, "Ruban de tireur du festival")
            dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_4')
        else:
            joueur.reputation += 1
            dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_5')
    elif choix == 2:
        joueur.alignement += 1
        joueur.reputation += 1
        item(joueur, "Amulette de Brumebois")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_consequence_3')
        dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_3')
    else:
        joueur.energie = min(joueur.energie_max, joueur.energie + 3)
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_consequence_4')
        dire(ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_response_6')

    journal(joueur, ACT_1_OUTCOMES, 'scene_1d_jeux_du_festival_journal_1')


def scene_1e_veillee_des_anciens(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_1e_veillee_des_anciens'])
    ajouter_souvenir(joueur, "premiere_flambebleue")
    choix = choisir(ACT_1_CHOICES, 'scene_1e_veillee_des_anciens', "Veillée des anciens > ")

    if choix == 0:
        joueur.reputation += 1
        secret(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_response_1')
    elif choix == 1:
        joueur.variables["flamme_bleue_cachee"] = True
        ajouter_trait_route(joueur, "Silence de Brumebois")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_response_2')
    elif choix == 2:
        if tester_stat(joueur, "agilite", 12):
            secret(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_secret_2')
            quete(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_quest_1')
            dire(ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_response_3')
        else:
            joueur.reputation -= 1
            dire(ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_response_4')
    else:
        joueur.variables["veillee_observee_en_silence"] = True
        ajouter_trait_route(joueur, "Regard qui retient tout")
        secret(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_secret_3')
        dire(ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_response_5')

    journal(joueur, ACT_1_OUTCOMES, 'scene_1e_veillee_des_anciens_journal_1')

def scene_1f_travaux_et_marche(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_1f_travaux_et_marche'])
    choix = choisir(ACT_1_CHOICES, 'scene_1f_travaux_et_marche', "Travail à Brumebois > ", group="travaux")

    gain = 0
    if choix == 0:
        gain = 15
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        joueur.reputation += 1
        dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_1')
    elif choix == 1:
        gain = 12
        joueur.modifier_faction("Cités Libres", 5)
        consequence(joueur, ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_2')
    elif choix == 2:
        if tester_stat(joueur, "agilite", 12):
            gain = 18
            joueur.reputation += 1
            dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_3')
        else:
            gain = 6
            dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_4')
    elif choix == 3:
        gain = 10
        joueur.alignement += 1
        item(joueur, "Baume de Mira")
        dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_5')
    else:
        joueur.energie = min(joueur.energie_max, joueur.energie + 2)
        dire(ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_response_6')

    if gain:
        joueur.or_poches += gain
        raconter(f"Vous gagnez {gain} pièces d'or. Votre bourse contient maintenant {joueur.or_poches}g.")

    if choisir(ACT_1_CHOICES, 'scene_1f_travaux_et_marche', "Après le travail > ") == 0:
        visiter_marchand(joueur)
        # Ne proposer que des objets réellement meilleurs que l'équipement actuel (l'achat au marchand
        # équipe déjà automatiquement le meilleur bouclier/bijou trouvé) pour éviter de suggérer un
        # retour en arrière vers un objet plus faible.
        options_bouclier = [
            objet for objet in joueur.inventaire
            if objet in BOUCLIERS and objet != joueur.bouclier and joueur.bouclier_est_meilleure(objet)
        ]
        if options_bouclier:
            options_bouclier.append("Ne rien changer")
            print("\nBoucliers disponibles :")
            afficher_options(options_bouclier)
            choix_bouclier = demander_choix("Équiper un bouclier > ", options_bouclier)
            if options_bouclier[choix_bouclier] != "Ne rien changer":
                joueur.equiper_bouclier(options_bouclier[choix_bouclier])
        options_bijou = [
            objet for objet in joueur.inventaire
            if objet in BIJOUX and objet != joueur.bijou and joueur.bijou_est_meilleur(objet)
        ]
        if options_bijou:
            options_bijou.append("Ne rien changer")
            print("\nBijoux disponibles :")
            afficher_options(options_bijou)
            choix_bijou = demander_choix("Équiper un bijou > ", options_bijou)
            if options_bijou[choix_bijou] != "Ne rien changer":
                joueur.equiper_bijou(options_bijou[choix_bijou])

    journal(joueur, ACT_1_OUTCOMES, 'scene_1f_travaux_et_marche_journal_1')

def chapitre_1(joueur):
    raconter(ACT_1_SCENE_TEXTS['chapitre_1'])
    choix = choisir(ACT_1_CHOICES, 'chapitre_1', "Votre décision > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.alignement += 1
        joueur.modifier_faction("Aldor", 5)
        consequence(joueur, ACT_1_OUTCOMES, 'chapitre_1_consequence_1')
        journal(joueur, ACT_1_OUTCOMES, 'chapitre_1_journal_1')
        dire(ACT_1_OUTCOMES, 'chapitre_1_response_1')
    elif choix == 1:
        joueur.or_poches += 30
        joueur.reputation -= 1
        joueur.modifier_faction("Ligue de Varken", 5)
        consequence(joueur, ACT_1_OUTCOMES, 'chapitre_1_consequence_2')
        journal(joueur, ACT_1_OUTCOMES, 'chapitre_1_journal_2')
        dire(ACT_1_OUTCOMES, 'chapitre_1_response_2')
        if tester_stat(joueur, "agilite", 13):
            item(joueur, "Médaillon Royal")
            joueur.alignement -= 1
            joueur.modifier_faction("Aldor", -5)
            consequence(joueur, ACT_1_OUTCOMES, 'chapitre_1_consequence_4')
            journal(joueur, ACT_1_OUTCOMES, 'chapitre_1_journal_4')
            dire(ACT_1_OUTCOMES, 'chapitre_1_response_4')
        else:
            joueur.reputation -= 2
            joueur.alignement -= 2
            joueur.modifier_faction("Aldor", -10)
            consequence(joueur, ACT_1_OUTCOMES, 'chapitre_1_consequence_5')
            dire(ACT_1_OUTCOMES, 'chapitre_1_response_5')
    else:
        quete(joueur, ACT_1_OUTCOMES, 'chapitre_1_quest_1')
        secret(joueur, ACT_1_OUTCOMES, 'chapitre_1_secret_1')
        joueur.modifier_faction("Serviteurs de Malakar", -5)
        consequence(joueur, ACT_1_OUTCOMES, 'chapitre_1_consequence_3')
        journal(joueur, ACT_1_OUTCOMES, 'chapitre_1_journal_3')
        dire(ACT_1_OUTCOMES, 'chapitre_1_response_3')
def scene_2a_les_premiers_cris(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_2a_les_premiers_cris'])
    choix = choisir(ACT_1_CHOICES, 'scene_2a_les_premiers_cris', "Les premiers cris > ")

    if choix == 0:
        joueur.modifier_faction("Aldor", 5)
        journal(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_journal_1')
        dire(ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_response_1')
    elif choix == 1:
        joueur.alignement += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_consequence_1')
        journal(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_journal_2')
        dire(ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_response_2')
    elif choix == 2:
        joueur.variables["attaque_brumebois_analysee"] = True
        ajouter_trait_route(joueur, "Œil de la forge")
        secret(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_secret_1')
        journal(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_journal_3')
        dire(ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_response_3')
    else:
        joueur.reputation -= 1
        journal(joueur, ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_journal_4')
        dire(ACT_1_OUTCOMES, 'scene_2a_les_premiers_cris_response_4')


def scene_2b_chercher_mira(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_2b_chercher_mira'])
    choix = choisir(ACT_1_CHOICES, 'scene_2b_chercher_mira', "Avec Mira > ")

    if choix == 0:
        joueur.reputation += 2
        joueur.alignement += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2b_chercher_mira_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_2b_chercher_mira_response_1')
    else:
        joueur.variables["mira_connait_la_marque"] = True
        ajouter_trait_route(joueur, "Confiance de Mira")
        secret(joueur, ACT_1_OUTCOMES, 'scene_2b_chercher_mira_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_2b_chercher_mira_response_2')
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2b_chercher_mira_consequence_2')
        if "Dague rouillée" in joueur.inventaire:
            joueur.inventaire.remove("Dague rouillée")
            if joueur.arme == "Dague rouillée":
                joueur.arme = "Mains nues"
                dire(ACT_1_OUTCOMES, 'scene_2b_chercher_mira_response_4')
            else:
                dire(ACT_1_OUTCOMES, 'scene_2b_chercher_mira_response_5')
        else:
            dire(ACT_1_OUTCOMES, 'scene_2b_chercher_mira_response_3')

    journal(joueur, ACT_1_OUTCOMES, 'scene_2b_chercher_mira_journal_1')


def scene_2c_place_en_flammes(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_2c_place_en_flammes'])
    choix = choisir(ACT_1_CHOICES, 'scene_2c_place_en_flammes', "Place en flammes > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.modifier_faction("Cités Libres", 5)
        dire(ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_response_1')
        if story_state.a_lien_avec_marek(joueur):
            dire(ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_response_2')
        if story_state.a_baume_de_mira(joueur):
            joueur.inventaire.remove("Baume de Mira")
            joueur.pv = min(joueur.pv_max, joueur.pv + 4)
            dire(ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_response_3')
    else:
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_consequence_1')
        joueur.tension_fragment += 1
        dire(ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_response_4')
        joueur.variables["ordres_morvayn_recuperes"] = True
        ajouter_trait_route(joueur, "Lecteur des cendres")
        item(joueur, "Ordres brûlés de Morvayn")
        quete(joueur, ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_quest_2')
        secret(joueur, ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_response_5')
    quete(joueur, ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_quest_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_2c_place_en_flammes_journal_1')

def scene_2d_premier_sang(joueur):
    illustrer("assets/images/backgrounds/S04_combat_arena.png")
    raconter(ACT_1_SCENE_TEXTS['scene_2d_premier_sang'])
    return lancer_combat(joueur, creer_ennemi("Porteur de Cendres"))


def scene_2e_morvayn_sur_la_place(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_2e_morvayn_sur_la_place'])
    choix = choisir(ACT_1_CHOICES, 'scene_2e_morvayn_sur_la_place', "Face à Morvayn > ")

    if choix == 0:
        joueur.variables["sceau_actif_nommee"] = True
        ajouter_trait_route(joueur, "Marque nommée")
        secret(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_secret_1')
        joueur.respect_morvayn += 1
        dire(ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_response_1')
    elif choix == 1:
        joueur.variables["garrick_lie_aux_porteurs"] = True
        ajouter_trait_route(joueur, "Doute sur Garrick")
        secret(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_secret_2')
        quete(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_quest_1')
        dire(ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_response_2')
    else:
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_consequence_2')
        dire(ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_response_3')
        consequence(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_consequence_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_2e_morvayn_sur_la_place_journal_1')

from elderia.core.gameplay import interjection_compagnon

def scene_3_la_fuite(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_3_la_fuite'])

    # [AMÉLIORATION NARRATIVE] Interjection de Compagnon
    interjection_compagnon(joueur, "Garrick", "Courrez, mon ami ! Ne laissez pas les flammes de Malakar vous rattraper !")

    decouvrir_codex(joueur, "garrick")
    ajouter_souvenir(joueur, "main_garrick")
    choix = choisir(ACT_1_CHOICES, 'scene_3_la_fuite', "Que faites-vous ? ")

    if choix == 0:
        joueur.variables["dragon_argent_revele"] = True
        ajouter_trait_route(joueur, "Ombre argentée")
        secret(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_3_la_fuite_response_2')
    elif choix == 1:
        joueur.modifier_faction("Cités Libres", 5)
        dire(ACT_1_OUTCOMES, 'scene_3_la_fuite_response_3')
    else:
        joueur.reputation += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_consequence_2')
        dire(ACT_1_OUTCOMES, 'scene_3_la_fuite_response_4')

    if "Médaillon du Dragon-Étoile" not in joueur.inventaire:
        item(joueur, "Médaillon du Dragon-Étoile")
        raconter("\n📖 [LORE] Le médaillon est froid au toucher. Son métal semble absorber la lumière des flammes.")
        decouvrir_codex(joueur, "dragon_etoile")
    quete(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_quest_1')
    quete(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_quest_2')
    quete(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_quest_3')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_consequence_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_3_la_fuite_journal_1')
    dire(ACT_1_OUTCOMES, 'scene_3_la_fuite_response_1')
    return True


def scene_4_grande_route(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_4_grande_route'])
    reve(joueur, ACT_1_OUTCOMES, 'scene_4_grande_route_dream_1')
    choix = choisir(ACT_1_CHOICES, 'scene_4_grande_route', "Sur la route > ")

    if choix == 0:
        if "Ration" in joueur.inventaire:
            joueur.inventaire.remove("Ration")
            joueur.reputation += 1
            joueur.modifier_faction("Cités Libres", 5)
            dire(ACT_1_OUTCOMES, 'scene_4_grande_route_response_1')
        else:
            dire(ACT_1_OUTCOMES, 'scene_4_grande_route_response_2')
    elif choix == 1:
        quete(joueur, ACT_1_OUTCOMES, 'scene_4_grande_route_quest_1')
        joueur.modifier_faction("Aldor", 5)
        dire(ACT_1_OUTCOMES, 'scene_4_grande_route_response_3')
    else:
        joueur.modifier_faction("Serviteurs de Malakar", -5)
        dire(ACT_1_OUTCOMES, 'scene_4_grande_route_response_4')

    journal(joueur, ACT_1_OUTCOMES, 'scene_4_grande_route_journal_1')


def scene_4a_campement_apres_brumebois(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_4a_campement_apres_brumebois'])
    choix = choisir(ACT_1_CHOICES, 'scene_4a_campement_apres_brumebois', "Campement > ")

    if choix == 0:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        secret(joueur, ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_response_1')
    elif choix == 1:
        joueur.tension_fragment += 1
        reve(joueur, ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_dream_1')
        dire(ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_response_2')
    elif choix == 2:
        joueur.variables["campement_vigilant"] = True
        ajouter_trait_route(joueur, "Veilleur de route")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_response_3')
    else:
        soin = min(joueur.pv_max - joueur.pv, 6)
        joueur.pv += soin
        raconter(f"Vous dormez mal, mais votre corps récupère {soin} PV.")

    journal(joueur, ACT_1_OUTCOMES, 'scene_4a_campement_apres_brumebois_journal_1')


def scene_5_pont_des_corbeaux(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_5_pont_des_corbeaux'])
    decouvrir_codex(joueur, "lyra")
    ajouter_souvenir(joueur, "regard_lyra")
    victoire = lancer_combat(joueur, creer_ennemi("Bandit", nom="Chef bandit du Pont"))
    if not victoire:
        return False

    ajouter_fragment_temps(joueur, 1)
    joueur.tension_fragment += 1
    joueur.pv = max(1, joueur.pv - 2)
    reve(joueur, ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_dream_1')
    secret(joueur, ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_secret_1')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_consequence_1')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_consequence_2')
    journal(joueur, ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_journal_1')
    dire(ACT_1_OUTCOMES, 'scene_5_pont_des_corbeaux_response_1')
    return True


def scene_6_lyra(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_6_lyra'])
    recruter_compagnon(joueur, "Lyra")
    soin = max(0, joueur.pv_max // 2 - joueur.pv)
    if soin:
        joueur.pv += soin
        raconter(f"Lyra panse vos blessures avec des herbes elfiques. Vous récupérez {soin} PV.")
    choix = choisir(ACT_1_CHOICES, 'scene_6_lyra', "Avec Lyra > ")

    if choix == 0:
        joueur.modifier_faction("Ellorien", 10)
        consequence(joueur, ACT_1_OUTCOMES, 'scene_6_lyra_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_6_lyra_response_1')
    elif choix == 1:
        joueur.modifier_faction("Ellorien", -5)
        secret(joueur, ACT_1_OUTCOMES, 'scene_6_lyra_secret_1')
        consequence(joueur, ACT_1_OUTCOMES, 'scene_6_lyra_consequence_2')
        dire(ACT_1_OUTCOMES, 'scene_6_lyra_response_2')
    else:
        joueur.variables["lyra_alliance_prudente"] = True
        ajouter_trait_route(joueur, "Alliance à distance")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_6_lyra_consequence_3')
        dire(ACT_1_OUTCOMES, 'scene_6_lyra_response_3')
    journal(joueur, ACT_1_OUTCOMES, 'scene_6_lyra_journal_1')


def scene_6a_campement_avec_lyra(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_6a_campement_avec_lyra'])
    choix = choisir(ACT_1_CHOICES, 'scene_6a_campement_avec_lyra', "Camp avec Lyra > ")

    if choix == 0:
        joueur.loyautes["Lyra"] += 10
        consequence(joueur, ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_response_1')
    elif choix == 1:
        secret(joueur, ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_secret_1')
        joueur.loyautes["Lyra"] += 5
        dire(ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_response_2')
    elif choix == 2:
        joueur.modifier_faction("Ellorien", -5)
        consequence(joueur, ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_consequence_2')
        dire(ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_response_3')
    else:
        joueur.loyautes["Lyra"] += 15
        reve(joueur, ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_dream_1')
        dire(ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_response_4')
    journal(joueur, ACT_1_OUTCOMES, 'scene_6a_campement_avec_lyra_journal_1')

def scene_7_val_therys(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7_val_therys'])
    decouvrir_codex(joueur, "val_therys")
    quete(joueur, ACT_1_OUTCOMES, 'scene_7_val_therys_quest_1')
    choix = choisir(ACT_1_CHOICES, 'scene_7_val_therys', "Dans Val-Therys > ")

    if choix == 0:
        item(joueur, "Chronique de Val-Therys")
        joueur.connaissance_temporelle += 1
        secret(joueur, ACT_1_OUTCOMES, 'scene_7_val_therys_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_7_val_therys_response_1')
    elif choix == 1:
        joueur.fragments_temps = min(25, joueur.fragments_temps + 1)
        consequence(joueur, ACT_1_OUTCOMES, 'scene_7_val_therys_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_7_val_therys_response_2')
    else:
        joueur.modifier_faction("Serviteurs de Malakar", -5)
        dire(ACT_1_OUTCOMES, 'scene_7_val_therys_response_3')

    journal(joueur, ACT_1_OUTCOMES, 'scene_7_val_therys_journal_1')

def scene_7a_quartier_des_nobles(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7a_quartier_des_nobles'])
    choix = choisir(ACT_1_CHOICES, 'scene_7a_quartier_des_nobles', "Quartier des Nobles > ")

    if choix == 0:
        joueur.variables["roi_val_therys_malakar"] = True
        ajouter_trait_route(joueur, "Mémoire des rois morts")
        secret(joueur, ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_secret_1')
        dire(ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_response_1')
    elif choix == 1:
        joueur.tension_fragment += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_response_2')
    else:
        joueur.modifier_faction("Serviteurs de Malakar", -5)
        dire(ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_response_3')
    journal(joueur, ACT_1_OUTCOMES, 'scene_7a_quartier_des_nobles_journal_1')

def scene_7b_bibliotheque_engloutie(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7b_bibliotheque_engloutie'])
    choix = choisir(ACT_1_CHOICES, 'scene_7b_bibliotheque_engloutie', "Bibliothèque Engloutie > ")

    if choix == 0:
        secret(joueur, ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_secret_1')
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_response_1')
    elif choix == 1:
        secret(joueur, ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_secret_2')
        quete(joueur, ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_quest_1')
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_response_2')
    else:
        item(joueur, "Carte ancienne d'Elderia")
        joueur.modifier_faction("Cités Libres", 5)
        dire(ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_response_3')
        journal(joueur, ACT_1_OUTCOMES, 'scene_7b_bibliotheque_engloutie_journal_1')

def scene_7c_catacombes(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7c_catacombes'])
    victoire = lancer_combat(joueur, creer_ennemi("Squelette", nom="Squelette de Val-Therys"))
    if victoire:
        item(joueur, "Clef de cuivre ancienne")
        consequence(joueur, ACT_1_OUTCOMES, 'scene_7c_catacombes_consequence_1')
        journal(joueur, ACT_1_OUTCOMES, 'scene_7c_catacombes_journal_1')
    return victoire


def scene_7d_temple_du_cycle(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7d_temple_du_cycle'])
    choix = choisir(ACT_1_CHOICES, 'scene_7d_temple_du_cycle', "Temple du Cycle > ")

    if choix == 0:
        joueur.alignement += 1
        joueur.pv = min(joueur.pv_max, joueur.pv + 4)
        dire(ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_response_1')
    elif choix == 1:
        secret(joueur, ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_secret_1')
        joueur.variables["secret_arthen"] += 1
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_response_2')
    else:
        joueur.tension_fragment += 1
        consequence(joueur, ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_consequence_1')
        dire(ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_response_3')
    journal(joueur, ACT_1_OUTCOMES, 'scene_7d_temple_du_cycle_journal_1')

def scene_7e_forum_des_heures(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_7e_forum_des_heures'])
    choix = choisir(ACT_1_CHOICES, 'scene_7e_forum_des_heures', "Forum des Heures > ")

    if choix == 0:
        joueur.variables["piece_hors_du_temps"] = True
        ajouter_trait_route(joueur, "Marchand des heures")
        item(joueur, "Pièce hors du temps")
        dire(ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_response_1')
    elif choix == 1:
        joueur.tension_fragment += 1
        reve(joueur, ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_dream_1')
        dire(ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_response_2')
    else:
        joueur.variables["morvayn_a_traverse_val_therys"] = True
        ajouter_trait_route(joueur, "Piste de Morvayn")
        secret(joueur, ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_secret_1')
        quete(joueur, ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_quest_1')
        dire(ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_response_3')
    journal(joueur, ACT_1_OUTCOMES, 'scene_7e_forum_des_heures_journal_1')
def explorer_val_therys(joueur):
    scene_7_val_therys(joueur)
    lieux = [
        ("Quartier des Nobles", scene_7a_quartier_des_nobles),
        ("Bibliothèque Engloutie", scene_7b_bibliotheque_engloutie),
        ("Temple du Cycle", scene_7d_temple_du_cycle),
        ("Forum des Heures", scene_7e_forum_des_heures),
    ]
    visites = set()
    while len(visites) < 3:
        options = [nom for nom, _scene in lieux if nom not in visites]
        print("\nVal-Therys : lieux accessibles")
        afficher_options(options)
        choix = demander_choix("Explorer > ", options)
        nom_lieu = options[choix]
        visites.add(nom_lieu)
        for nom, scene in lieux:
            if nom == nom_lieu:
                scene(joueur)
                break

    dire(ACT_1_OUTCOMES, 'explorer_val_therys_response_1')
    return retry_scene(scene_7c_catacombes, joueur, ecran_game_over)


def scene_8_gardien_horloge(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_8_gardien_horloge'])
    secret(joueur, ACT_1_OUTCOMES, 'scene_8_gardien_horloge_secret_1')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_8_gardien_horloge_consequence_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_8_gardien_horloge_journal_1')
    soin = max(0, joueur.pv_max - joueur.pv)
    if soin:
        joueur.pv = joueur.pv_max
        raconter(f"L'Horloge du Premier Âge inverse quelques blessures récentes. Vous récupérez {soin} PV.")
    if story_state.fragment_sous_pression(joueur):
        joueur.tension_fragment = max(0, joueur.tension_fragment - 2)
        dire(ACT_1_OUTCOMES, 'scene_8_gardien_horloge_response_1')


def scene_9_chasseurs_malakar(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_9_chasseurs_malakar'])
    ennemi = {
        "nom": "Morvayn le Porte-Cendre",
        "pv": 22,
        "force": 7,
        "agilite": 5,
        "armure": 3,
        "arme": 4,
        "xp": XP_ENNEMIS["Lieutenant de Malakar"],
        "or": 18,
    }
    if story_state.morvayn_respecte_le_joueur(joueur):
        ennemi["agilite"] -= 1
        dire(ACT_1_OUTCOMES, 'scene_9_chasseurs_malakar_response_1')
    victoire = lancer_combat(joueur, ennemi)
    if victoire:
        secret(joueur, ACT_1_OUTCOMES, 'scene_9_chasseurs_malakar_secret_1')
        consequence(joueur, ACT_1_OUTCOMES, 'scene_9_chasseurs_malakar_consequence_1')
        journal(joueur, ACT_1_OUTCOMES, 'scene_9_chasseurs_malakar_journal_1')
        dire(ACT_1_OUTCOMES, 'scene_9_chasseurs_malakar_response_2')
    return victoire


def scene_10_sanctuaire_oublie(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_10_sanctuaire_oublie'])

    # [AMÉLIORATION NARRATIVE] Résonance Temporelle
    resonance_temporelle(joueur, "Une citadelle noire s'effondre sous un soleil pourpre tandis que des cris de dédain résonnent.")

    if story_state.fragment_instable(joueur):
        migraine = min(joueur.pv - 1, 3)
        joueur.pv -= migraine
        raconter(f"Trop de visions du Fragment se superposent d'un coup. Une migraine violente vous coûte {migraine} PV avant que la salle ne cesse de tourner.")
    quete(joueur, ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_quest_1')
    choix = choisir(ACT_1_CHOICES, 'scene_10_sanctuaire_oublie', "Dans le sanctuaire > ")

    if choix == 0:
        secret(joueur, ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_secret_1')
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_response_1')
    elif choix == 1:
        secret(joueur, ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_secret_2')
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_response_2')
    else:
        secret(joueur, ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_secret_3')
        joueur.connaissance_temporelle += 1
        dire(ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_response_3')
        journal(joueur, ACT_1_OUTCOMES, 'scene_10_sanctuaire_oublie_journal_1')
def scene_11_verite_incomplete(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_11_verite_incomplete'])
    quete(joueur, ACT_1_OUTCOMES, 'scene_11_verite_incomplete_quest_1')
    secret(joueur, ACT_1_OUTCOMES, 'scene_11_verite_incomplete_secret_1')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_11_verite_incomplete_consequence_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_11_verite_incomplete_journal_1')
    if story_state.comprend_arthen(joueur):
        secret(joueur, ACT_1_OUTCOMES, 'scene_11_verite_incomplete_secret_2')
        dire(ACT_1_OUTCOMES, 'scene_11_verite_incomplete_response_1')

def scene_12_fin_acte_1(joueur):
    raconter(ACT_1_SCENE_TEXTS['scene_12_fin_acte_1'])
    voie = story_state.voie_alignement(joueur)
    if voie == "lumiere":
        dire(ACT_1_OUTCOMES, 'scene_12_fin_acte_1_response_1')
    elif voie == "ombre":
        dire(ACT_1_OUTCOMES, 'scene_12_fin_acte_1_response_4')
    else:
        dire(ACT_1_OUTCOMES, 'scene_12_fin_acte_1_response_5')
    faction_dominante = story_state.faction_dominante(joueur)
    if faction_dominante:
        raconter(f"Déjà, des rumeurs sur Arthen remontent jusqu'à {faction_dominante}, qui se demande si cette légende naissante lui sera utile... ou dangereuse.")

    if story_state.morvayn_respecte_le_joueur(joueur):
        dire(ACT_1_OUTCOMES, 'scene_12_fin_acte_1_response_2')
    else:
        dire(ACT_1_OUTCOMES, 'scene_12_fin_acte_1_response_3')
    joueur.acte_courant = "Acte II - Les Royaumes Déchirés"
    reve(joueur, ACT_1_OUTCOMES, 'scene_12_fin_acte_1_dream_1')
    consequence(joueur, ACT_1_OUTCOMES, 'scene_12_fin_acte_1_consequence_1')
    journal(joueur, ACT_1_OUTCOMES, 'scene_12_fin_acte_1_journal_1')
    afficher_bilan_acte_1(joueur)


def afficher_bilan_acte_1(joueur):
    afficher_bilan_acte(joueur, "ACTE I - L'ÉVEIL")
    print("\n" + "=" * 60)
    print("BILAN DE L'ACTE I - L'ÉVEIL")
    print("=" * 60)
    print(f"Niveau atteint : {joueur.niveau} | PV {joueur.pv}/{joueur.pv_max} | Or {joueur.or_poches}g")
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


def jouer_acte_1(joueur):
    # Point de reprise le plus ancien : évite qu'une mort précoce n'efface la création du personnage.
    sauvegarder(joueur)
    scene_2a_les_premiers_cris(joueur)
    transition(ACT_1_OUTCOMES, 'transition_2a_to_2b')
    scene_2b_chercher_mira(joueur)
    transition(ACT_1_OUTCOMES, 'transition_2b_to_2c')
    scene_2c_place_en_flammes(joueur)
    transition(ACT_1_OUTCOMES, 'transition_2c_to_2d')
    if not retry_scene(scene_2d_premier_sang, joueur, ecran_game_over):
        return
    transition(ACT_1_OUTCOMES, 'transition_2d_to_2e')
    scene_2e_morvayn_sur_la_place(joueur)
    transition(ACT_1_OUTCOMES, 'transition_2e_to_3')
    scene_3_la_fuite(joueur)
    transition(ACT_1_OUTCOMES, 'transition_3_to_4')
    lancer_evenement_aleatoire(joueur)
    scene_4_grande_route(joueur)
    transition(ACT_1_OUTCOMES, 'transition_4_to_4a')
    scene_4a_campement_apres_brumebois(joueur)
    transition(ACT_1_OUTCOMES, 'transition_4a_to_5')
    if not retry_scene(scene_5_pont_des_corbeaux, joueur, ecran_game_over):
        return
    transition(ACT_1_OUTCOMES, 'transition_5_to_6')
    scene_6_lyra(joueur)
    transition(ACT_1_OUTCOMES, 'transition_6_to_6a')
    scene_6a_campement_avec_lyra(joueur)
    sauvegarder(joueur)
    transition(ACT_1_OUTCOMES, 'transition_6a_to_7')
    if not explorer_val_therys(joueur):
        return
    transition(ACT_1_OUTCOMES, 'transition_7_to_8')
    scene_8_gardien_horloge(joueur)
    transition(ACT_1_OUTCOMES, 'transition_8_to_9')
    if not retry_scene(scene_9_chasseurs_malakar, joueur, ecran_game_over):
        return
    transition(ACT_1_OUTCOMES, 'transition_9_to_10')
    scene_10_sanctuaire_oublie(joueur)
    transition(ACT_1_OUTCOMES, 'transition_10_to_11')
    scene_11_verite_incomplete(joueur)
    transition(ACT_1_OUTCOMES, 'transition_11_to_12')
    scene_12_fin_acte_1(joueur)

def jouer(joueur=None, sauvegarder=True):
    if joueur is None:
        from elderia.core.io import afficher_titre

        afficher_titre()
        afficher_prologue()
        afficher_structure_campagne()
        joueur = creer_personnage()
        joueur.afficher_fiche_personnage()
    joueur.acte_courant = "Acte I - L'Éveil"
    scene_1a_vie_quotidienne(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1a_to_1b')
    scene_1b_atelier_garrick(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1b_to_1c')
    scene_1c_maison_de_mira(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1c_to_1d')
    scene_1d_jeux_du_festival(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1d_to_1e')
    scene_1e_veillee_des_anciens(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1e_to_1f')
    scene_1f_travaux_et_marche(joueur)
    transition(ACT_1_OUTCOMES, 'transition_1f_to_chapitre_1')
    chapitre_1(joueur)
    transition(ACT_1_OUTCOMES, 'transition_chapitre_1_to_2a')
    jouer_acte_1(joueur)
    if sauvegarder and joueur.pv > 0:
        sauvegarder_partie(joueur)
    return joueur
