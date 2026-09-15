import os

from elderia.core.io import afficher_titre, demander_choix, lancer_de, raconter
from elderia.core.crafting import peut_forger, visiter_forge
from elderia.core.equipment import generer_stock, objets_vendables, prix_revente
from elderia.core.models import Joueur
from elderia.core.save import charger
from elderia.data.tables import (
    ACTES_CAMPAGNE,
    ARMES,
    ARMURES,
    BOUCLIERS,
    BIJOUX,
    CLASSES,
    DIFFICULTES,
    MONDE,
    RECETTES_FORGE,
    SAUVEGARDE_FICHIER,
)

# Composants de forge vendus systématiquement chez le marchand (ex: "Éclat de Cristal" n'était sinon
# obtenable que via un événement aléatoire à 40% de chance sur 4 rencontres de toute la partie).
COMPOSANTS_FORGE_CONNUS = {comp for data in RECETTES_FORGE.values() for comp in data["composants"]}

# Stats sur lesquelles chaque origine donne l'avantage (relance, garde le meilleur jet) à TOUS les tests
# de la partie (pas seulement à la scène d'introduction) - c'est ce qui donne vraiment du poids au choix
# d'origine tout au long de l'aventure.
ORIGINES_AVANTAGE = {
    "Noble Déchu": {"charisme", "intelligence"},
    "Enfant des Rues": {"agilite"},
    "Ancien Soldat": {"force", "volonte"},
    "Érudit Errant": {"intelligence", "volonte"},
}

def tester_stat(joueur, statistique, difficulte, avantage=False, desavantage=False):
    aliases = {"magie": "intelligence"}
    attribut = aliases.get(statistique) or statistique
    valeur = getattr(joueur, attribut)

    if attribut in ORIGINES_AVANTAGE.get(joueur.origine, ()):
        avantage = True

    # [WARHAMMER] Désavantage permanent si corruption trop haute sur certains tests
    if statistique == "charisme" and joueur.corruption >= 20:
        desavantage = True

    jet = lancer_de(20, avantage=avantage, desavantage=desavantage)
    resultat = jet + valeur

    if jet == 20:
        raconter("🌟 [RÉUSSITE CRITIQUE] !")
        return True
    if jet == 1:
        raconter("💀 [ÉCHEC CRITIQUE] !")
        return False

    effet_bijou, valeur_bijou = joueur.effet_bijou
    if effet_bijou == "bonus_test_stat":
        resultat += valeur_bijou
    if joueur.a_talent("Vision Temporelle") and joueur.talent_vision_utilisee != joueur.acte_courant:
        joueur.talent_vision_utilisee = joueur.acte_courant
        resultat += 5
        raconter("🔮 Vision Temporelle : +5 à ce test (une fois par chapitre).")
    reussite = resultat >= difficulte
    if not reussite and joueur.a_talent("Vision d'Avenir") and joueur.talent_relance_utilisee != joueur.acte_courant:
        joueur.talent_relance_utilisee = joueur.acte_courant
        raconter("⏳ Vision d'Avenir : vous relancez ce test (une fois par chapitre).")
        jet = lancer_de(20)
        resultat = jet + valeur + (valeur_bijou if effet_bijou == "bonus_test_stat" else 0)
        reussite = resultat >= difficulte
    raconter(f"Test de {statistique} : {resultat} contre {difficulte}.")
    return reussite

MARCHAND_STOCK_ACTE_1 = [
    ("Épée d'acier", 18),
    ("Arc elfique", 20),
    ("Bâton runique", 22),
    ("Cotte de mailles", 16),
    ("Bouclier renforcé", 10),
    ("Grimoire des Cendres", 20),
    ("Carquois de précision", 15),
    ("Relique bénie", 18),
    ("Anneau de Vigueur", 20),
    ("Grelot du Marchand", 20),
    ("Potion de soin", 5),
    ("Éclat de Cristal", 25),
    ("Minerai de Fer", 15),
    ("Cuir de Qualité", 10),
    ("Quitter", 0),
]

MARCHAND_STOCK_ACTE_2 = [
    ("Hache des Cendres", 45),
    ("Armure Royale", 40),
    ("Bouclier renforcé", 15),
    ("Grimoire des Cendres", 25),
    ("Carquois de précision", 20),
    ("Relique bénie", 25),
    ("Amulette des Cendres", 25),
    ("Boucle d'Acier", 25),
    ("Larme d'Ashkar", 20),
    ("Potion supérieure", 12),
    ("Éclat de Cristal", 25),
    ("Minerai de Fer", 15),
    ("Cuir de Qualité", 10),
    ("Quitter", 0),
]

MARCHAND_STOCK_ACTE_3 = [
    ("Plaques", 60),
    ("Cape elfique", 55),
    ("Bouclier royal", 35),
    ("Grimoire du Dévoreur", 45),
    ("Carquois du Grand Chasseur", 35),
    ("Relique du Dernier Serment", 50),
    ("Talisman du Chasseur", 30),
    ("Charme du Fuyard", 25),
    ("Potion supérieure", 12),
    ("Éclat de Cristal", 25),
    ("Minerai de Fer", 15),
    ("Cuir de Qualité", 10),
    ("Quitter", 0),
]

MARCHAND_STOCK_ACTE_4 = [
    ("Excalion", 90),
    ("Mithril", 80),
    ("Armure du Titan", 75),
    ("Bouclier royal", 40),
    ("Grimoire du Dévoreur", 55),
    ("Carquois du Grand Chasseur", 45),
    ("Relique du Dernier Serment", 60),
    ("Sceau de Fortune", 35),
    ("Pendentif du Sacrifice", 30),
    ("Œil de Cristal", 30),
    ("Potion supérieure", 12),
    ("Éclat de Cristal", 25),
    ("Minerai de Fer", 15),
    ("Cuir de Qualité", 10),
    ("Quitter", 0),
]


def vendre_objet(joueur):
    vendables = objets_vendables(joueur)
    if not vendables:
        raconter("Vous n'avez aucun équipement non porté à vendre.")
        return
    options = [f"{objet} ({prix_revente(objet)}g)" for objet in vendables] + ["Annuler"]
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    choix = demander_choix("Vendre > ", options, interaction=True)
    if choix == len(vendables):
        return
    objet = vendables[choix]
    gain = prix_revente(objet)
    joueur.inventaire.remove(objet)
    joueur.or_poches += gain
    raconter(f"Vous vendez {objet} pour {gain}g.")


def visiter_marchand(joueur, articles=None, intro=None, palier="mineur"):
    raconter(intro or "\nLe marchand de Brumebois entrouvre une caisse marquée du sceau royal.")
    articles = generer_stock(articles or MARCHAND_STOCK_ACTE_1, palier, joueur.difficulte)
    facteur_charisme = max(0.6, 1 - joueur.charisme * 0.01)
    if facteur_charisme < 1.0:
        articles = [(nom, max(1, round(prix * facteur_charisme)) if prix else prix) for nom, prix in articles]
    if joueur.a_talent("Influence Marchande"):
        articles = [(nom, max(1, round(prix * 0.8)) if prix else prix) for nom, prix in articles]
    effet_bijou, valeur_bijou = joueur.effet_bijou
    if effet_bijou == "reduction_prix":
        articles = [(nom, max(1, round(prix * (1 - valeur_bijou / 100))) if prix else prix) for nom, prix in articles]
    articles.insert(-1, ("Vendre un objet (1/4 prix)", 0))
    articles.insert(-1, ("Utiliser la Forge", 0))
    while True:
        print(f"\nVotre or : {joueur.or_poches}g")
        for index, (nom, prix) in enumerate(articles, 1):
            cout = f"{prix}g" if prix else ""
            if nom == "Utiliser la Forge" and not peut_forger(joueur):
                cout = "(aucune recette prête)"
            print(f"{index}. {nom} {cout}")
        choix = demander_choix("Acheter > ", articles, interaction=True)
        nom_article, prix = articles[choix]

        if nom_article == "Quitter":
            break
        if nom_article == "Vendre un objet (1/4 prix)":
            vendre_objet(joueur)
            continue
        if nom_article == "Utiliser la Forge":
            visiter_forge(joueur)
            continue
        if joueur.or_poches < prix:
            raconter("❌ Or insuffisant.")
            continue
        if nom_article in ARMES:
            if joueur.arme == nom_article:
                raconter("Vous possédez déjà cette arme.")
                continue
            if not joueur.ajouter_objet(nom_article):
                continue
            raconter(f"🛍️ Achat effectué : {nom_article}.")
            if joueur.arme_est_meilleure(nom_article):
                # On équipe l'arme en arrière-plan sans déclencher le double texte de modèles
                joueur.arme = nom_article
                joueur.actualiser_mana_max()
                raconter(f"{nom_article} équipée.")
            else:
                raconter(f"{nom_article} rejoint votre inventaire, mais votre équipement actuel reste plus efficace.")
        elif nom_article in ARMURES:
            if joueur.armure == nom_article:
                raconter("Vous portez déjà cette armure.")
                continue
            if not joueur.ajouter_objet(nom_article):
                continue
            raconter(f"🛍️ Achat effectué : {nom_article}.")
            if joueur.armure_est_meilleure(nom_article):
                joueur.armure = nom_article
                raconter(f"{nom_article} équipée.")
            else:
                raconter(f"{nom_article} rejoint votre inventaire, mais votre équipement actuel reste plus efficace.")
        elif nom_article in BOUCLIERS:
            if joueur.bouclier_equipe == nom_article:
                raconter("Vous possédez déjà ce bouclier.")
                continue
            if not joueur.ajouter_objet(nom_article):
                continue
            raconter(f"🛍️ Achat effectué : {nom_article}.")
            if joueur.bouclier_est_meilleure(nom_article):
                joueur.bouclier_equipe = nom_article
                raconter(f"{nom_article} équipé.")
            else:
                raconter(f"{nom_article} rejoint votre inventaire, mais votre équipement actuel reste plus efficace.")
        elif nom_article in BIJOUX:
            if joueur.bijou_equipe == nom_article:
                raconter("Vous possédez déjà ce bijou.")
                continue
            if not joueur.ajouter_objet(nom_article):
                continue
            raconter(f"🛍️ Achat effectué : {nom_article}.")
            if joueur.bijou_est_meilleur(nom_article):
                joueur.bijou_equipe = nom_article
                raconter(f"{nom_article} équipé.")
            else:
                raconter(f"{nom_article} rejoint votre inventaire, mais votre bijou actuel reste plus efficace.")
        elif nom_article in COMPOSANTS_FORGE_CONNUS:
            joueur.ajouter_composant(nom_article)
            raconter(f"🛍️ Achat effectué : {nom_article}.")
        else:
            if not joueur.ajouter_objet(nom_article):
                continue
            raconter(f"🛍️ Achat effectué : {nom_article}.")

        joueur.or_poches -= prix
        raconter(f"{nom_article} obtenu.")

def recruter_compagnon(joueur, nom, condition=True):
    if condition and nom not in joueur.compagnons:
        joueur.compagnons.append(nom)
        joueur.ajouter_consequence(f"{nom} peut influencer une intrigue majeure plus tard.")
        raconter(f"🤝 {nom} rejoint votre groupe.")

def ajouter_fragment_temps(joueur, nombre=1):
    joueur.fragments_temps = min(25, joueur.fragments_temps + nombre)
    if joueur.fragments_temps > 0:
        joueur.terminer_quete("Localiser les fragments du Temps")
    raconter(f"⏳ Fragment du Temps obtenu. Total : {joueur.fragments_temps}/25.")

def voyager(joueur, lieu_depart):
    destinations = MONDE.get(lieu_depart, {})
    if not destinations:
        raconter("Aucune route connue depuis ce lieu.")
        return lieu_depart
    routes = list(destinations.items())
    print(f"\nRoutes depuis {lieu_depart} :")
    for index, (direction, destination) in enumerate(routes, 1):
        print(f"{index}. {direction} -> {destination}")
    choix = demander_choix("Destination > ", routes, interaction=True)
    destination = routes[choix][1]
    joueur.journal.append(f"Voyage : {lieu_depart} -> {destination}.")
    raconter(f"Vous voyagez vers {destination}.")
    return destination


# --- CHAPITRES ---

def afficher_prologue():
    raconter("""
Avant la naissance des hommes, Elderia était gouvernée par les Dragons-Dieux.
Aurelion créa le soleil, Nythra fit naître les océans, Valgor façonna les montagnes,
Sylwen ouvrit le royaume des esprits, et Aeternis créa le Temps lui-même.

Pour qu'aucune créature ne domine les autres, leur pouvoir fut enfermé dans sept Cristaux Primordiaux.
Pendant des millénaires, les royaumes prospérèrent. Puis survint la Trahison.

Malakar, héros devenu mage noir, tenta de contrôler le Cristal du Temps.
Il blessa la réalité : des cités demeurent figées, des armées mortes reviennent,
des enfants vieillissent en quelques heures, et le monde commence à mourir.

Personne ne sait encore que votre existence est liée à cette prophétie.
""")

def afficher_structure_campagne():
    print("\nSTRUCTURE DES ACTES")
    for code, titre, niveaux, objectif in ACTES_CAMPAGNE:
        print(f"{code} - {titre} | {niveaux} | {objectif}")

def ecran_game_over(joueur):
    raconter(f"\n💀 {joueur.nom} succombe à ses blessures avant d'achever son destin.")
    if joueur.modificateurs["permadeath"]:
        raconter("☠️ Mode Hardcore : la mort est définitive. Aucune sauvegarde ne sera rechargée.")
        if os.path.exists(SAUVEGARDE_FICHIER):
            os.remove(SAUVEGARDE_FICHIER)
        return False
    options = ["Recharger la dernière sauvegarde", "Arrêter la partie ici"]
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    if demander_choix("Game Over > ", options, interaction=True) == 0:
        sauvegarde = charger()
        if sauvegarde is not None:
            joueur.__dict__.update(sauvegarde.__dict__)
            raconter("Vous reprenez votre aventure depuis la dernière sauvegarde.")
            return True
        raconter("Aucune sauvegarde disponible.")
    raconter("Votre légende s'arrête ici... pour cette tentative.")
    return False

def creer_personnage():
    nom = input("Quel est votre nom d'aventurier ?\n> ")
    print("\nChoisissez votre difficulté :")
    noms_difficultes = list(DIFFICULTES)
    descriptions = {
        "Facile": "Ennemis moins violents, XP et or bonifiés, PV renforcés.",
        "Normal": "Expérience équilibrée d'origine.",
        "Difficile": "Ennemis plus violents, récompenses réduites.",
        "Hardcore": "Ennemis très violents, récompenses réduites, mort définitive (pas de rechargement).",
    }
    for index, nom_difficulte in enumerate(noms_difficultes, 1):
        print(f"{index}. {nom_difficulte} — {descriptions.get(nom_difficulte, '')}")
    difficulte = noms_difficultes[demander_choix("> ", noms_difficultes)]
    print("\nChoisissez votre classe :")
    noms_classes = list(CLASSES)
    for index, nom_classe in enumerate(noms_classes, 1):
        donnees = CLASSES[nom_classe]
        pv = 14 + donnees["endurance"] * 2
        energie = 10 + donnees["volonte"]
        mana = donnees["intelligence"] * 2
        print(
            f"{index}. {nom_classe} | PV {pv} | Énergie {energie} | Mana {mana} | "
            f"FOR {donnees['force']} | AGI {donnees['agilite']} | END {donnees['endurance']} | "
            f"INT {donnees['intelligence']} | VOL {donnees['volonte']} | CHA {donnees['charisme']} | "
            f"Or {donnees['or']} | {donnees['competence']}"
        )
    classe = noms_classes[demander_choix("> ", noms_classes)]
    return Joueur(nom, classe, difficulte)
