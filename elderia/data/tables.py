import os

def obtenir_chemin_securise(nom_fichier):
    dir_priv = os.environ.get("ANDROID_PRIVATE_DATA")
    if not dir_priv:
        if os.environ.get("HOME") and "android" in os.environ.get("HOME", "").lower():
            dir_priv = os.environ.get("HOME")
    if dir_priv:
        return os.path.join(dir_priv, nom_fichier)
    return nom_fichier

SAUVEGARDE_FICHIER = obtenir_chemin_securise("save.json")

ORIGINES = {
    "Noble Déchu": "Vous portez le nom d'une lignée brisée. Le protocole et l'histoire n'ont aucun secret pour vous.",
    "Enfant des Rues": "Vous avez survécu dans l'ombre des cités. Vous repérez les mensonges et les passages cachés.",
    "Ancien Soldat": "Vous avez servi sous les bannières d'Aldor. La discipline et la stratégie sont votre seconde nature.",
    "Érudit Errant": "Vous avez passé votre vie dans les livres. Le lore ancien et la magie résiduelle vous parlent.",
}

CLASSES = {
    "Guerrier": {
        "force": 8,
        "agilite": 4,
        "endurance": 10,
        "intelligence": 2,
        "volonte": 3,
        "charisme": 4,
        "or": 20,
        "competence": "Coup Puissant",
    },
    "Rôdeur": {
        "force": 5,
        "agilite": 8,
        "endurance": 7,
        "intelligence": 2,
        "volonte": 5,
        "charisme": 4,
        "or": 25,
        "competence": "Tir Rapide",
    },
    "Mage": {
        "force": 2,
        "agilite": 4,
        "endurance": 4,
        "intelligence": 10,
        "volonte": 6,
        "charisme": 5,
        "or": 15,
        "competence": "Boule de Feu",
    },
    "Paladin": {
        "force": 6,
        "agilite": 4,
        "endurance": 9,
        "intelligence": 5,
        "volonte": 7,
        "charisme": 6,
        "or": 18,
        "competence": "Lumière Sacrée",
    },
    "Nécromancien": {
        "force": 3,
        "agilite": 5,
        "endurance": 6,
        "intelligence": 8,
        "volonte": 8,
        "charisme": 6,
        "or": 20,
        "competence": "Réveil des Cendres",
    },
}

DIFFICULTES = {
    "Facile": {"degats_ennemis": 0.75, "xp": 1.25, "or": 1.25, "pv_joueur": 1.15, "permadeath": False},
    "Normal": {"degats_ennemis": 1.0, "xp": 1.0, "or": 1.0, "pv_joueur": 1.0, "permadeath": False},
    "Difficile": {"degats_ennemis": 1.25, "xp": 1.15, "or": 1.15, "pv_joueur": 0.9, "permadeath": False},
    "Hardcore": {"degats_ennemis": 1.5, "xp": 1.4, "or": 1.4, "pv_joueur": 0.85, "permadeath": True},
}

# Compense le risque accru par de meilleures chances de butin/objets rares selon la difficulté.
DIFFICULTE_BONUS_RARETE = {
    "Facile": {"Commun": 1.0, "Rare": 1.0, "Épique": 1.0},
    "Normal": {"Commun": 1.0, "Rare": 1.0, "Épique": 1.0},
    "Difficile": {"Commun": 0.85, "Rare": 1.3, "Épique": 1.6},
    "Hardcore": {"Commun": 0.7, "Rare": 1.5, "Épique": 2.2},
}

XP_ENNEMIS = {
    "Rat Corrompu": 20,
    "Gobelin": 20,
    "Squelette": 25,
    "Bandit": 30,
    "Porteur de Cendres": 40,
    "Garde Cendreux": 80,
    "Assassin de Morvayn": 60,
    "Rafleur temporel": 70,
    "Bourreau des Cendres": 180,
    "Morvayn": 2500,
    "Lieutenant de Malakar": 80,
}

ARMES = {
    "Mains nues": {"degats": 1, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "neutre"},
    "Dague rouillée": {"degats": 2, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "dague"},
    "Épée Longue": {"degats": 4, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "lourde"},
    "Épée d'acier": {"degats": 4, "bonus_force": 1, "bonus_intelligence": 0, "categorie": "lourde"},
    "Arc elfique": {"degats": 3, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "distance"},
    "Bâton runique": {"degats": 2, "bonus_force": 0, "bonus_intelligence": 2, "categorie": "arcane"},
    "Hache des Cendres": {"degats": 6, "bonus_force": 2, "bonus_intelligence": 0, "categorie": "lourde"},
    "Excalion": {"degats": 8, "bonus_force": 4, "bonus_intelligence": 0, "categorie": "lourde"},
    "Tranche-Sceau": {"degats": 10, "bonus_force": 5, "bonus_intelligence": 0, "categorie": "lourde"},
    "Sceptre du Dévoreur": {"degats": 6, "bonus_force": 0, "bonus_intelligence": 6, "categorie": "arcane"},
    "Arc du Jugement": {"degats": 8, "bonus_force": 3, "bonus_intelligence": 0, "categorie": "distance"},
}

ARMURES = {
    "Vêtements simples": {"reduction": 0, "defense": 0, "agilite": 0, "categorie": "legere"},
    "Armure de cuir": {"reduction": 2, "defense": 1, "agilite": 0, "categorie": "legere"},
    "Cotte de mailles": {"reduction": 4, "defense": 2, "agilite": -1, "categorie": "lourde"},
    "Armure Royale": {"reduction": 5, "defense": 3, "agilite": -1, "categorie": "lourde"},
    "Plaques": {"reduction": 6, "defense": 3, "agilite": -2, "categorie": "lourde"},
    "Mithril": {"reduction": 8, "defense": 4, "agilite": 0, "categorie": "lourde"},
    "Cape elfique": {"reduction": 2, "defense": 1, "agilite": 2, "categorie": "legere"},
    "Armure du Titan": {"reduction": 6, "defense": 3, "agilite": -2, "categorie": "lourde"},
    "Égide du Dernier Âge": {"reduction": 9, "defense": 5, "agilite": 0, "categorie": "lourde"},
    "Voile du Sceau": {"reduction": 5, "defense": 3, "agilite": 3, "categorie": "legere"},
}

# Efficacité de l'équipement selon la classe : un Guerrier tire peu de profit d'un bâton arcanique,
# un Mage traîne sous une armure lourde. Multiplicateur appliqué aux stats de puissance de l'objet
# (dégâts/bonus/réduction/défense), pas à l'agilité (encombrement physique, indépendant du talent).
AFFINITES_CLASSE = {
    "Guerrier": {
        "armes": {"lourde": 1.2, "dague": 0.9, "distance": 0.8, "arcane": 0.6, "neutre": 1.0},
        "armures": {"lourde": 1.15, "legere": 0.9, "neutre": 1.0},
        "secondaire": {"lourde": 1.2, "legere": 0.9, "arcane": 0.6, "distance": 0.8, "neutre": 1.0},
    },
    "Paladin": {
        "armes": {"lourde": 1.15, "dague": 0.9, "distance": 0.8, "arcane": 0.7, "neutre": 1.0},
        "armures": {"lourde": 1.15, "legere": 0.9, "neutre": 1.0},
        "secondaire": {"lourde": 1.1, "legere": 1.15, "arcane": 0.7, "distance": 0.8, "neutre": 1.0},
    },
    "Rôdeur": {
        "armes": {"distance": 1.2, "dague": 1.1, "lourde": 0.85, "arcane": 0.7, "neutre": 1.0},
        "armures": {"legere": 1.15, "lourde": 0.8, "neutre": 1.0},
        "secondaire": {"distance": 1.2, "legere": 1.0, "lourde": 0.8, "arcane": 0.7, "neutre": 1.0},
    },
    "Mage": {
        "armes": {"arcane": 1.25, "dague": 0.9, "distance": 0.8, "lourde": 0.6, "neutre": 1.0},
        "armures": {"legere": 1.2, "lourde": 0.6, "neutre": 1.0},
        "secondaire": {"arcane": 1.25, "legere": 1.0, "distance": 0.8, "lourde": 0.6, "neutre": 1.0},
    },
    "Nécromancien": {
        "armes": {"arcane": 1.2, "dague": 1.0, "distance": 0.8, "lourde": 0.6, "neutre": 1.0},
        "armures": {"legere": 1.15, "lourde": 0.65, "neutre": 1.0},
        "secondaire": {"arcane": 1.2, "legere": 1.0, "distance": 0.8, "lourde": 0.6, "neutre": 1.0},
    },
}

# Objets de seconde main : boucliers pour les classes de mêlee, mais aussi grimoires, carquois et reliques
# adaptés aux autres classes. "categorie" est évaluée via AFFINITES_CLASSE[classe]["secondaire"].
BOUCLIERS = {
    "Bouclier en bois": {"blocage": 0, "defense": 1, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "lourde"},
    "Bouclier renforcé": {"blocage": 2, "defense": 1, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "lourde"},
    "Bouclier royal": {"blocage": 4, "defense": 2, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "lourde"},
    "Grimoire des Cendres": {"blocage": 0, "defense": 1, "bonus_force": 0, "bonus_intelligence": 3, "categorie": "arcane"},
    "Grimoire du Dévoreur": {"blocage": 1, "defense": 2, "bonus_force": 0, "bonus_intelligence": 5, "categorie": "arcane"},
    "Carquois de précision": {"blocage": 1, "defense": 0, "bonus_force": 1, "bonus_intelligence": 0, "categorie": "distance"},
    "Carquois du Grand Chasseur": {"blocage": 2, "defense": 1, "bonus_force": 2, "bonus_intelligence": 0, "categorie": "distance"},
    "Relique bénie": {"blocage": 1, "defense": 2, "bonus_force": 0, "bonus_intelligence": 1, "categorie": "legere"},
    "Relique du Dernier Serment": {"blocage": 2, "defense": 3, "bonus_force": 0, "bonus_intelligence": 2, "categorie": "legere"},
}

# Prix de référence (avant rareté) pour la revente d'équipement chez le marchand.
PRIX_BASE_ARMES = {
    "Mains nues": 0,
    "Dague rouillée": 5,
    "Épée Longue": 10,
    "Épée d'acier": 18,
    "Arc elfique": 20,
    "Bâton runique": 22,
    "Hache des Cendres": 45,
    "Excalion": 90,
    "Tranche-Sceau": 130,
    "Sceptre du Dévoreur": 120,
    "Arc du Jugement": 125,
}

PRIX_BASE_ARMURES = {
    "Vêtements simples": 0,
    "Armure de cuir": 8,
    "Cotte de mailles": 16,
    "Armure Royale": 40,
    "Plaques": 60,
    "Mithril": 80,
    "Cape elfique": 55,
    "Armure du Titan": 75,
    "Égide du Dernier Âge": 115,
    "Voile du Sceau": 100,
}

PRIX_BASE_BOUCLIERS = {
    "Bouclier en bois": 5,
    "Bouclier renforcé": 15,
    "Bouclier royal": 40,
    "Grimoire des Cendres": 20,
    "Grimoire du Dévoreur": 50,
    "Carquois de précision": 15,
    "Carquois du Grand Chasseur": 40,
    "Relique bénie": 25,
    "Relique du Dernier Serment": 55,
}

# Bijoux : emplacement d'accessoire universel (aucune affinité de classe), un effet passif
# distinct par objet plutôt que des stats brutes redondantes avec arme/armure/bouclier.
BIJOUX = {
    "Anneau de Vigueur": {"effet": "regen_pv", "valeur": 2},
    "Amulette des Cendres": {"effet": "regen_ressource", "valeur": 2},
    "Talisman du Chasseur": {"effet": "bonus_critique", "valeur": 10},
    "Sceau de Fortune": {"effet": "bonus_loot", "valeur": 20},
    "Pendentif du Sacrifice": {"effet": "vol_vie", "valeur": 15},
    "Boucle d'Acier": {"effet": "reduction_degats", "valeur": 2},
    "Charme du Fuyard": {"effet": "bonus_esquive", "valeur": 2},
    "Larme d'Ashkar": {"effet": "bonus_soin", "valeur": 15},
    "Grelot du Marchand": {"effet": "reduction_prix", "valeur": 10},
    "Œil de Cristal": {"effet": "bonus_test_stat", "valeur": 2},
}

PRIX_BASE_BIJOUX = {
    "Anneau de Vigueur": 20,
    "Amulette des Cendres": 25,
    "Talisman du Chasseur": 30,
    "Sceau de Fortune": 35,
    "Pendentif du Sacrifice": 30,
    "Boucle d'Acier": 25,
    "Charme du Fuyard": 25,
    "Larme d'Ashkar": 20,
    "Grelot du Marchand": 20,
    "Œil de Cristal": 30,
}

# Affixes tirés aléatoirement pour faire varier l'équipement d'une partie à l'autre.
# Chaque entrée : (étiquette affichée, modificateurs appliqués aux stats de base, rareté).
RARETES = {
    "Commun": {"poids": 60, "multiplicateur_prix": 1.0},
    "Rare": {"poids": 30, "multiplicateur_prix": 1.6},
    "Épique": {"poids": 10, "multiplicateur_prix": 2.5},
}

# Multiplicateurs de poids appliqués selon la dangerosité de l'ennemi vaincu :
# un boss a bien plus de chances de laisser tomber du Rare/Épique qu'un ennemi mineur.
BONUS_RARETE_PAR_PALIER = {
    "mineur": {"Commun": 1.0, "Rare": 1.0, "Épique": 1.0},
    "elite": {"Commun": 0.7, "Rare": 1.6, "Épique": 2.0},
    "boss": {"Commun": 0.4, "Rare": 1.8, "Épique": 4.0},
}

# Verrou de progression : une rareté n'est tirable que si elle figure dans ce palier.
RARETES_AUTORISEES_PAR_PALIER = {
    "mineur": ("Commun", "Rare"),
    "elite": ("Commun", "Rare", "Épique"),
    "boss": ("Commun", "Rare", "Épique"),
}

PREFIXES_ARMES = [
    ("", {}, "Commun"),
    ("Rouillée", {"degats": -1}, "Commun"),
    ("Affûtée", {"degats": 1}, "Commun"),
    ("Renforcée", {"degats": 1, "bonus_force": 1}, "Rare"),
    ("Runique", {"bonus_intelligence": 1}, "Rare"),
    ("Ancestrale", {"degats": 2}, "Rare"),
    ("Bénie", {"degats": 1, "bonus_intelligence": 1}, "Épique"),
    ("Légendaire", {"degats": 3, "bonus_force": 2}, "Épique"),
]

PREFIXES_ARMURES = [
    ("", {}, "Commun"),
    ("Rapiécée", {"reduction": -1}, "Commun"),
    ("Renforcée", {"reduction": 1}, "Commun"),
    ("des Sentinelles", {"reduction": 1, "defense": 1}, "Rare"),
    ("Runique", {"agilite": 1}, "Rare"),
    ("Ancestrale", {"reduction": 2}, "Rare"),
    ("du Titan", {"reduction": 2, "defense": 1}, "Épique"),
]

PREFIXES_BOUCLIERS = [
    ("", {}, "Commun"),
    ("Ébréché", {"blocage": -1}, "Commun"),
    ("Renforcé", {"blocage": 1}, "Commun"),
    ("du Gardien", {"blocage": 1, "defense": 1}, "Rare"),
    ("du Ciel", {"blocage": 2, "defense": 1}, "Épique"),
]

# Affixes dédiés aux objets de seconde main non-boucliers : chaque table cible la statistique
# signature de la catégorie (force pour un carquois, intelligence pour un grimoire, etc.).
PREFIXES_CARQUOIS = [
    ("", {}, "Commun"),
    ("Usé", {"bonus_force": -1}, "Commun"),
    ("Affûté", {"bonus_force": 1}, "Commun"),
    ("de Précision", {"bonus_force": 1, "blocage": 1}, "Rare"),
    ("du Grand Chasseur", {"bonus_force": 2, "blocage": 1}, "Épique"),
]

PREFIXES_GRIMOIRES = [
    ("", {}, "Commun"),
    ("Corrompu", {"bonus_intelligence": -1}, "Commun"),
    ("Annoté", {"bonus_intelligence": 1}, "Commun"),
    ("Runique", {"bonus_intelligence": 2, "defense": 1}, "Rare"),
    ("des Cendres Ardentes", {"bonus_intelligence": 3, "defense": 1}, "Épique"),
]

PREFIXES_RELIQUES = [
    ("", {}, "Commun"),
    ("Ternie", {"defense": -1}, "Commun"),
    ("Polie", {"defense": 1}, "Commun"),
    ("Sanctifiée", {"defense": 1, "bonus_intelligence": 1}, "Rare"),
    ("du Dernier Serment", {"defense": 2, "bonus_intelligence": 1, "blocage": 1}, "Épique"),
]

# Affixes des bijoux : modifient uniquement la magnitude ("valeur") de l'effet passif de l'objet.
PREFIXES_BIJOUX = [
    ("", {}, "Commun"),
    ("Terni", {"valeur": -1}, "Commun"),
    ("Poli", {"valeur": 1}, "Commun"),
    ("Enchanté", {"valeur": 2}, "Rare"),
    ("Ascendant", {"valeur": 4}, "Épique"),
]

COMPETENCES = {
    "Coup Puissant": {"ressource": "energie", "cout": 2, "degats_bonus": 5},
    "Tir Rapide": {"ressource": "energie", "cout": 3, "attaques": 2},
    "Boule de Feu": {"ressource": "mana", "cout": 5, "des": (6, 6, 6)},
    "Lumière Sacrée": {"ressource": "mana", "cout": 5, "soin_des": (6, 6, 6)},
    "Réveil des Cendres": {"ressource": "mana", "cout": 6, "des": (4, 4)},
}

# Arbre de talents : 4 paliers par classe. Le palier 1 ouvre une branche (A/B),
# le palier 3 la subdivise à nouveau (A1/A2 ou B1/B2), pour 4 profils finaux par classe.
# Chaque nœud : id unique, palier de déblocage, prérequis (id d'un nœud précédent ou None),
# et un effet générique { "type": ..., "valeur": ... } lu par le moteur de combat.
ARBRE_TALENTS = {
    "Guerrier": [
        {"id": "berserker", "nom": "Berserker", "palier": 5, "prerequis": None, "effet": {"type": "degats_pv_bas", "valeur": 3}},
        {"id": "mur_de_fer", "nom": "Mur de fer", "palier": 5, "prerequis": None, "effet": {"type": "reduction_degats", "valeur": 2}},
        {"id": "rage_prolongee", "nom": "Rage prolongée", "palier": 15, "prerequis": "berserker", "effet": {"type": "degats_pv_bas", "valeur": 5}},
        {"id": "bouclier_vivant", "nom": "Bouclier vivant", "palier": 15, "prerequis": "mur_de_fer", "effet": {"type": "reduction_degats", "valeur": 4}},
        {"id": "fureur_sanguinaire", "nom": "Fureur sanguinaire", "palier": 30, "prerequis": "rage_prolongee", "effet": {"type": "degats_pv_bas", "valeur": 7}},
        {"id": "instinct_predateur", "nom": "Instinct prédateur", "palier": 30, "prerequis": "rage_prolongee", "effet": {"type": "crit_bonus", "valeur": 2}},
        {"id": "rempart_inebranlable", "nom": "Rempart inébranlable", "palier": 30, "prerequis": "bouclier_vivant", "effet": {"type": "reduction_degats", "valeur": 6}},
        {"id": "gardien_devoue", "nom": "Gardien dévoué", "palier": 30, "prerequis": "bouclier_vivant", "effet": {"type": "bonus_compagnons", "valeur": 0.2}},
        {"id": "avatar_de_rage", "nom": "Avatar de la Rage", "palier": 45, "prerequis": "fureur_sanguinaire", "effet": {"type": "degats_pv_bas", "valeur": 10}},
        {"id": "chasseur_implacable", "nom": "Chasseur implacable", "palier": 45, "prerequis": "instinct_predateur", "effet": {"type": "crit_bonus", "valeur": 4}},
        {"id": "forteresse_vivante", "nom": "Forteresse vivante", "palier": 45, "prerequis": "rempart_inebranlable", "effet": {"type": "reduction_degats", "valeur": 9}},
        {"id": "protecteur_absolu_guerrier", "nom": "Protecteur absolu", "palier": 45, "prerequis": "gardien_devoue", "effet": {"type": "bonus_compagnons", "valeur": 0.4}},
    ],
    "Rôdeur": [
        {"id": "maitre_archer", "nom": "Maître Archer", "palier": 5, "prerequis": None, "effet": {"type": "bonus_arme_type", "valeur": 2, "mot_cle": "Arc"}},
        {"id": "ombre_des_routes", "nom": "Ombre des routes", "palier": 5, "prerequis": None, "effet": {"type": "bonus_agilite", "valeur": 2}},
        {"id": "oeil_du_faucon", "nom": "Œil du faucon", "palier": 15, "prerequis": "maitre_archer", "effet": {"type": "bonus_arme_type", "valeur": 4, "mot_cle": "Arc"}},
        {"id": "pas_silencieux", "nom": "Pas silencieux", "palier": 15, "prerequis": "ombre_des_routes", "effet": {"type": "bonus_agilite", "valeur": 4}},
        {"id": "tir_perforant", "nom": "Tir perforant", "palier": 30, "prerequis": "oeil_du_faucon", "effet": {"type": "bonus_arme_type", "valeur": 6, "mot_cle": "Arc"}},
        {"id": "volee_precise", "nom": "Volée précise", "palier": 30, "prerequis": "oeil_du_faucon", "effet": {"type": "bonus_competence_degats", "valeur": 4}},
        {"id": "art_de_lesquive", "nom": "Art de l'esquive", "palier": 30, "prerequis": "pas_silencieux", "effet": {"type": "bonus_agilite", "valeur": 6}},
        {"id": "reflexes_du_chasseur", "nom": "Réflexes du chasseur", "palier": 30, "prerequis": "pas_silencieux", "effet": {"type": "crit_bonus", "valeur": 3}},
        {"id": "aigle_royal", "nom": "Aigle royal", "palier": 45, "prerequis": "tir_perforant", "effet": {"type": "bonus_arme_type", "valeur": 10, "mot_cle": "Arc"}},
        {"id": "tempete_de_fleches", "nom": "Tempête de flèches", "palier": 45, "prerequis": "volee_precise", "effet": {"type": "bonus_competence_degats", "valeur": 8}},
        {"id": "fantome_des_bois", "nom": "Fantôme des bois", "palier": 45, "prerequis": "art_de_lesquive", "effet": {"type": "bonus_agilite", "valeur": 10}},
        {"id": "predateur_absolu", "nom": "Prédateur absolu", "palier": 45, "prerequis": "reflexes_du_chasseur", "effet": {"type": "crit_bonus", "valeur": 6}},
    ],
    "Mage": [
        {"id": "chronomancien", "nom": "Chronomancien", "palier": 5, "prerequis": None, "effet": {"type": "reduction_cout_competence", "valeur": 1}},
        {"id": "feu_interieur", "nom": "Feu intérieur", "palier": 5, "prerequis": None, "effet": {"type": "bonus_competence_degats", "valeur": 2}},
        {"id": "maitrise_du_temps", "nom": "Maîtrise du temps", "palier": 15, "prerequis": "chronomancien", "effet": {"type": "reduction_cout_competence", "valeur": 2}},
        {"id": "brasier_interieur", "nom": "Brasier intérieur", "palier": 15, "prerequis": "feu_interieur", "effet": {"type": "bonus_competence_degats", "valeur": 4}},
        {"id": "flux_arcanique", "nom": "Flux arcanique", "palier": 30, "prerequis": "maitrise_du_temps", "effet": {"type": "bonus_mana", "valeur": 15}},
        {"id": "dilatation_temporelle", "nom": "Dilatation temporelle", "palier": 30, "prerequis": "maitrise_du_temps", "effet": {"type": "reduction_cout_competence", "valeur": 3}},
        {"id": "coeur_ardent", "nom": "Cœur ardent", "palier": 30, "prerequis": "brasier_interieur", "effet": {"type": "bonus_competence_degats", "valeur": 6}},
        {"id": "combustion_totale", "nom": "Combustion totale", "palier": 30, "prerequis": "brasier_interieur", "effet": {"type": "crit_bonus", "valeur": 3}},
        {"id": "archimage_du_temps", "nom": "Archimage du temps", "palier": 45, "prerequis": "flux_arcanique", "effet": {"type": "bonus_mana", "valeur": 25}},
        {"id": "seigneur_des_instants", "nom": "Seigneur des instants", "palier": 45, "prerequis": "dilatation_temporelle", "effet": {"type": "reduction_cout_competence", "valeur": 5}},
        {"id": "avatar_des_flammes", "nom": "Avatar des flammes", "palier": 45, "prerequis": "coeur_ardent", "effet": {"type": "bonus_competence_degats", "valeur": 10}},
        {"id": "supernova", "nom": "Supernova", "palier": 45, "prerequis": "combustion_totale", "effet": {"type": "crit_bonus", "valeur": 6}},
    ],
    "Paladin": [
        {"id": "protecteur", "nom": "Protecteur", "palier": 5, "prerequis": None, "effet": {"type": "reduction_degats", "valeur": 2}},
        {"id": "jugement_sacre", "nom": "Jugement sacré", "palier": 5, "prerequis": None, "effet": {"type": "bonus_armure_cible", "valeur": 3}},
        {"id": "rempart_sacre", "nom": "Rempart sacré", "palier": 15, "prerequis": "protecteur", "effet": {"type": "reduction_degats", "valeur": 4}},
        {"id": "lame_du_jugement", "nom": "Lame du jugement", "palier": 15, "prerequis": "jugement_sacre", "effet": {"type": "bonus_armure_cible", "valeur": 5}},
        {"id": "aura_de_soin", "nom": "Aura de soin", "palier": 30, "prerequis": "rempart_sacre", "effet": {"type": "bonus_soin", "valeur": 6}},
        {"id": "bouclier_de_lumiere", "nom": "Bouclier de lumière", "palier": 30, "prerequis": "rempart_sacre", "effet": {"type": "reduction_degats", "valeur": 6}},
        {"id": "zele_divin", "nom": "Zèle divin", "palier": 30, "prerequis": "lame_du_jugement", "effet": {"type": "bonus_armure_cible", "valeur": 7}},
        {"id": "chatiment_ardent", "nom": "Châtiment ardent", "palier": 30, "prerequis": "lame_du_jugement", "effet": {"type": "crit_bonus", "valeur": 3}},
        {"id": "guerisseur_beni", "nom": "Guérisseur béni", "palier": 45, "prerequis": "aura_de_soin", "effet": {"type": "bonus_soin", "valeur": 12}},
        {"id": "gardien_eternel", "nom": "Gardien éternel", "palier": 45, "prerequis": "bouclier_de_lumiere", "effet": {"type": "reduction_degats", "valeur": 9}},
        {"id": "marteau_de_la_justice", "nom": "Marteau de la justice", "palier": 45, "prerequis": "zele_divin", "effet": {"type": "bonus_armure_cible", "valeur": 12}},
        {"id": "executeur_sacre", "nom": "Exécuteur sacré", "palier": 45, "prerequis": "chatiment_ardent", "effet": {"type": "crit_bonus", "valeur": 6}},
    ],
    "Nécromancien": [
        {"id": "pacte_des_cendres", "nom": "Pacte des Cendres", "palier": 5, "prerequis": None, "effet": {"type": "bonus_compagnons", "valeur": 0.15}},
        {"id": "etreinte_funeste", "nom": "Étreinte funeste", "palier": 5, "prerequis": None, "effet": {"type": "bonus_competence_degats", "valeur": 2}},
        {"id": "legs_des_cendres", "nom": "Legs des Cendres", "palier": 15, "prerequis": "pacte_des_cendres", "effet": {"type": "bonus_compagnons", "valeur": 0.3}},
        {"id": "cendres_ardentes", "nom": "Cendres ardentes", "palier": 15, "prerequis": "etreinte_funeste", "effet": {"type": "bonus_competence_degats", "valeur": 4}},
        {"id": "cohorte_spectrale", "nom": "Cohorte spectrale", "palier": 30, "prerequis": "legs_des_cendres", "effet": {"type": "bonus_compagnons", "valeur": 0.45}},
        {"id": "rempart_ossements", "nom": "Rempart d'ossements", "palier": 30, "prerequis": "legs_des_cendres", "effet": {"type": "reduction_degats", "valeur": 6}},
        {"id": "nuee_de_cendres", "nom": "Nuée de Cendres", "palier": 30, "prerequis": "cendres_ardentes", "effet": {"type": "bonus_competence_degats", "valeur": 6}},
        {"id": "frappe_necrotique", "nom": "Frappe nécrotique", "palier": 30, "prerequis": "cendres_ardentes", "effet": {"type": "crit_bonus", "valeur": 3}},
        {"id": "legion_des_cendres", "nom": "Légion des Cendres", "palier": 45, "prerequis": "cohorte_spectrale", "effet": {"type": "bonus_compagnons", "valeur": 0.6}},
        {"id": "ossuaire_vivant", "nom": "Ossuaire vivant", "palier": 45, "prerequis": "rempart_ossements", "effet": {"type": "reduction_degats", "valeur": 9}},
        {"id": "cataclysme_de_cendres", "nom": "Cataclysme de Cendres", "palier": 45, "prerequis": "nuee_de_cendres", "effet": {"type": "bonus_competence_degats", "valeur": 10}},
        {"id": "faucheuse_necrotique", "nom": "Faucheuse nécrotique", "palier": 45, "prerequis": "frappe_necrotique", "effet": {"type": "crit_bonus", "valeur": 6}},
    ],
}

# Capacités spéciales des boss : déclenchées aléatoirement lors de leur riposte en combat.
# La clé est cherchée comme sous-chaîne dans le nom affiché de l'ennemi (gère les variantes/phases).
CAPACITES_SPECIALES = {
    "Morvayn": {"nom": "Tempête Chronique", "chance": 0.20, "des": (8, 8, 8)},
    "Champion de guerre": {"nom": "Cri de guerre", "chance": 0.25, "des": (6, 6)},
    "Avant-garde fracturée de Malakar": {"nom": "Rupture temporelle", "chance": 0.25, "des": (8, 8)},
    "Avatar de Malakar": {"nom": "Rupture temporelle", "chance": 0.25, "des": (10, 10)},
    "Manifestation du Dévoreur": {"nom": "Faim insatiable", "chance": 0.25, "des": (6, 6, 6), "vol_vie": True},
}

ENNEMIS = {
    "Rat Corrompu": {"nom": "Rat Corrompu", "pv": 20, "force": 3, "agilite": 6, "armure": 0, "arme": 2, "xp": 20, "or": 0},
    "Gobelin": {"nom": "Gobelin", "pv": 14, "force": 4, "agilite": 5, "armure": 1, "arme": 2, "xp": 20, "or": 6},
    "Squelette": {"nom": "Squelette", "pv": 15, "force": 5, "agilite": 2, "armure": 2, "arme": 3, "xp": 25, "or": 0},
    "Bandit": {"nom": "Bandit", "pv": 18, "force": 5, "agilite": 6, "armure": 2, "arme": 3, "xp": 30, "or": 10},
    "Porteur de Cendres": {"nom": "Porteur de Cendres", "pv": 16, "force": 5, "agilite": 4, "armure": 2, "arme": 3, "xp": 40, "or": 4},
    "Garde Cendreux": {"nom": "Garde Cendreux", "pv": 38, "force": 8, "agilite": 4, "armure": 4, "arme": 4, "xp": 80, "or": 8},
    "Bourreau des Cendres": {"nom": "Bourreau des Cendres", "pv": 120, "force": 12, "agilite": 5, "armure": 8, "arme": 7, "xp": 180, "or": 0},
    "Morvayn": {"nom": "Morvayn le Porte-Cendre", "pv": 180, "force": 18, "agilite": 16, "armure": 10, "arme": 10, "xp": 2500, "or": 500},
    "Chasseur du Cristal": {"nom": "Chasseur du Cristal", "pv": 30, "force": 10, "agilite": 6, "armure": 5, "arme": 6, "xp": 130, "or": 9},
    "Soldat de Malakar": {"nom": "Soldat de Malakar", "pv": 55, "force": 12, "agilite": 7, "armure": 7, "arme": 6, "xp": 180, "or": 10},
    "Suppôt du Dévoreur": {"nom": "Suppôt du Dévoreur", "pv": 85, "force": 15, "agilite": 7, "armure": 8, "arme": 7, "xp": 280, "or": 0},
}

LOOTS = {
    "Rat Corrompu": [None, "Ration", "Bague de cuivre ancienne"],
    "Gobelin": [None, "Potion de soin", "Dague rouillée"],
    "Squelette": [None, "Pierre Spectrale", "Clé antique"],
    "Bandit": [None, "Potion de soin", "Carte du marché noir"],
    "Porteur de Cendres": [None, "Flèche noire cendreuse", "Potion de soin"],
    "Garde Cendreux": [None, "Clé des geôles", "Potion supérieure"],
    "Bourreau des Cendres": ["Hache des Cendres", "Boucle d'Acier"],
    "Morvayn": ["Fragment Temporel Majeur", "Sceau des Porteurs"],
    "Chasseur du Cristal": [None, "Potion supérieure"],
    "Gardien du Cristal": ["Plaques", "Relique du Dernier Serment"],
    "Soldat de Malakar": [None, "Potion supérieure", "Œil de Cristal"],
    "Champion de guerre": ["Mithril", "Carquois du Grand Chasseur", "Talisman du Chasseur"],
    "Suppôt du Dévoreur": [None, "Potion supérieure"],
    "Manifestation du Dévoreur": ["Sceptre du Dévoreur", "Voile du Sceau", "Grimoire du Dévoreur", "Pendentif du Sacrifice"],
    "Avatar de Malakar": ["Tranche-Sceau", "Arc du Jugement", "Égide du Dernier Âge"],
}

COMPAGNONS_STATS = {
    "Lyra": {"pv": 22, "force": 4, "degats": 3},
    "Borin": {"pv": 30, "force": 5, "degats": 4},
    "Selene": {"pv": 18, "force": 2, "degats": 5},
    "Kael": {"pv": 20, "force": 5, "degats": 3},
    "Elara": {"pv": 16, "force": 1, "degats": 2},
    "Garrick": {"pv": 24, "force": 4, "degats": 4},
    "Mira aux Corbeaux": {"pv": 18, "force": 3, "degats": 2},
}

MONDE = {
    "Brumebois": {"nord": "Montagnes Grises", "est": "Forêt d'Argelune", "sud": "Marécages de Vire-Saule"},
    "Aldorath": {"nord": "Montagnes d'Ashkar", "bas-quartiers": "Basse-Ville", "port": "Port d'Arken"},
    "Montagnes d'Ashkar": {"sud": "Aldorath", "donjon": "Forteresse de Givre"},
}

COMPAGNONS_DISPONIBLES = ["Lyra", "Borin", "Selene", "Kael", "Elara"]

LOYautes_DEPART = {
    "Lyra": 0,
    "Borin": 0,
    "Selene": 0,
    "Kael": 0,
    "Mira aux Corbeaux": 0,
    "Elara": 0,
    "Morvayn": -100,
}

VARIABLES_DEPART = {
    "garrick_recherche": False,
    "garrick_localise": False,
    "garrick_sauve": False,
    "secret_arthen": 0,
    "secret_malakar": 0,
    "secret_morvayn": 0,
    "morvayn_alerte": False,
    "elara_sauvee": False,
    "ancien_allie": False,
    "prisonnier_libere": False,
    "bourreau_capture": False,
    "alliance_choisie": None,
    "cristal_prioritaire": None,
    "morvayn_epargne": False,
    "morvayn_tue": False,
    "morvayn_recrute": False,
}

INFLUENCES_POLITIQUES = {
    "Militaire": 0,
    "Religieuse": 0,
    "Politique": 0,
}

ACTES_CAMPAGNE = [
    ("Acte I", "L'Éveil", "Niveaux 1 à 10", "Découvrir votre véritable identité."),
    ("Acte II", "Les Royaumes Déchirés", "Niveaux 10 à 20", "Survivre aux intrigues d'Aldor, Varken et Ellorien."),
    ("Acte III", "La Chasse aux Cristaux", "Niveaux 20 à 35", "Récupérer les Cristaux Primordiaux sans condamner le monde."),
    ("Acte IV", "La Guerre du Crépuscule", "Niveaux 35 à 45", "Commander alliés, forteresse et armées contre l'invasion."),
    ("Acte V", "Le Dernier Âge", "Niveaux 45 à 50", "Affronter l'effondrement du Temps et le Dévoreur des Âges."),
]

FACTIONS = {
    "Aldor": 0,
    "Ligue de Varken": 0,
    "Cités Libres": 0,
    "Royaumes Nains": 0,
    "Ellorien": 0,
    "Serviteurs de Malakar": 0,
}

COMPAGNONS_DETAILS = {
    "Lyra": "Archère elfe chargée d'observer le Porteur et de l'éliminer s'il devient dangereux.",
    "Borin": "Prince nain déchu dont le secret familial menace une guerre civile.",
    "Selene": "Sorcière qui connaît l'existence du Dévoreur des Âges.",
    "Kael": "Assassin chargé de vous surveiller si votre pouvoir grandit trop vite.",
    "Elara": "Érudite des Porteurs sauvée dans les Cellules Oubliées.",
}

# Échanges déclenchés au camp quand les deux compagnons de la paire sont présents à la fois.
BANTERS_COMPAGNONS = {
    frozenset({"Lyra", "Garrick"}): "\"Tu le couves comme si c'était encore un enfant\", glisse Lyra. Garrick ne lève pas les yeux de son fourreau : \"Et toi, tu le surveilles comme si c'était encore une cible. On protège tous les deux la même chose, à notre façon.\"",
    frozenset({"Lyra", "Borin"}): "\"Les elfes ne dorment jamais vraiment, il paraît\", lance Borin en s'installant près du feu. \"Les nains ronflent assez fort pour réveiller une montagne\", répond Lyra sans ouvrir les yeux. Ils finissent par rire tous les deux.",
    frozenset({"Garrick", "Borin"}): "Garrick examine la hache de Borin d'un œil de forgeron. \"Nain-forgée ?\" \"Volée, en fait\", admet Borin. \"Mais je l'ai bien entretenue.\" Garrick hoche la tête, presque impressionné malgré lui.",
    frozenset({"Lyra", "Kael"}): "Kael s'assoit un peu trop loin du feu pour que ce soit un hasard. \"Tu m'observes encore ?\", demande Lyra sans se retourner. \"Vieille habitude\", répond-il. \"J'essaie d'arrêter.\"",
    frozenset({"Selene", "Garrick"}): "\"Le feu de forge et le feu arcanique ne brûlent pas pareil\", remarque Selene en regardant Garrick travailler. \"Le mien ne ment pas, au moins\", répond-il sans lever les yeux — mais il la laisse s'approcher de l'enclume.",
    frozenset({"Kael", "Borin"}): "\"Un assassin et un prince déchu\", raconte Borin en versant deux gobelets. \"On ferait une sacrée histoire à raconter, si on survit assez pour la raconter.\" Kael accepte le gobelet sans un mot, ce qui, chez lui, vaut un sourire.",
    frozenset({"Elara", "Selene"}): "Les deux érudites comparent leurs notes toute la soirée, à voix basse, s'interrompant sans cesse l'une l'autre. \"Vous vous trompez sur Arthen\", finit par dire Selene. \"Vous aussi\", répond Elara, radieuse.",
    frozenset({"Mira aux Corbeaux", "Lyra"}): "\"Vous le suivez tous les deux comme des ombres\", remarque Mira en resserrant un bandage. \"La différence\", dit Lyra, \"c'est que je le protège de loin. Vous, vous le grondez de près.\"",
    frozenset({"Selene", "Kael"}): "\"Vous savez ce qu'est le Dévoreur des Âges ?\", demande Kael à voix basse. Selene hésite, puis répond : \"Je sais surtout qu'on ne devrait jamais prononcer son nom près du feu. Trop de choses écoutent.\"",
    frozenset({"Elara", "Borin"}): "\"Les Porteurs, les nains déchus... on collectionne les secrets encombrants dans ce groupe\", plaisante Elara. \"Au moins les miens ont un bon goût pour l'hydromel\", répond Borin en trinquant avec elle.",
}

FINS_MAJEURES = [
    "Fin du Héros",
    "Fin du Roi",
    "Fin du Gardien",
    "Fin du Tyran",
    "Fin du Sacrifice",
    "Fin Secrète",
    "Fin d'Ashkar Préservée",
    "Fin de la Coalition Brisée",
    "Fin des Cristaux Scellés",
    "Fin du Geôlier Maintenu",
]

QUETES_PRINCIPALES = [
    "Préserver vos liens à Brumebois",
    "Quitter Brumebois",
    "Retrouver Garrick",
    "Survivre aux Porteurs de Cendres",
    "Trouver le Cristal de Vie",
    "Découvrir qui sert Malakar",
    "Localiser les fragments du Temps",
    "Découvrir votre véritable identité",
    "Comprendre la prophétie du Septième Sceau",
    "Atteindre Val-Therys",
    "Découvrir le Sanctuaire Oublié",
    "Entrer à Aldorath",
    "Trouver une piste sur Garrick",
    "Choisir un premier allié politique",
    "Survivre à l'attentat de Morvayn",
    "Enquêter sur les Disparus d'Aldorath",
    "Découvrir pourquoi Garrick a été capturé",
    "Obtenir l'Œil d'Aeternis",
    "Démasquer les mensonges de la cour",
    "Assister à la Nuit des Masques",
    "Découvrir le Sang des Porteurs",
    "Affronter Morvayn à la Tour du Soleil",
]

RECETTES_FORGE = {
    "Épée Scintillante": {"base": "Épée Longue", "composants": {"Éclat de Cristal": 1, "Minerai de Fer": 1}},
    "Arc de Brume": {"base": "Arc court", "composants": {"Éclat de Cristal": 1, "Cuir de Qualité": 2}},
    "Armure Renforcée": {"base": "Armure de cuir", "composants": {"Minerai de Fer": 2, "Cuir de Qualité": 1}},
}

__all__ = [
    "RECETTES_FORGE",

    "SAUVEGARDE_FICHIER",
    "CLASSES",
    "DIFFICULTES",
    "DIFFICULTE_BONUS_RARETE",
    "XP_ENNEMIS",
    "ARMES",
    "AFFINITES_CLASSE",
    "ARMURES",
    "BOUCLIERS",
    "PRIX_BASE_ARMES",
    "PRIX_BASE_ARMURES",
    "PRIX_BASE_BOUCLIERS",
    "BIJOUX",
    "PRIX_BASE_BIJOUX",
    "COMPETENCES",
    "ARBRE_TALENTS",
    "CAPACITES_SPECIALES",
    "ENNEMIS",
    "LOOTS",
    "COMPAGNONS_STATS",
    "MONDE",
    "COMPAGNONS_DISPONIBLES",
    "LOYautes_DEPART",
    "VARIABLES_DEPART",
    "INFLUENCES_POLITIQUES",
    "ACTES_CAMPAGNE",
    "FACTIONS",
    "COMPAGNONS_DETAILS",
    "BANTERS_COMPAGNONS",
    "FINS_MAJEURES",
    "QUETES_PRINCIPALES",
]
