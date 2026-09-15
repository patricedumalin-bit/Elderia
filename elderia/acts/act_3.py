from elderia.content.act_3_choices import ACT_3_CHOICES
from elderia.content.act_3_scenes import ACT_3_SCENE_TEXTS
from elderia.core import story_state
from elderia.core.combat import creer_ennemi, lancer_combat, lancer_combat_vague
from elderia.core.codex import ajouter_souvenir, decouvrir_codex
from elderia.core.ending_variants import normaliser_trait
from elderia.core.gameplay import interaction_compagnons, interjection_compagnon, ravitaillement, repos_de_camp
from elderia.core.io import illustrer, raconter
from elderia.core.meta_progression import actualiser_reves_dynamiques
from elderia.core.narrative_state import afficher_bilan_acte, ajouter_trait_route
from elderia.core.scene_engine import choisir, consequence, dire, fin_prematuree, journal, obtenir_cristal, recruter, resonance_temporelle, secret, transition
from elderia.core.systems import MARCHAND_STOCK_ACTE_3, tester_stat, visiter_marchand
from elderia.core.procedural import lancer_evenement_aleatoire
from elderia.core.tome import XP_TOME_2, valider_quete
from elderia.core.runtime import charger_ou_preparer, sauvegarder_fin_acte
from elderia.content.act_3_outcomes import ACT_3_OUTCOMES


def scene_21_route_du_nord(joueur):
    illustrer("assets/images/backgrounds/S05_act_transition.png")
    raconter(ACT_3_SCENE_TEXTS['scene_21_route_du_nord'])

    # [NARRATIF] Interjection
    interjection_compagnon(joueur, "Borin", "Le vent du nord charrie l'odeur du fer et de la cendre... Les miens ne sont plus très loin.")

    if story_state.garrick_est_localise(joueur):
        dire(ACT_3_OUTCOMES, 'story_state_garrick_localise_response_1')
    choix = choisir(ACT_3_CHOICES, 'scene_21_route_du_nord', "Route du nord > ")

    if choix == 0:
        joueur.tension_fragment += 2
        secret(joueur, ACT_3_OUTCOMES, 'scene_21_route_du_nord_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_21_route_du_nord_response_1')
    else:
        joueur.modifier_faction(joueur.allie_politique, 10)
        joueur.ajouter_consequence(f"{joueur.allie_politique} engage officiellement des ressources dans la Chasse aux Cristaux.")
        raconter(f"Votre alliance avec {joueur.allie_politique} ouvre routes, escortes et dettes politiques.")
        if "Borin" in joueur.compagnons:
            joueur.modifier_faction("Royaumes Nains", 10)
            dire(ACT_3_OUTCOMES, 'scene_21_route_du_nord_response_2')
        else:
            joueur.modifier_faction("Royaumes Nains", -5)
            dire(ACT_3_OUTCOMES, 'scene_21_route_du_nord_response_3')

    valider_quete(joueur, "Atteindre les Montagnes d'Ashkar")
    journal(joueur, ACT_3_OUTCOMES, 'scene_21_route_du_nord_journal_1')


def scene_21a_col_des_morsures(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_21a_col_des_morsures'])
    choix = choisir(ACT_3_CHOICES, 'scene_21a_col_des_morsures', "Col des Morsures > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.modifier_faction("Royaumes Nains", 5)
        consequence(joueur, ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_response_1')
    elif choix == 1:
        secret(joueur, ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_secret_1')
        joueur.variables["secret_morvayn"] += 1
        dire(ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_response_2')
    elif choix == 2:
        joueur.energie = max(0, joueur.energie - 2)
        joueur.variables["morvayn_alerte"] = False
        dire(ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_response_3')
    else:
        joueur.diplomatie = getattr(joueur, "diplomatie", 0) + 1
        joueur.modifier_faction("Royaumes Nains", 5)
        dire(ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_response_4')

    journal(joueur, ACT_3_OUTCOMES, 'scene_21a_col_des_morsures_journal_1')


def scene_21b_camp_des_lanternes_froides(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_21b_camp_des_lanternes_froides'])
    ajouter_souvenir(joueur, "lampe_ashkar")
    if story_state.morvayn_est_tue(joueur):
        raconter("Garrick remarque votre silence quand le nom de Morvayn traverse le feu. 'Tuer un homme ne tue jamais toutes ses questions.'")
    elif story_state.morvayn_est_epargne(joueur):
        raconter("Lyra ne juge pas votre choix d'avoir épargné Morvayn. Elle demande seulement : 'S'il revient, tu espères quoi ?' Aucune réponse ne vient vite.")
    elif story_state.morvayn_est_recrute(joueur):
        raconter("Une marque de cendre apparaît brièvement dans la flamme. Morvayn n'est pas là, mais son avertissement trouve quand même le camp.")
    choix = choisir(ACT_3_CHOICES, 'scene_21b_camp_des_lanternes_froides', "Camp des lanternes > ")

    if choix == 0:
        joueur.loyautes["Lyra"] += 5
        dire(ACT_3_OUTCOMES, 'scene_21b_camp_response_1')
    elif choix == 1:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        dire(ACT_3_OUTCOMES, 'scene_21b_camp_response_2')
    else:
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment += 1
        secret(joueur, ACT_3_OUTCOMES, 'scene_21b_camp_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_21b_camp_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_21b_camp_journal_1')


def scene_22a_approche_de_la_forteresse(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_22a_approche_de_la_forteresse'])
    choix = choisir(ACT_3_CHOICES, 'scene_22a_approche_de_la_forteresse', "Approche de Fort-Nord > ")

    if choix == 0:
        joueur.reputation += 1
        consequence(joueur, ACT_3_OUTCOMES, 'scene_22a_approche_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_22a_approche_response_1')
    else:
        if "Borin" in joueur.compagnons:
            joueur.modifier_faction("Royaumes Nains", 10)
        else:
            joueur.tension_fragment += 1
        dire(ACT_3_OUTCOMES, 'scene_22a_approche_response_2')
        if "Œil d'Aeternis" in joueur.artefacts and joueur.pm >= 2:
            joueur.pm -= 2
        else:
            joueur.tension_fragment += 1
        dire(ACT_3_OUTCOMES, 'scene_22a_approche_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_22a_approche_journal_1')


def scene_22_forteresse_de_givre(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_22_forteresse_de_givre'])
    choix = choisir(ACT_3_CHOICES, 'scene_22_forteresse_de_givre', "Garrick > ")

    if choix == 0:
        joueur.reputation += 2
        consequence(joueur, ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_response_1')
    elif choix == 1:
        joueur.variables["garrick_verite_exigee_avant_pardon"] = True
        ajouter_trait_route(joueur, "Vérité avant pardon")
        secret(joueur, ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_secret_1')
        consequence(joueur, ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_consequence_2')
        dire(ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_response_2')
    else:
        joueur.tension_fragment += 1
        secret(joueur, ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_secret_2')
        dire(ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_response_3')
    recruter(joueur, "Garrick")
    joueur.variables["garrick_sauve"] = True
    consequence(joueur, ACT_3_OUTCOMES, 'story_state_garrick_sauve_consequence_1')
    valider_quete(joueur, "Retrouver Garrick")
    journal(joueur, ACT_3_OUTCOMES, 'scene_22_forteresse_de_givre_journal_1')


def scene_22b_verite_de_garrick(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_22b_verite_de_garrick'])
    traits = {normaliser_trait(trait) for trait in joueur.traits_route}
    if normaliser_trait("Doute sur Garrick") in traits:
        raconter("Les paroles de Morvayn reviennent avant celles de Garrick. Ce n'est plus seulement une confession que vous attendez : c'est la preuve que votre enfance n'a pas été bâtie sur un mensonge utile.")
    if normaliser_trait("Ombre argentée") in traits:
        raconter("Le souvenir du dragon d'argent traverse votre esprit quand Garrick évite votre regard. Il y a des vérités que même lui semble craindre de nommer devant le Cristal.")
    choix = choisir(ACT_3_CHOICES, 'scene_22b_verite_de_garrick', "Vérité de Garrick > ")

    if choix == 0:
        joueur.variables["secret_arthen"] += 1
        secret(joueur, ACT_3_OUTCOMES, 'scene_22b_verite_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_22b_verite_response_1')
    elif choix == 1:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 15
        consequence(joueur, ACT_3_OUTCOMES, 'scene_22b_verite_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_22b_verite_response_2')
    else:
        joueur.tension_fragment += 1
        dire(ACT_3_OUTCOMES, 'scene_22b_verite_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_22b_verite_journal_1')


def scene_23_gardien_du_cristal(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23_gardien_du_cristal'])
    decouvrir_codex(joueur, "cristal_vie")
    victoire = lancer_combat(joueur, {
        "nom": "Gardien du Cristal",
        "pv": 58,
        "force": 13,
        "agilite": 6,
        "armure": 7,
        "arme": 7,
        "xp": XP_TOME_2["Gardien du Cristal"],
        "or": 0,
    })
    if victoire:
        obtenir_cristal(joueur, "Cristal de Vie")
        valider_quete(joueur, "Obtenir le Cristal de Vie")
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23_gardien_du_cristal_consequence_1')
        journal(joueur, ACT_3_OUTCOMES, 'scene_23_gardien_du_cristal_journal_1')
    return victoire


def scene_23a_prix_du_cristal_de_vie(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23a_prix_du_cristal_de_vie'])
    choix = choisir(ACT_3_CHOICES, 'scene_23a_prix_du_cristal_de_vie', "Prix du Cristal > ")

    if choix == 0:
        joueur.tension_fragment += 2
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23a_prix_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_23a_prix_response_1')
    elif choix == 1:
        joueur.modifier_faction("Royaumes Nains", 10)
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23a_prix_consequence_2')
        dire(ACT_3_OUTCOMES, 'scene_23a_prix_response_2')
    elif choix == 2:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        joueur.connaissance_temporelle += 1
        dire(ACT_3_OUTCOMES, 'scene_23a_prix_response_3')
    else:
        joueur.modifier_faction("Royaumes Nains", 5)
        joueur.reputation += 1
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23a_prix_consequence_3')
        dire(ACT_3_OUTCOMES, 'scene_23a_prix_response_4')

    journal(joueur, ACT_3_OUTCOMES, 'scene_23a_prix_journal_1')


def scene_23b_conseil_ashkar(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23b_conseil_ashkar'])
    if story_state.a_choisi_alliance(joueur):
        raconter(f"Votre alliance avec {joueur.allie_politique} pèse déjà sur la carte : certains chemins sont plus ouverts, d'autres plus surveillés.")
    if story_state.elara_est_sauvee(joueur):
        raconter("Les notes d'Elara ajoutent une hypothèse que Garrick n'aime pas : certains Cristaux ne veulent peut-être pas être retrouvés.")
        joueur.connaissance_temporelle += 1
    if tester_stat(joueur, "charisme", 15):
        joueur.modifier_faction("Royaumes Nains", 5)
        raconter("Votre présence convainc plusieurs voix hésitantes du conseil d'Ashkar.")
    choix = choisir(ACT_3_CHOICES, 'scene_23b_conseil_ashkar', "Conseil d'Ashkar > ")

    if choix == 0:
        joueur.modifier_faction(joueur.allie_politique or "Aldor", 5)
        dire(ACT_3_OUTCOMES, 'scene_23b_conseil_response_1')
    elif choix == 1:
        joueur.variables["morvayn_alerte"] = False
        dire(ACT_3_OUTCOMES, 'scene_23b_conseil_response_2')
    else:
        joueur.variables["secret_arthen"] += 1
        joueur.connaissance_temporelle += 1
        dire(ACT_3_OUTCOMES, 'scene_23b_conseil_response_3')
        if recruter(joueur, "Selene"):
            raconter("Une femme encapuchonnée s'attarde après le conseil. \"Selene\", dit-elle. \"Ce que vous cherchez dans les archives d'Arthen touche à quelque chose que j'étudie depuis longtemps : le Dévoreur des Âges. Je viens avec vous.\"")

    journal(joueur, ACT_3_OUTCOMES, 'scene_23b_conseil_journal_1')


def scene_23c_cicatrice_ashkar(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23c_cicatrice_ashkar'])
    decouvrir_codex(joueur, "ashkar")
    ajouter_souvenir(joueur, "cicatrice_ashkar")
    choix = choisir(ACT_3_CHOICES, 'scene_23c_cicatrice_ashkar', "Cicatrice d'Ashkar > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.modifier_faction("Royaumes Nains", 10)
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_response_1')
    else:
        joueur.modifier_faction("Royaumes Nains", 5)
        joueur.variables["garrick_sauve"] = True
        dire(ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_response_2')
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment += 1
        secret(joueur, ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_23c_cicatrice_ashkar_journal_1')


def scene_23d_heritage_de_garrick(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23d_heritage_de_garrick'])
    decouvrir_codex(joueur, "veilleurs")
    traits = {normaliser_trait(trait) for trait in joueur.traits_route}
    if normaliser_trait("Vérité avant pardon") in traits:
        raconter("Cette fois, Garrick ne peut plus se cacher derrière l'urgence. Vous avez déjà choisi que l'amour ne suffirait pas à remplacer une réponse.")
    if normaliser_trait("Gardien des lettres") in traits:
        raconter("Les lettres conservées contre votre armure rendent chaque phrase de Garrick plus difficile à croire et plus nécessaire à entendre.")
    choix = choisir(ACT_3_CHOICES, 'scene_23d_heritage_de_garrick', "Héritage de Garrick > ")

    if choix == 0:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        consequence(joueur, ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_consequence_1')
        dire(ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_response_1')
    elif choix == 1:
        joueur.variables["secret_malakar"] += 1
        joueur.variables["secret_morvayn"] += 1
        secret(joueur, ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_response_2')
    else:
        joueur.connaissance_temporelle += 1
        joueur.respect_morvayn += 1
        dire(ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_23d_heritage_de_garrick_journal_1')


def scene_23e_serment_des_compagnons(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_23e_serment_des_compagnons'])
    dialogue = interaction_compagnons(joueur)
    if dialogue:
        raconter(dialogue)
    choix = choisir(ACT_3_CHOICES, 'scene_23e_serment_des_compagnons', "Serment des compagnons > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 5
        dire(ACT_3_OUTCOMES, 'scene_23e_serment_des_compagnons_response_1')
    elif choix == 1:
        joueur.variables["compagnons_garde_fou"] = True
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        dire(ACT_3_OUTCOMES, 'scene_23e_serment_des_compagnons_response_2')
    elif choix == 2:
        joueur.tension_fragment += 1
        joueur.variables["poids_solitaire_cristaux"] = True
        dire(ACT_3_OUTCOMES, 'scene_23e_serment_des_compagnons_response_3')
    else:
        fin_prematuree(joueur, ACT_3_OUTCOMES, 'ending_premature_ashkar', "Fin d'Ashkar Préservée")
        return

    consequence(joueur, ACT_3_OUTCOMES, 'scene_23e_serment_des_compagnons_consequence_1')
    journal(joueur, ACT_3_OUTCOMES, 'scene_23e_serment_des_compagnons_journal_1')


def scene_24_routes_des_cristaux(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24_routes_des_cristaux'])
    decouvrir_codex(joueur, "cristaux")
    choix = choisir(ACT_3_CHOICES, 'scene_24_routes_des_cristaux', "Prochaine chasse > ")

    cristal = ["Cristal des Ombres", "Cristal des Esprits", "Cristal des Marées"][choix]
    joueur.variables["cristal_prioritaire"] = cristal
    actualiser_reves_dynamiques(joueur)
    joueur.tension_fragment += choix + 1
    consequence(joueur, ACT_3_OUTCOMES, f'scene_24_routes_consequence_{choix + 1}')
    joueur.journal.append(f"Vous choisissez de poursuivre {cristal}, acceptant de ne pas pouvoir tout sauver.")


def scene_24b_resonance_cristal_choisi(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24b_resonance_cristal_choisi'])
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    raconter(f"Le {cristal} module la vision : ce n'est pas la même peur qui vous appelle, mais elle connaît déjà la forme de votre marque.")
    choix = choisir(ACT_3_CHOICES, 'scene_24b_resonance_cristal_choisi', "Résonance du Cristal > ")

    if choix == 0:
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_3_OUTCOMES, 'scene_24b_resonance_cristal_choisi_response_1')
    elif choix == 1:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        joueur.connaissance_temporelle += 1
        dire(ACT_3_OUTCOMES, 'scene_24b_resonance_cristal_choisi_response_2')
    else:
        joueur.tension_fragment += 2
        joueur.fragments_temps = min(25, joueur.fragments_temps + 1)
        secret(joueur, ACT_3_OUTCOMES, 'scene_24b_resonance_cristal_choisi_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_24b_resonance_cristal_choisi_response_3')

    journal(joueur, ACT_3_OUTCOMES, 'scene_24b_resonance_cristal_choisi_journal_1')


def scene_24d_route_du_cristal_choisi(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24d_route_du_cristal_choisi'])
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    raconter(f"Le {cristal} colore chaque signe : même vos compagnons commencent à parler plus bas lorsqu'il répond au Cristal de Vie.")
    choix = choisir(ACT_3_CHOICES, 'scene_24d_route_du_cristal_choisi', "Route du Cristal choisi > ")

    if choix == 0:
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_3_OUTCOMES, 'scene_24d_route_du_cristal_choisi_response_1')
    elif choix == 1:
        joueur.espionnage = getattr(joueur, "espionnage", 0) + 1
        joueur.variables["manifestations_cristal_cachees"] = True
        dire(ACT_3_OUTCOMES, 'scene_24d_route_du_cristal_choisi_response_2')
    else:
        joueur.tension_fragment += 1
        joueur.fragments_temps = min(25, joueur.fragments_temps + 1)
        dire(ACT_3_OUTCOMES, 'scene_24d_route_du_cristal_choisi_response_3')

    secret(joueur, ACT_3_OUTCOMES, 'scene_24d_route_du_cristal_choisi_secret_1')
    journal(joueur, ACT_3_OUTCOMES, 'scene_24d_route_du_cristal_choisi_journal_1')


def scene_24d1_chasseurs_du_cristal(joueur):
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    raconter(f"\nLa route vers le {cristal} attire aussi ceux qui ont appris à suivre votre marque. Des chasseurs des Cendres surgissent avant l'épreuve, non pour vous tuer, mais pour mesurer ce que deux Cristaux font déjà de vous.")
    return lancer_combat_vague(joueur, [
        creer_ennemi("Chasseur du Cristal", nom=f"Chasseur du {cristal}")
        for _ in range(2)
    ])


def scene_24a_epreuve_second_cristal(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24a_epreuve_second_cristal'])
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    raconter(f"Le {cristal} vous attend au bout de cette épreuve, mais il refuse d'être réduit à une destination.")
    choix = choisir(ACT_3_CHOICES, 'scene_24a_epreuve_second_cristal', "Épreuve du second Cristal > ")

    if choix == 0:
        joueur.reputation += 2
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_3_OUTCOMES, 'scene_24a_epreuve_response_1')
    elif choix == 1:
        joueur.tension_fragment += 3
        joueur.fragments_temps = min(25, joueur.fragments_temps + 1)
        dire(ACT_3_OUTCOMES, 'scene_24a_epreuve_response_2')
    else:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        dire(ACT_3_OUTCOMES, 'scene_24a_epreuve_response_3')

    victoire = lancer_combat(joueur, {
        "nom": f"Sentinelle du {cristal}",
        "pv": 64,
        "force": 14,
        "agilite": 7,
        "armure": 7,
        "arme": 7,
        "xp": XP_TOME_2["Gardien du Cristal"],
        "or": 0,
    })
    if victoire:
        obtenir_cristal(joueur, cristal)
        consequence(joueur, ACT_3_OUTCOMES, 'scene_24a_epreuve_consequence_1')
        journal(joueur, ACT_3_OUTCOMES, 'scene_24a_epreuve_journal_1')
        joueur.acte_courant = "Acte IV - La Guerre du Crépuscule"
    return victoire


def scene_24e_perte_avant_la_guerre(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24e_perte_avant_la_guerre'])
    choix = choisir(ACT_3_CHOICES, 'scene_24e_perte_avant_la_guerre', "Perte avant la guerre > ")

    if choix == 0:
        joueur.reputation += 1
        joueur.diplomatie = getattr(joueur, "diplomatie", 0) + 1
        dire(ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_response_1')
    elif choix == 1:
        joueur.armee = getattr(joueur, "armee", 0) + 1
        joueur.variables["malakar_poursuivi_avant_guerre"] = True
        dire(ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_response_2')
    elif choix == 2:
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment += 1
        joueur.variables["marque_malakar_etudiee"] = True
        dire(ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_response_3')
    else:
        joueur.espionnage = getattr(joueur, "espionnage", 0) + 1
        joueur.variables["lyra_eclaireuse_malakar"] = True
        secret(joueur, ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_secret_1')
        dire(ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_response_4')

    consequence(joueur, ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_consequence_1')
    journal(joueur, ACT_3_OUTCOMES, 'scene_24e_perte_avant_la_guerre_journal_1')


def scene_24c_presage_de_guerre(joueur):
    raconter(ACT_3_SCENE_TEXTS['scene_24c_presage_de_guerre'])
    choix = choisir(ACT_3_CHOICES, 'scene_24c_presage_de_guerre', "Présage de guerre > ")

    if choix == 0:
        ajouter_allie = joueur.allie_politique or "Aldor"
        joueur.modifier_faction(ajouter_allie, 10)
        joueur.armee = getattr(joueur, "armee", 0) + 1
        dire(ACT_3_OUTCOMES, 'scene_24c_presage_de_guerre_response_1')
    elif choix == 1:
        joueur.espionnage = getattr(joueur, "espionnage", 0) + 2
        joueur.variables["morvayn_alerte"] = False
        dire(ACT_3_OUTCOMES, 'scene_24c_presage_de_guerre_response_2')
    else:
        joueur.diplomatie = getattr(joueur, "diplomatie", 0) + 2
        joueur.reputation += 1
        dire(ACT_3_OUTCOMES, 'scene_24c_presage_de_guerre_response_3')

    consequence(joueur, ACT_3_OUTCOMES, 'scene_24c_presage_de_guerre_consequence_1')
    journal(joueur, ACT_3_OUTCOMES, 'scene_24c_presage_de_guerre_journal_1')
    joueur.acte_courant = "Acte IV - La Guerre du Crépuscule"
    afficher_bilan_acte(joueur, "ACTE III - LA CHASSE AUX CRISTAUX")


def jouer_acte_3(joueur):
    scene_21_route_du_nord(joueur)
    transition(ACT_3_OUTCOMES, 'transition_21_to_21a')
    lancer_evenement_aleatoire(joueur)
    scene_21a_col_des_morsures(joueur)
    transition(ACT_3_OUTCOMES, 'transition_21a_to_21b')
    scene_21b_camp_des_lanternes_froides(joueur)
    repos_de_camp(joueur, "Camp des Lanternes froides")
    transition(ACT_3_OUTCOMES, 'transition_21b_to_22a')
    scene_22a_approche_de_la_forteresse(joueur)
    transition(ACT_3_OUTCOMES, 'transition_22a_to_22')
    scene_22_forteresse_de_givre(joueur)
    transition(ACT_3_OUTCOMES, 'transition_22_to_22b')
    scene_22b_verite_de_garrick(joueur)
    transition(ACT_3_OUTCOMES, 'transition_22b_to_23')
    if not scene_23_gardien_du_cristal(joueur):
        return
    transition(ACT_3_OUTCOMES, 'transition_23_to_23a')
    scene_23a_prix_du_cristal_de_vie(joueur)
    transition(ACT_3_OUTCOMES, 'transition_23a_to_23b')
    scene_23b_conseil_ashkar(joueur)
    transition(ACT_3_OUTCOMES, 'transition_23b_to_23c')
    scene_23c_cicatrice_ashkar(joueur)
    ravitaillement(joueur, "Forge basse d'Ashkar")
    visiter_marchand(joueur, MARCHAND_STOCK_ACTE_3, "\nLes forgerons nains d'Ashkar proposent leurs meilleures pièces.", palier="elite")
    transition(ACT_3_OUTCOMES, 'transition_23c_to_23d')
    scene_23d_heritage_de_garrick(joueur)
    transition(ACT_3_OUTCOMES, 'transition_23d_to_23e')
    scene_23e_serment_des_compagnons(joueur)
    if joueur.acte_courant == "Épilogue":
        return
    transition(ACT_3_OUTCOMES, 'transition_23e_to_24')
    scene_24_routes_des_cristaux(joueur)
    transition(ACT_3_OUTCOMES, 'transition_24_to_24b')
    scene_24b_resonance_cristal_choisi(joueur)
    transition(ACT_3_OUTCOMES, 'transition_24b_to_24d')
    scene_24d_route_du_cristal_choisi(joueur)
    if not scene_24d1_chasseurs_du_cristal(joueur):
        return
    transition(ACT_3_OUTCOMES, 'transition_24d_to_24a')
    if not scene_24a_epreuve_second_cristal(joueur):
        return
    transition(ACT_3_OUTCOMES, 'transition_24a_to_24e')
    scene_24e_perte_avant_la_guerre(joueur)
    transition(ACT_3_OUTCOMES, 'transition_24e_to_24c')
    scene_24c_presage_de_guerre(joueur)


def jouer(joueur=None, sauvegarder=True):
    if joueur is None:
        joueur = charger_ou_preparer(3)
    joueur.acte_courant = "Acte III - La Chasse aux Cristaux"
    if joueur.pv > 0:
        jouer_acte_3(joueur)
    if sauvegarder and joueur.pv > 0:
        sauvegarder_fin_acte(joueur)
    return joueur
