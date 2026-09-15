import random

from elderia.data.tables import (
    ARMES,
    ARMURES,
    BOUCLIERS,
    BIJOUX,
    BONUS_RARETE_PAR_PALIER,
    DIFFICULTE_BONUS_RARETE,
    PREFIXES_ARMES,
    PREFIXES_ARMURES,
    PREFIXES_BIJOUX,
    PREFIXES_BOUCLIERS,
    PREFIXES_CARQUOIS,
    PREFIXES_GRIMOIRES,
    PREFIXES_RELIQUES,
    PRIX_BASE_ARMES,
    PRIX_BASE_ARMURES,
    PRIX_BASE_BOUCLIERS,
    PRIX_BASE_BIJOUX,
    RARETES,
    RARETES_AUTORISEES_PAR_PALIER,
)

# Plancher appliqué après un modificateur d'affixe (évite une arme à 0 dégât, etc.).
_PLANCHERS = {"degats": 1, "reduction": 0, "defense": 0, "blocage": 0, "bonus_force": 0, "bonus_intelligence": 0, "valeur": 1}


def palier_ennemi(ennemi):
    """Classe un ennemi par dangerosité (via son xp) pour moduler ses chances de bon loot."""
    xp = ennemi.get("xp", 0) if isinstance(ennemi, dict) else 0
    if xp >= 300:
        return "boss"
    if xp >= 100:
        return "elite"
    return "mineur"


def _tirer_affixe(prefixes, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    autorisees = RARETES_AUTORISEES_PAR_PALIER.get(palier, RARETES_AUTORISEES_PAR_PALIER["mineur"])
    candidats = [prefixe for prefixe in prefixes if prefixe[2] in autorisees]
    bonus_palier = BONUS_RARETE_PAR_PALIER.get(palier, BONUS_RARETE_PAR_PALIER["mineur"])
    bonus_difficulte = DIFFICULTE_BONUS_RARETE.get(difficulte, DIFFICULTE_BONUS_RARETE["Normal"])
    poids = [
        RARETES[rarete]["poids"] * bonus_palier.get(rarete, 1.0) * bonus_difficulte.get(rarete, 1.0)
        * (1 + bonus_rarete if rarete != "Commun" else 1.0)
        for (_, _, rarete) in candidats
    ]
    return random.choices(candidats, weights=poids, k=1)[0]


def _appliquer_variante(nom_base, table, prefixes, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    label, modificateurs, rarete = _tirer_affixe(prefixes, palier, difficulte, bonus_rarete)
    if not label:
        return nom_base, "Commun"
    nom_variante = f"{nom_base} [{rarete} : {label}]"
    if nom_variante not in table:
        stats = dict(table[nom_base])
        for cle, delta in modificateurs.items():
            valeur = stats.get(cle, 0) + delta
            plancher = _PLANCHERS.get(cle)
            stats[cle] = max(plancher, valeur) if plancher is not None else valeur
        table[nom_variante] = stats
    return nom_variante, rarete


def generer_variante_arme(nom_base, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    return _appliquer_variante(nom_base, ARMES, PREFIXES_ARMES, palier, difficulte, bonus_rarete)


def generer_variante_armure(nom_base, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    return _appliquer_variante(nom_base, ARMURES, PREFIXES_ARMURES, palier, difficulte, bonus_rarete)


def generer_variante_bouclier(nom_base, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    """Les objets de seconde main non-boucliers (grimoire, carquois, relique) piochent leurs
    affixes dans une table dédiée à leur catégorie, pour faire varier leur statistique signature."""
    categorie = BOUCLIERS[nom_base].get("categorie", "lourde")
    prefixes = _PREFIXES_SECONDAIRE_PAR_CATEGORIE.get(categorie, PREFIXES_BOUCLIERS)
    return _appliquer_variante(nom_base, BOUCLIERS, prefixes, palier, difficulte, bonus_rarete)


def generer_variante_bijou(nom_base, palier="mineur", difficulte="Normal", bonus_rarete=0.0):
    return _appliquer_variante(nom_base, BIJOUX, PREFIXES_BIJOUX, palier, difficulte, bonus_rarete)


_PREFIXES_SECONDAIRE_PAR_CATEGORIE = {
    "distance": PREFIXES_CARQUOIS,
    "arcane": PREFIXES_GRIMOIRES,
    "legere": PREFIXES_RELIQUES,
}



def prix_avec_rarete(prix, rarete):
    if not prix:
        return prix
    return max(1, round(prix * RARETES[rarete]["multiplicateur_prix"]))


def generer_stock(stock_base, palier="mineur", difficulte="Normal"):
    """Régénère une liste d'articles marchand avec des variantes tirées au sort et un prix ajusté à la rareté."""
    articles = []
    for nom, prix in stock_base:
        if nom in ARMES:
            nom_final, rarete = generer_variante_arme(nom, palier, difficulte)
        elif nom in ARMURES:
            nom_final, rarete = generer_variante_armure(nom, palier, difficulte)
        elif nom in BOUCLIERS:
            nom_final, rarete = generer_variante_bouclier(nom, palier, difficulte)
        elif nom in BIJOUX:
            nom_final, rarete = generer_variante_bijou(nom, palier, difficulte)
        else:
            nom_final, rarete = nom, "Commun"
        articles.append((nom_final, prix_avec_rarete(prix, rarete)))
    return articles


def _nom_de_base_et_rarete(nom_objet):
    """Extrait le nom canonique et la rareté d'un objet, variante ou non (ex: 'Excalion [Épique : Légendaire]')."""
    if "[" not in nom_objet:
        return nom_objet, "Commun"
    nom_base, reste = nom_objet.split(" [", 1)
    rarete = reste.split(" :")[0].split("]")[0]
    return nom_base, rarete if rarete in RARETES else "Commun"


def prix_revente(nom_objet):
    """Prix de revente d'un objet (arme/armure/bouclier/bijou) : 1/4 de son prix plein, rareté comprise."""
    nom_base, rarete = _nom_de_base_et_rarete(nom_objet)
    if nom_base in PRIX_BASE_ARMES:
        base = PRIX_BASE_ARMES[nom_base]
    elif nom_base in PRIX_BASE_ARMURES:
        base = PRIX_BASE_ARMURES[nom_base]
    elif nom_base in PRIX_BASE_BOUCLIERS:
        base = PRIX_BASE_BOUCLIERS[nom_base]
    elif nom_base in PRIX_BASE_BIJOUX:
        base = PRIX_BASE_BIJOUX[nom_base]
    else:
        return 0
    prix_plein = round(base * RARETES[rarete]["multiplicateur_prix"])
    return prix_plein // 4


def objets_vendables(joueur):
    """Équipements (arme/armure/bouclier/bijou) possédés mais non équipés, vendables chez le marchand."""
    vendables = []
    for objet in dict.fromkeys(joueur.inventaire):
        if objet in (joueur.arme, joueur.armure, joueur.bouclier_equipe, joueur.bijou_equipe):
            continue
        nom_base, _ = _nom_de_base_et_rarete(objet)
        if (
            nom_base in PRIX_BASE_ARMES
            or nom_base in PRIX_BASE_ARMURES
            or nom_base in PRIX_BASE_BOUCLIERS
            or nom_base in PRIX_BASE_BIJOUX
        ):
            vendables.append(objet)
    return vendables
