import random
from elderia.core.io import demander_choix, illustrer, raconter
from elderia.content.random_events import RANDOM_EVENTS

def lancer_evenement_aleatoire(joueur):
    """Déclenche une rencontre aléatoire sur la route."""
    if random.random() > 0.4: # 40% de chance de rencontre
        return

    event_key = random.choice(list(RANDOM_EVENTS.keys()))
    event = RANDOM_EVENTS[event_key]

    raconter(f"\n--- RENCONTRE : {event['titre']} ---")
    illustrer(event['image'])
    raconter(event['description'])

    choix_idx = demander_choix("Votre action > ", event['choix'])
    outcome = event['outcomes'][choix_idx]

    traiter_outcome(joueur, outcome)

def traiter_outcome(joueur, outcome):
    from elderia.core.systems import tester_stat
    from elderia.core.combat import lancer_combat, creer_ennemi

    o_type = outcome['type']

    if o_type == "text":
        raconter(outcome['text'])

    elif o_type == "buy_comp":
        if joueur.or_poches >= outcome['prix']:
            joueur.or_poches -= outcome['prix']
            joueur.ajouter_composant(outcome['item'])
            raconter(f"Vous avez acheté {outcome['item']}.")
        else:
            raconter("Vous n'avez pas assez d'or.")

    elif o_type == "test_stat":
        if tester_stat(joueur, outcome['stat'], outcome['seuil']):
            if outcome['success'] == "vfx_bless":
                joueur.effets_actifs["Bénédiction"] = 3
                raconter("Une aura dorée vous entoure. Vous vous sentez plus fort.")
        else:
            raconter("Rien ne se produit.")

    elif o_type == "combat":
        lancer_combat(joueur, creer_ennemi(outcome['ennemi']))

    elif o_type == "find_loot":
        if random.random() < outcome['prob']:
            item = random.choice(outcome['items'])
            joueur.ajouter_composant(item)
            raconter(f"Vous avez trouvé : {item} !")
        else:
            raconter("Vous n'avez rien trouvé d'utile.")
