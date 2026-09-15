# Événements aléatoires de route pour Elderia

RANDOM_EVENTS = {
    "marchand_ambulant": {
        "titre": "Un marchand égaré",
        "description": "Un vieil homme tire une charrette grinçante sur le bord de la route. Il propose des composants rares.",
        "image": "assets/images/backgrounds/S02_main_menu.png", # placeholder
        "choix": ["Acheter du Minerai de Fer (15g)", "Acheter du Cuir de Qualité (10g)", "Ignorer et continuer"],
        "outcomes": [
            {"type": "buy_comp", "item": "Minerai de Fer", "prix": 15},
            {"type": "buy_comp", "item": "Cuir de Qualité", "prix": 10},
            {"type": "text", "text": "Vous reprenez la route sans un mot."}
        ]
    },
    "sanctuaire_oublie": {
        "titre": "Le Sanctuaire de l'Aube",
        "description": "Une petite chapelle de pierre semble vibrer d'une énergie ancienne. On raconte que prier ici renforce la volonté.",
        "image": "assets/images/backgrounds/S05_act_transition.png",
        "choix": ["Prier (Test Volonté 12)", "Fouiller les environs", "Partir"],
        "outcomes": [
            {"type": "test_stat", "stat": "volonte", "seuil": 12, "success": "vfx_bless", "fail": "text_fail"},
            {"type": "find_loot", "items": ["Éclat de Cristal"], "prob": 0.3},
            {"type": "text", "text": "Le silence du sanctuaire vous accompagne."}
        ]
    },
    "embuscade_bandits": {
        "titre": "Embuscade !",
        "description": "Des brigands surgissent des hautes herbes ! Ils en veulent à votre bourse.",
        "image": "assets/images/backgrounds/S04_combat_arena.png",
        "choix": ["Combattre", "Négocier (Charisme 14)", "Fuir (Agilité 13)"],
        "outcomes": [
            {"type": "combat", "ennemi": "Bandit"},
            {"type": "test_stat", "stat": "charisme", "seuil": 14, "success": "text_negotiated", "fail": "combat"},
            {"type": "test_stat", "stat": "agilite", "seuil": 13, "success": "text_escaped", "fail": "combat_surprise"}
        ]
    }
}
