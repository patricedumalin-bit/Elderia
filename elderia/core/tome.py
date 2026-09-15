from elderia.core.io import afficher_titre, demander_choix, raconter
from elderia.core.save import charger, sauvegarder
from elderia.core.systems import afficher_prologue, afficher_structure_campagne, creer_personnage


XP_TOME_2 = {
    "Gardien du Cristal": 220,
    "Champion de guerre": 300,
    "Avatar de Malakar": 500,
}

CRISTAUX_MAJEURS = [
    "Cristal de Vie",
    "Cristal des Ombres",
    "Cristal des Esprits",
    "Cristal du Feu",
    "Cristal des Marées",
    "Cristal de la Terre",
]


def valider_quete(joueur, quete):
    if hasattr(joueur, "terminer_quete"):
        joueur.terminer_quete(quete)
    else:
        joueur.quetes[quete] = True


def ajouter_score(joueur, attribut, valeur):
    courant = getattr(joueur, attribut, 0)
    setattr(joueur, attribut, courant + valeur)


def chapitre_final(joueur):
    raconter("\nLa nuit tombe sur Elderia. Vos premiers choix ont déjà changé la forme du monde.")
    joueur.afficher_fiche_personnage()

    if joueur.pv <= 0:
        raconter("\nFIN 1 : L'Échec. Malakar gagne, et le monde sombre.")
    elif joueur.acte_courant.startswith("Acte III"):
        raconter("\nFIN PROVISOIRE : Les Royaumes Déchirés. Aldorath survit au couronnement, Garrick est vivant au nord, Morvayn était un Porteur, et l'Acte III peut commencer.")
    elif joueur.acte_courant.startswith("Acte II"):
        raconter("\nFIN PROVISOIRE : L'Éveil accompli. Vous quittez l'Acte I avec le nom d'Arthen, Lyra à vos côtés, et le continent devant vous.")
    elif "Les anciens associent le Septième Sceau au Dévoreur des Âges." in joueur.secrets:
        raconter("\nFIN PROVISOIRE : Le Grand Secret. Vous savez déjà que Malakar craint une puissance plus ancienne que lui.")
    elif joueur.fragments_temps >= 3 and "Cristal de Vie" in joueur.cristaux:
        raconter("\nFIN PROVISOIRE : Le Sauveur en marche. Vous avez récupéré le Cristal de Vie et plusieurs fragments du Temps.")
    elif joueur.alignement <= -3:
        raconter("\nFIN PROVISOIRE : Le Tyran possible. Les ombres d'Elderia commencent à répondre à votre nom.")
    elif joueur.reputation >= 2:
        raconter("\nFIN PROVISOIRE : Le Roi d'Elderia. Les peuples libres murmurent déjà votre légende.")
    else:
        raconter("\nFIN PROVISOIRE : La Quête Continue. Malakar attend encore, et six Cristaux restent à sauver.")


def chapitre_final_tome_2(joueur):
    raconter("\nLes chroniques ferment leur dernier chapitre jouable.")
    joueur.afficher_fiche_personnage()
    if joueur.pv <= 0:
        raconter("\nFIN : Le Temps se referme sur votre défaite.")
    else:
        raconter(f"\n{getattr(joueur, 'fin_majeure', 'FIN PROVISOIRE')} : Elderia entre dans un nouvel âge.")


def jouer_tome_1(afficher_fin=True):
    afficher_titre()
    afficher_prologue()
    afficher_structure_campagne()
    joueur = creer_personnage()
    joueur.afficher_fiche_personnage()
    from elderia.acts import act_1, act_2

    act_1.jouer(joueur, sauvegarder=False)
    if joueur.pv > 0 and joueur.acte_courant.startswith("Acte II"):
        act_2.jouer(joueur, sauvegarder=False)

    if afficher_fin:
        chapitre_final(joueur)
        sauvegarder(joueur)
        print("\n--- FIN DU TOME I : ACTES I-II ---")
    return joueur


def preparer_heros_acte_3():
    afficher_titre()
    raconter("\nTOME II : Les Cristaux, la Guerre et le Dernier Âge")
    joueur = creer_personnage()
    joueur.acte_courant = "Acte III - La Chasse aux Cristaux"
    joueur.niveau = max(joueur.niveau, 10)
    joueur.xp = max(joueur.xp, 1000)
    joueur.pv_max = joueur.calculer_pv_max()
    joueur.pv = joueur.pv_max
    joueur.energie = joueur.energie_max
    joueur.pm = joueur.pm_max
    joueur.compagnons.extend([compagnon for compagnon in ["Lyra", "Borin"] if compagnon not in joueur.compagnons])
    joueur.fragments_temps = max(joueur.fragments_temps, 3)
    if "Œil d'Aeternis" not in joueur.artefacts:
        joueur.artefacts.append("Œil d'Aeternis")
    joueur.allie_politique = joueur.allie_politique or "Aldor"
    joueur.journal.append("Résumé : après Aldorath, la chasse aux Cristaux commence dans les Montagnes d'Ashkar.")
    return joueur


def obtenir_joueur_depart():
    print("\nComment voulez-vous commencer le Tome II ?")
    options = [
        "Continuer en jouant d'abord le Tome I complet",
        "Démarrer directement avec un héros préparé pour l'Acte III",
        "Charger save.json",
    ]
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    choix = demander_choix("> ", options)
    if choix == 0:
        return jouer_tome_1(afficher_fin=False)
    if choix == 1:
        return preparer_heros_acte_3()
    joueur = charger()
    if joueur is None:
        return preparer_heros_acte_3()
    if not joueur.acte_courant.startswith("Acte III"):
        joueur.acte_courant = "Acte III - La Chasse aux Cristaux"
    return joueur


def executer_tome_2():
    from elderia.acts import act_3, act_4, act_5

    joueur = obtenir_joueur_depart()
    if joueur.pv > 0 and joueur.acte_courant.startswith("Acte III"):
        act_3.jouer(joueur, sauvegarder=False)
    if joueur.pv > 0 and joueur.acte_courant.startswith("Acte IV"):
        act_4.jouer(joueur, sauvegarder=False)
    if joueur.pv > 0 and joueur.acte_courant.startswith("Acte V"):
        act_5.jouer(joueur, sauvegarder=False)
    chapitre_final_tome_2(joueur)
    print("\n--- FIN DU TOME II : ACTES III-V ---")


def executer_jeu():
    jouer_tome_1()
