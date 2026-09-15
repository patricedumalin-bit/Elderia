CODEX_ENTRIES = {
    "brumebois": {
        "categorie": "Lieux",
        "titre": "Brumebois",
        "texte": "Village d'origine du Porteur, devenu le premier foyer perdu de la campagne.",
    },
    "garrick": {
        "categorie": "Personnages",
        "titre": "Garrick",
        "texte": "Forgeron, mentor et gardien de secrets liés aux Porteurs et aux Veilleurs.",
    },
    "lyra": {
        "categorie": "Personnages",
        "titre": "Lyra",
        "texte": "Archère d'Ellorien envoyée pour surveiller le Porteur, puis possible garde-fou humain.",
    },
    "morvayn": {
        "categorie": "Personnages",
        "titre": "Morvayn",
        "texte": "Porteur déchu lié aux Cendres, à Malakar et aux cycles brisés du Temps.",
    },
    "dragon_etoile": {
        "categorie": "Lore",
        "titre": "Ordre du Dragon-Étoile",
        "texte": "Une confrérie antique vouée à la protection des Sceaux Temporels avant la Grande Fracture.",
    },

    "malakar": {
        "categorie": "Personnages",
        "titre": "Malakar",
        "texte": "Tyran et geôlier du Sceau, moins origine du mal que gardien corrompu d'une peur ancienne.",
    },
    "val_therys": {
        "categorie": "Lieux",
        "titre": "Val-Therys",
        "texte": "Ancienne capitale figée par les fractures du Temps et les erreurs des cycles passés.",
    },
    "aldorath": {
        "categorie": "Lieux",
        "titre": "Aldorath",
        "texte": "Cité des Trois Couronnes, coeur politique des royaumes déchirés.",
    },
    "ashkar": {
        "categorie": "Lieux",
        "titre": "Ashkar",
        "texte": "Montagne vivante nourrie par le Cristal de Vie et blessée par la Chasse aux Cristaux.",
    },
    "cristal_vie": {
        "categorie": "Cristaux",
        "titre": "Cristal de Vie",
        "texte": "Cristal majeur qui soigne autant qu'il affame lorsqu'on le retire à la terre qu'il nourrit.",
    },
    "cristaux": {
        "categorie": "Cristaux",
        "titre": "Les Cristaux Primordiaux",
        "texte": "Pouvoirs anciens liés aux terres, aux peuples et à la prison du Dévoreur des Âges.",
    },
    "porteurs": {
        "categorie": "Mystères",
        "titre": "Les Porteurs",
        "texte": "Lignée de verrous vivants appelée lorsque les Cristaux ne suffisent plus à maintenir le Sceau.",
    },
    "veilleurs": {
        "categorie": "Mystères",
        "titre": "Les Veilleurs",
        "texte": "Ordre disparu qui tenta de garder les Cristaux, les Porteurs et le Sceau hors des royaumes.",
    },
    "devoreur": {
        "categorie": "Mystères",
        "titre": "Le Dévoreur des Âges",
        "texte": "Présence derrière le Temps, enfermée par le Sceau et crainte même par Malakar.",
    },
}


SOUVENIRS_ENTRIES = {
    "pain_mira": "Le pain chaud de Mira",
    "main_garrick": "La main de Garrick sur votre épaule",
    "rire_marek": "Le rire trop fort de Marek",
    "premiere_flambebleue": "La flamme bleue de Brumebois",
    "regard_lyra": "Le regard de Lyra au Pont des Corbeaux",
    "masque_morvayn": "Le masque rouge de Morvayn",
    "lampe_ashkar": "La lanterne verte d'Ashkar",
    "cicatrice_ashkar": "La cicatrice d'Ashkar",
    "trois_bannieres": "La plaine des Trois Bannières",
    "voix_finales": "Les dernières voix avant le Sceau",
    "autre_age": "Le souvenir d'un autre âge",
}


def decouvrir_codex(joueur, identifiant):
    if identifiant not in CODEX_ENTRIES:
        return False
    if not hasattr(joueur, "codex"):
        joueur.codex = {}
    if identifiant in joueur.codex:
        return False
    joueur.codex[identifiant] = dict(CODEX_ENTRIES[identifiant])
    joueur.journal.append(f"Chronique découverte : {CODEX_ENTRIES[identifiant]['titre']}.")
    return True


def ajouter_souvenir(joueur, identifiant):
    if identifiant not in SOUVENIRS_ENTRIES:
        return False
    if not hasattr(joueur, "souvenirs"):
        joueur.souvenirs = []
    souvenir = SOUVENIRS_ENTRIES[identifiant]
    if souvenir in joueur.souvenirs:
        return False
    joueur.souvenirs.append(souvenir)
    joueur.journal.append(f"Souvenir persistant : {souvenir}.")
    return True


def progression_codex(joueur):
    return len(getattr(joueur, "codex", {})), len(CODEX_ENTRIES)


def progression_souvenirs(joueur):
    return len(getattr(joueur, "souvenirs", [])), len(SOUVENIRS_ENTRIES)


def afficher_chronique(joueur):
    print("\nCHRONIQUE")
    courant, total = progression_codex(joueur)
    print(f"Entrées découvertes : {courant} / {total}")
    categories = {}
    for entree in getattr(joueur, "codex", {}).values():
        categories.setdefault(entree["categorie"], []).append(entree)
    if not categories:
        print("- Aucune entrée découverte")
    for categorie, entrees in categories.items():
        print(f"{categorie} :")
        for entree in sorted(entrees, key=lambda item: item["titre"]):
            print(f"- {entree['titre']} : {entree['texte']}")

    print("\nSOUVENIRS PERSISTANTS")
    courant, total = progression_souvenirs(joueur)
    print(f"Souvenirs retrouvés : {courant} / {total}")
    if getattr(joueur, "souvenirs", []):
        for souvenir in joueur.souvenirs:
            print(f"- {souvenir}")
    else:
        print("- Aucun souvenir persistant")