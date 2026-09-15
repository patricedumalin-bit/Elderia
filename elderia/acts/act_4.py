from elderia.content.act_4_choices import ACT_4_CHOICES
from elderia.content.act_4_scenes import ACT_4_SCENE_TEXTS
from elderia.core import story_state
from elderia.core.combat import lancer_combat
from elderia.core.codex import ajouter_souvenir
from elderia.core.gameplay import interaction_compagnons, interjection_compagnon, ravitaillement, repos_de_camp
from elderia.core.io import illustrer, raconter
from elderia.core.meta_progression import actualiser_reves_dynamiques
from elderia.core.narrative_state import afficher_bilan_acte, faction_dominante
from elderia.core.scene_engine import choisir, consequence, dire, fin_prematuree, journal, resonance_temporelle, reve, secret, transition
from elderia.core.systems import MARCHAND_STOCK_ACTE_4, tester_stat, visiter_marchand
from elderia.core.procedural import lancer_evenement_aleatoire
from elderia.core.tome import XP_TOME_2, ajouter_score, valider_quete
from elderia.core.runtime import charger_ou_preparer, sauvegarder_fin_acte
from elderia.content.act_4_outcomes import ACT_4_OUTCOMES


def bonus_effort_guerre(joueur):
    """Convertit les scores armée/espionnage/diplomatie accumulés en préparation tactique concrète.
    Le plafond (-20 PV) demande ~40 points cumulés : vu la densité des scènes qui les alimentent,
    un ratio 1 pour 1 (au lieu de x2) évite qu'un seul acte suffise à atteindre le maximum trivialement."""
    effort = joueur.armee + joueur.espionnage + joueur.diplomatie
    reduction_pv = min(20, effort // 2)
    if reduction_pv:
        raconter(f"Vos préparatifs (armée, espionnage, diplomatie) affaiblissent l'ennemi avant même le combat : -{reduction_pv} PV.")
    return reduction_pv


def scene_25_conseil_de_guerre(joueur):
    illustrer("assets/images/backgrounds/S04_combat_arena.png") # Placeholder cité en guerre
    raconter(ACT_4_SCENE_TEXTS['scene_25_conseil_de_guerre'])

    # [NARRATIF] Interjection
    interjection_compagnon(joueur, "Lyra", "Regardez leurs yeux... ils ne voient plus que la victoire, ils ont oublié la paix.")

    if story_state.a_choisi_alliance(joueur):
        raconter(f"Votre alliance avec {joueur.allie_politique} arrive avant vous dans la salle : appuis, rancunes et dettes s'assoient déjà autour de la table.")
    if story_state.garrick_est_sauve(joueur):
        ajouter_score(joueur, "armee", 1)
        dire(ACT_4_OUTCOMES, 'story_state_garrick_sauve_response_1')
    if story_state.ancien_allie_temporel(joueur):
        ajouter_score(joueur, "espionnage", 1)
        dire(ACT_4_OUTCOMES, 'story_state_ancien_allie_response_1')
    if story_state.prisonnier_sans_age_libere(joueur):
        ajouter_score(joueur, "diplomatie", 1)
        dire(ACT_4_OUTCOMES, 'story_state_prisonnier_libere_response_1')
    if story_state.morvayn_est_recrute(joueur):
        ajouter_score(joueur, "espionnage", 2)
        dire(ACT_4_OUTCOMES, 'story_state_morvayn_recrute_response_1')
    elif story_state.morvayn_est_epargne(joueur):
        ajouter_score(joueur, "diplomatie", 1)
        dire(ACT_4_OUTCOMES, 'story_state_morvayn_epargne_response_1')
    elif story_state.morvayn_est_tue(joueur):
        ajouter_score(joueur, "armee", 1)
        dire(ACT_4_OUTCOMES, 'story_state_morvayn_tue_response_1')
    influence_dominante = max(joueur.influences, key=joueur.influences.get)
    if joueur.influences[influence_dominante] > 0:
        if influence_dominante == "Militaire":
            ajouter_score(joueur, "armee", 1)
            raconter("Les officiers reconnaissent en vous une autorité qu'ils ont appris à respecter à Aldorath.")
        elif influence_dominante == "Religieuse":
            ajouter_score(joueur, "diplomatie", 1)
            raconter("Le clergé d'Aldorath a fait circuler votre nom avec une réputation presque sacrée.")
        else:
            ajouter_score(joueur, "espionnage", 1)
            raconter("Vos manœuvres politiques à Aldorath précèdent votre arrivée jusque dans cette salle.")
    choix = choisir(ACT_4_CHOICES, 'scene_25_conseil_de_guerre', "Conseil de guerre > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 3)
        joueur.modifier_faction("Aldor", 10)
        dire(ACT_4_OUTCOMES, 'scene_25_conseil_de_guerre_response_1')
    elif choix == 1:
        ajouter_score(joueur, "espionnage", 3)
        joueur.modifier_faction("Cités Libres", 10)
        dire(ACT_4_OUTCOMES, 'scene_25_conseil_de_guerre_response_2')
    else:
        ajouter_score(joueur, "diplomatie", 3)
        joueur.modifier_faction("Ellorien", 5)
        joueur.modifier_faction("Royaumes Nains", 5)
        dire(ACT_4_OUTCOMES, 'scene_25_conseil_de_guerre_response_3')

    valider_quete(joueur, "Fonder la forteresse du Crépuscule")
    journal(joueur, ACT_4_OUTCOMES, 'scene_25_conseil_de_guerre_journal_1')


def scene_25a_camp_des_refugies(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_25a_camp_des_refugies'])
    choix = choisir(ACT_4_CHOICES, 'scene_25a_camp_des_refugies', "Camp des réfugiés > ")

    if choix == 0:
        joueur.reputation += 2
        ajouter_score(joueur, "diplomatie", 2)
        dire(ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_response_1')
        consequence(joueur, ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_consequence_1')
    elif choix == 1:
        ajouter_score(joueur, "armee", 2)
        joueur.modifier_faction("Aldor", 5)
        dire(ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_response_2')
        consequence(joueur, ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_consequence_2')
    else:
        ajouter_score(joueur, "diplomatie", 1)
        ajouter_score(joueur, "espionnage", 1)
        if joueur.allie_politique:
            joueur.modifier_faction(joueur.allie_politique, 5)
        dire(ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_response_3')
        consequence(joueur, ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_consequence_3')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25a_camp_des_refugies_journal_1')


def scene_25b_forge_des_bannieres(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_25b_forge_des_bannieres'])
    choix = choisir(ACT_4_CHOICES, 'scene_25b_forge_des_bannieres', "Forge des Bannières > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        dire(ACT_4_OUTCOMES, 'scene_25b_forge_des_bannieres_response_1')
    elif choix == 1:
        ajouter_score(joueur, "espionnage", 2)
        dire(ACT_4_OUTCOMES, 'scene_25b_forge_des_bannieres_response_2')
    elif choix == 2:
        ajouter_score(joueur, "diplomatie", 2)
        dire(ACT_4_OUTCOMES, 'scene_25b_forge_des_bannieres_response_3')
    else:
        ajouter_score(joueur, "armee", 1)
        ajouter_score(joueur, "espionnage", 1)
        joueur.variables["forge_bannieres_equilibree"] = True
        dire(ACT_4_OUTCOMES, 'scene_25b_forge_des_bannieres_response_4')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25b_forge_des_bannieres_journal_1')


def scene_25c_cartes_du_crepuscule(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_25c_cartes_du_crepuscule'])
    choix = choisir(ACT_4_CHOICES, 'scene_25c_cartes_du_crepuscule', "Cartes du Crépuscule > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        dire(ACT_4_OUTCOMES, 'scene_25c_cartes_du_crepuscule_response_1')
    else:
        ajouter_score(joueur, "espionnage", 2)
        joueur.tension_fragment += 1
        dire(ACT_4_OUTCOMES, 'scene_25c_cartes_du_crepuscule_response_2')
        ajouter_score(joueur, "diplomatie", 2)
        joueur.reputation += 1
        dire(ACT_4_OUTCOMES, 'scene_25c_cartes_du_crepuscule_response_3')
    secret(joueur, ACT_4_OUTCOMES, 'scene_25c_cartes_du_crepuscule_secret_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25c_cartes_du_crepuscule_journal_1')


def scene_25d_fissures_de_la_coalition(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_25d_fissures_de_la_coalition'])
    if joueur.allie_politique:
        raconter(f"Votre alliance avec {joueur.allie_politique} donne un nom à la faction qui attend le plus de vous, et donc à celle que les autres observent le plus durement.")
    choix = choisir(ACT_4_CHOICES, 'scene_25d_fissures_de_la_coalition', "Fissures de la coalition > ")

    if choix == 0:
        ajouter_score(joueur, "diplomatie", 1)
        ajouter_score(joueur, "armee", 1)
        joueur.modifier_faction(joueur.allie_politique or "Aldor", 10)
        dire(ACT_4_OUTCOMES, 'scene_25d_fissures_de_la_coalition_response_1')
    elif choix == 1:
        ajouter_score(joueur, "armee", 2)
        joueur.reputation += 1
        joueur.variables["coalition_sous_autorite"] = True
        dire(ACT_4_OUTCOMES, 'scene_25d_fissures_de_la_coalition_response_2')
    elif choix == 2:
        ajouter_score(joueur, "diplomatie", 2)
        joueur.modifier_faction("Ellorien", 5)
        joueur.modifier_faction("Royaumes Nains", 5)
        joueur.variables["coalition_entraidee"] = True
        dire(ACT_4_OUTCOMES, 'scene_25d_fissures_de_la_coalition_response_3')
    else:
        fin_prematuree(joueur, ACT_4_OUTCOMES, 'ending_premature_coalition_brisee', "Fin de la Coalition Brisée")
        return

    consequence(joueur, ACT_4_OUTCOMES, 'scene_25d_fissures_de_la_coalition_consequence_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25d_fissures_de_la_coalition_journal_1')


def scene_25f_route_faction(joueur):
    faction = joueur.allie_politique or faction_dominante(joueur)
    scenes = {
        "Aldor": 'scene_25f_route_aldor',
        "Ligue de Varken": 'scene_25f_route_varken',
        "Ellorien": 'scene_25f_route_ellorien',
        "Cités Libres": 'scene_25f_route_cites_libres',
    }
    raconter(ACT_4_SCENE_TEXTS[scenes.get(faction or "", 'scene_25f_route_sans_allie')])

    if faction == "Aldor":
        ajouter_score(joueur, "armee", 1)
        joueur.variables["route_faction_aldor"] = True
        if "Garrick" in joueur.compagnons:
            raconter("\"La couronne se souvient toujours de qui a forgé ses armes\", dit Garrick, à moitié fier, à moitié inquiet de ce que ce lien pourrait vous coûter.")
    elif faction == "Ligue de Varken":
        ajouter_score(joueur, "espionnage", 1)
        joueur.variables["route_faction_varken"] = True
        if "Mira aux Corbeaux" in joueur.compagnons:
            raconter("\"Varken n'oublie jamais une dette\", murmure Mira aux Corbeaux. \"Ni celles qu'on lui doit, ni celles qu'elle nous doit désormais.\"")
    elif faction == "Ellorien":
        ajouter_score(joueur, "diplomatie", 1)
        joueur.variables["route_faction_ellorien"] = True
        if "Lyra" in joueur.compagnons:
            raconter("Lyra reste silencieuse un long moment. \"Mon peuple ne pardonne pas facilement\", finit-elle par dire, \"mais il n'oublie pas non plus ceux qui ont tenu parole.\"")
    elif faction == "Cités Libres":
        ajouter_score(joueur, "espionnage", 1)
        joueur.reputation += 1
        joueur.variables["route_faction_cites_libres"] = True
        if "Borin" in joueur.compagnons:
            raconter("\"Aucune couronne, aucun serment de sang\", approuve Borin. \"Voilà une alliance qu'un prince déchu peut respecter.\"")
    else:
        joueur.variables["route_sans_allie_dominant"] = True

    if tester_stat(joueur, "charisme", 14):
        ajouter_score(joueur, "diplomatie", 1)
        raconter("Votre charisme pèse dans les tractations, quel que soit le camp choisi.")

    dire(ACT_4_OUTCOMES, 'scene_25f_route_faction_response_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25f_route_faction_journal_1')


def scene_25e_trahison_des_bannieres(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_25e_trahison_des_bannieres'])
    choix = choisir(ACT_4_CHOICES, 'scene_25e_trahison_des_bannieres', "Trahison des Bannières > ")

    if choix == 0:
        ajouter_score(joueur, "diplomatie", 1)
        ajouter_score(joueur, "espionnage", 1)
        dire(ACT_4_OUTCOMES, 'scene_25e_trahison_des_bannieres_response_1')
    elif choix == 1:
        ajouter_score(joueur, "armee", 2)
        joueur.reputation_criminelle += 1
        dire(ACT_4_OUTCOMES, 'scene_25e_trahison_des_bannieres_response_2')
    else:
        ajouter_score(joueur, "espionnage", 2)
        joueur.variables["trahison_retournee"] = True
        dire(ACT_4_OUTCOMES, 'scene_25e_trahison_des_bannieres_response_3')

    secret(joueur, ACT_4_OUTCOMES, 'scene_25e_trahison_des_bannieres_secret_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_25e_trahison_des_bannieres_journal_1')


def scene_26_bataille_des_trois_bannieres(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26_bataille_des_trois_bannieres'])
    ajouter_souvenir(joueur, "trois_bannieres")
    choix = choisir(ACT_4_CHOICES, 'scene_26_bataille_des_trois_bannieres', "Bataille > ")

    if choix == 0:
        joueur.reputation += 3
        ajouter_score(joueur, "armee", 1)
        consequence(joueur, ACT_4_OUTCOMES, 'scene_26_bataille_des_trois_bannieres_consequence_1')
    elif choix == 1:
        ajouter_score(joueur, "espionnage", 1)
        consequence(joueur, ACT_4_OUTCOMES, 'scene_26_bataille_des_trois_bannieres_consequence_2')
    else:
        joueur.tension_fragment += 3
        consequence(joueur, ACT_4_OUTCOMES, 'scene_26_bataille_des_trois_bannieres_consequence_3')
    victoire = lancer_combat(joueur, {
        "nom": "Champion de guerre",
        "pv": 80 - bonus_effort_guerre(joueur),
        "force": 17,
        "agilite": 8,
        "armure": 9,
        "arme": 8,
        "xp": XP_TOME_2["Champion de guerre"],
        "or": 30,
    })
    if victoire:
        valider_quete(joueur, "Gagner la bataille des Trois Bannières")
        journal(joueur, ACT_4_OUTCOMES, 'scene_26_bataille_des_trois_bannieres_journal_1')
    return victoire


def scene_26f_revers_des_lignes(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26f_revers_des_lignes'])
    choix = choisir(ACT_4_CHOICES, 'scene_26f_revers_des_lignes', "Revers des lignes > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        dire(ACT_4_OUTCOMES, 'scene_26f_revers_des_lignes_response_1')
    elif choix == 1:
        ajouter_score(joueur, "espionnage", 1)
        ajouter_score(joueur, "diplomatie", 1)
        dire(ACT_4_OUTCOMES, 'scene_26f_revers_des_lignes_response_2')
    else:
        ajouter_score(joueur, "armee", 1)
        ajouter_score(joueur, "espionnage", 1)
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 5
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 5
        dire(ACT_4_OUTCOMES, 'scene_26f_revers_des_lignes_response_3')

    consequence(joueur, ACT_4_OUTCOMES, 'scene_26f_revers_des_lignes_consequence_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26f_revers_des_lignes_journal_1')
    return lancer_combat(joueur, {
        "nom": "Percée des lignes noires",
        "pv": 85 - bonus_effort_guerre(joueur),
        "force": 17,
        "agilite": 8,
        "armure": 8,
        "arme": 8,
        "xp": 340,
        "or": 12,
    })


def scene_26a_breche_du_crepuscule(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26a_breche_du_crepuscule'])
    choix = choisir(ACT_4_CHOICES, 'scene_26a_breche_du_crepuscule', "Brèche du Crépuscule > ")

    if choix == 0:
        joueur.tension_fragment += 2
        ajouter_score(joueur, "armee", 1)
        dire(ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_response_1')
    elif choix == 1:
        joueur.tension_fragment += 1
        ajouter_score(joueur, "espionnage", 2)
        dire(ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_response_2')
    elif choix == 2:
        joueur.reputation += 1
        ajouter_score(joueur, "diplomatie", 2)
        dire(ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_response_3')
    else:
        ajouter_score(joueur, "armee", 1)
        ajouter_score(joueur, "diplomatie", 1)
        joueur.variables["breche_refermee_a_deux"] = True
        dire(ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_response_4')
    reve(joueur, ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_dream_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26a_breche_du_crepuscule_journal_1')


def scene_26c_cristal_sur_le_front(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26c_cristal_sur_le_front'])
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    raconter(f"Le {cristal} répond au Cristal de Vie avec une nuance que les stratèges ne savent pas noter sur leurs cartes.")
    choix = choisir(ACT_4_CHOICES, 'scene_26c_cristal_sur_le_front', "Cristal sur le front > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        joueur.tension_fragment += 1
        dire(ACT_4_OUTCOMES, 'scene_26c_cristal_sur_le_front_response_1')
    elif choix == 1:
        ajouter_score(joueur, "espionnage", 2)
        joueur.variables["cristal_cache_aux_ennemis"] = True
        dire(ACT_4_OUTCOMES, 'scene_26c_cristal_sur_le_front_response_2')
    else:
        ajouter_score(joueur, "diplomatie", 2)
        joueur.connaissance_temporelle += 1
        dire(ACT_4_OUTCOMES, 'scene_26c_cristal_sur_le_front_response_3')

    secret(joueur, ACT_4_OUTCOMES, 'scene_26c_cristal_sur_le_front_secret_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26c_cristal_sur_le_front_journal_1')


def scene_26c1_cristal_prioritaire(joueur):
    cristal = joueur.variables.get("cristal_prioritaire", "Cristal des Ombres")
    if cristal == "Cristal des Esprits":
        raconter(ACT_4_SCENE_TEXTS['scene_26c1_cristal_des_esprits'])
        ajouter_score(joueur, "diplomatie", 1)
        joueur.connaissance_temporelle += 1
        dire(ACT_4_OUTCOMES, 'scene_26c1_cristal_des_esprits_response_1')
        journal(joueur, ACT_4_OUTCOMES, 'scene_26c1_cristal_des_esprits_journal_1')
    elif cristal == "Cristal des Marées":
        raconter(ACT_4_SCENE_TEXTS['scene_26c1_cristal_des_marees'])
        ajouter_score(joueur, "armee", 1)
        joueur.reputation += 1
        dire(ACT_4_OUTCOMES, 'scene_26c1_cristal_des_marees_response_1')
        journal(joueur, ACT_4_OUTCOMES, 'scene_26c1_cristal_des_marees_journal_1')
    else:
        raconter(ACT_4_SCENE_TEXTS['scene_26c1_cristal_des_ombres'])
        ajouter_score(joueur, "espionnage", 2)
        joueur.variables["ombres_sur_le_front"] = True
        dire(ACT_4_OUTCOMES, 'scene_26c1_cristal_des_ombres_response_1')
        journal(joueur, ACT_4_OUTCOMES, 'scene_26c1_cristal_des_ombres_journal_1')


def scene_26d_contre_offensive_malakar(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26d_contre_offensive_malakar'])
    choix = choisir(ACT_4_CHOICES, 'scene_26d_contre_offensive_malakar', "Contre-offensive > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        joueur.reputation += 1
        dire(ACT_4_OUTCOMES, 'scene_26d_contre_offensive_malakar_response_1')
    elif choix == 1:
        ajouter_score(joueur, "diplomatie", 2)
        joueur.modifier_faction("Cités Libres", 5)
        dire(ACT_4_OUTCOMES, 'scene_26d_contre_offensive_malakar_response_2')
    else:
        ajouter_score(joueur, "espionnage", 2)
        joueur.tension_fragment += 2
        dire(ACT_4_OUTCOMES, 'scene_26d_contre_offensive_malakar_response_3')

    victoire = lancer_combat(joueur, {
        "nom": "Avant-garde fracturée de Malakar",
        "pv": 90 - bonus_effort_guerre(joueur),
        "force": 18,
        "agilite": 9,
        "armure": 9,
        "arme": 9,
        "xp": XP_TOME_2["Champion de guerre"],
        "or": 20,
    })
    if victoire:
        consequence(joueur, ACT_4_OUTCOMES, 'scene_26d_contre_offensive_malakar_consequence_1')
        journal(joueur, ACT_4_OUTCOMES, 'scene_26d_contre_offensive_malakar_journal_1')
    return victoire


def scene_26g_cristaux_interdits(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26g_cristaux_interdits'])
    choix = choisir(ACT_4_CHOICES, 'scene_26g_cristaux_interdits', "Cristaux interdits > ")

    if choix == 0:
        joueur.tension_fragment = max(0, joueur.tension_fragment - 2)
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        dire(ACT_4_OUTCOMES, 'scene_26g_cristaux_interdits_response_1')
    elif choix == 1:
        joueur.connaissance_temporelle += 1
        joueur.tension_fragment += 1
        ajouter_score(joueur, "diplomatie", 1)
        dire(ACT_4_OUTCOMES, 'scene_26g_cristaux_interdits_response_2')
    elif choix == 2:
        ajouter_score(joueur, "armee", 2)
        joueur.tension_fragment += 3
        joueur.variables["cristaux_utilises_dangereusement"] = True
        dire(ACT_4_OUTCOMES, 'scene_26g_cristaux_interdits_response_3')
    else:
        fin_prematuree(joueur, ACT_4_OUTCOMES, 'ending_premature_cristaux_scelles', "Fin des Cristaux Scellés")
        return

    secret(joueur, ACT_4_OUTCOMES, 'scene_26g_cristaux_interdits_secret_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26g_cristaux_interdits_journal_1')


def scene_26b_nuit_des_survivants(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26b_nuit_des_survivants'])
    choix = choisir(ACT_4_CHOICES, 'scene_26b_nuit_des_survivants', "Nuit des survivants > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 1)
        joueur.reputation += 1
        dire(ACT_4_OUTCOMES, 'scene_26b_nuit_des_survivants_response_1')
    else:
        ajouter_score(joueur, "diplomatie", 1)
        joueur.reputation += 2
        dire(ACT_4_OUTCOMES, 'scene_26b_nuit_des_survivants_response_2')
        ajouter_score(joueur, "espionnage", 1)
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_4_OUTCOMES, 'scene_26b_nuit_des_survivants_response_3')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26b_nuit_des_survivants_journal_1')


def scene_26e_conseil_des_compagnons(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26e_conseil_des_compagnons'])
    dialogue = interaction_compagnons(joueur)
    if dialogue:
        raconter(dialogue)
    choix = choisir(ACT_4_CHOICES, 'scene_26e_conseil_des_compagnons', "Conseil des compagnons > ")

    if choix == 0:
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) + 10
        joueur.tension_fragment = max(0, joueur.tension_fragment - 1)
        dire(ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_response_1')
    elif choix == 1:
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) + 10
        joueur.variables["lyra_garde_fou"] = True
        dire(ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_response_2')
    elif choix == 2:
        ajouter_score(joueur, "armee", 1)
        ajouter_score(joueur, "espionnage", 1)
        ajouter_score(joueur, "diplomatie", 1)
        joueur.variables["commandement_partage"] = True
        dire(ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_response_3')
    else:
        joueur.reputation += 1
        joueur.loyautes["Garrick"] = joueur.loyautes.get("Garrick", 0) - 2
        joueur.loyautes["Lyra"] = joueur.loyautes.get("Lyra", 0) - 2
        joueur.variables["commandement_solitaire"] = True
        dire(ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_response_4')

    consequence(joueur, ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_consequence_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26e_conseil_des_compagnons_journal_1')


def scene_26h_derniers_ordres(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_26h_derniers_ordres'])
    choix = choisir(ACT_4_CHOICES, 'scene_26h_derniers_ordres', "Derniers ordres > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        joueur.variables["commandement_efficace"] = True
        dire(ACT_4_OUTCOMES, 'scene_26h_derniers_ordres_response_1')
    elif choix == 1:
        ajouter_score(joueur, "diplomatie", 2)
        joueur.reputation += 1
        joueur.variables["commandement_compatissant"] = True
        dire(ACT_4_OUTCOMES, 'scene_26h_derniers_ordres_response_2')
    else:
        ajouter_score(joueur, "diplomatie", 1)
        ajouter_score(joueur, "espionnage", 1)
        joueur.variables["commandement_equilibre"] = True
        dire(ACT_4_OUTCOMES, 'scene_26h_derniers_ordres_response_3')

    actualiser_reves_dynamiques(joueur)
    consequence(joueur, ACT_4_OUTCOMES, 'scene_26h_derniers_ordres_consequence_1')
    journal(joueur, ACT_4_OUTCOMES, 'scene_26h_derniers_ordres_journal_1')


def scene_27_prix_du_commandement(joueur):
    raconter(ACT_4_SCENE_TEXTS['scene_27_prix_du_commandement'])
    choix = choisir(ACT_4_CHOICES, 'scene_27_prix_du_commandement', "Après la bataille > ")

    if choix == 0:
        ajouter_score(joueur, "armee", 2)
        joueur.modifier_faction("Cités Libres", -5)
        consequence(joueur, ACT_4_OUTCOMES, 'scene_27_prix_du_commandement_consequence_1')
    else:
        joueur.reputation += 2
        joueur.modifier_faction("Aldor", -5)
        consequence(joueur, ACT_4_OUTCOMES, 'scene_27_prix_du_commandement_consequence_2')
        joueur.modifier_faction("Aldor", -5)
        joueur.modifier_faction("Ellorien", 5)
        consequence(joueur, ACT_4_OUTCOMES, 'scene_27_prix_du_commandement_consequence_3')
    joueur.acte_courant = "Acte V - Le Dernier Âge"
    journal(joueur, ACT_4_OUTCOMES, 'scene_27_prix_du_commandement_journal_1')
    afficher_bilan_acte(joueur, "ACTE IV - LA GUERRE DU CRÉPUSCULE")


def jouer_acte_4(joueur):
    scene_25_conseil_de_guerre(joueur)
    transition(ACT_4_OUTCOMES, 'transition_25_to_25a')
    lancer_evenement_aleatoire(joueur)
    scene_25a_camp_des_refugies(joueur)
    transition(ACT_4_OUTCOMES, 'transition_25a_to_25b')
    scene_25b_forge_des_bannieres(joueur)
    ravitaillement(joueur, "Intendance de la forteresse")
    visiter_marchand(joueur, MARCHAND_STOCK_ACTE_4, "\nL'intendance a mis de côté un arsenal réservé aux héros de la coalition.", palier="boss")
    transition(ACT_4_OUTCOMES, 'transition_25b_to_25c')
    scene_25c_cartes_du_crepuscule(joueur)
    transition(ACT_4_OUTCOMES, 'transition_25c_to_25d')
    scene_25d_fissures_de_la_coalition(joueur)
    if joueur.acte_courant == "Épilogue":
        return
    transition(ACT_4_OUTCOMES, 'transition_25d_to_25f')
    scene_25f_route_faction(joueur)
    transition(ACT_4_OUTCOMES, 'transition_25f_to_25e')
    scene_25e_trahison_des_bannieres(joueur)
    transition(ACT_4_OUTCOMES, 'transition_25e_to_26')
    if not scene_26_bataille_des_trois_bannieres(joueur):
        return
    transition(ACT_4_OUTCOMES, 'transition_26_to_26f')
    if not scene_26f_revers_des_lignes(joueur):
        return
    transition(ACT_4_OUTCOMES, 'transition_26f_to_26a')
    scene_26a_breche_du_crepuscule(joueur)
    transition(ACT_4_OUTCOMES, 'transition_26a_to_26c')
    scene_26c_cristal_sur_le_front(joueur)
    transition(ACT_4_OUTCOMES, 'transition_26c_to_26c1')
    scene_26c1_cristal_prioritaire(joueur)
    transition(ACT_4_OUTCOMES, 'transition_26c1_to_26d')
    if not scene_26d_contre_offensive_malakar(joueur):
        return
    transition(ACT_4_OUTCOMES, 'transition_26d_to_26g')
    scene_26g_cristaux_interdits(joueur)
    if joueur.acte_courant == "Épilogue":
        return
    transition(ACT_4_OUTCOMES, 'transition_26g_to_26b')
    scene_26b_nuit_des_survivants(joueur)
    repos_de_camp(joueur, "Camp des survivants")
    transition(ACT_4_OUTCOMES, 'transition_26b_to_26e')
    scene_26e_conseil_des_compagnons(joueur)
    transition(ACT_4_OUTCOMES, 'transition_26e_to_26h')
    scene_26h_derniers_ordres(joueur)
    transition(ACT_4_OUTCOMES, 'transition_26h_to_27')
    scene_27_prix_du_commandement(joueur)


def jouer(joueur=None, sauvegarder=True):
    if joueur is None:
        joueur = charger_ou_preparer(4)
    joueur.acte_courant = "Acte IV - La Guerre du Crépuscule"
    if joueur.pv > 0:
        jouer_acte_4(joueur)
    if sauvegarder and joueur.pv > 0:
        sauvegarder_fin_acte(joueur)
    return joueur
