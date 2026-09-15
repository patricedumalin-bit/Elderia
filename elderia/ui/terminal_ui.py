import json

from elderia.acts import act_1, act_2, act_3, act_4, act_5
from elderia.core.codex import CODEX_ENTRIES, SOUVENIRS_ENTRIES, ajouter_souvenir
from elderia.core.ending_variants import activer_nouvelle_route_plus
from elderia.core.io import demander_choix
from elderia.core.meta_progression import SUCCES_NARRATIFS
from elderia.core.options import OPTIONS_DEFAUT, appliquer_options, charger_options, sauvegarder_options
from elderia.core.save import charger, sauvegarder
from elderia.core.systems import creer_personnage
from elderia.data.tables import FINS_MAJEURES, SAUVEGARDE_FICHIER


ACTES = {
    1: act_1.jouer,
    2: act_2.jouer,
    3: act_3.jouer,
    4: act_4.jouer,
    5: act_5.jouer,
}


def choisir_acte():
    charger_options()
    print("\nLES CHRONIQUES D'ELDERIA")
    afficher_progression_fins()
    print("1. Acte I - L'Éveil")
    print("2. Acte II - Les Royaumes Déchirés")
    print("3. Acte III - La Chasse aux Cristaux")
    print("4. Acte IV - La Guerre du Crépuscule")
    print("5. Acte V - Le Dernier Âge")
    print("6. Chronique & progression")
    while True:
        try:
            choix = int(input("Acte à lancer > "))
            if choix in ACTES:
                return choix
            if choix == 6:
                afficher_menu_chronique_progression()
                return choisir_acte()
            print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un nombre.")


def lire_sauvegarde_meta():
    try:
        with open(SAUVEGARDE_FICHIER, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        return {}


def lire_fins_atteintes_sauvegarde():
    return list(lire_sauvegarde_meta().get("fins_atteintes", []))


def calculer_completion_meta(data):
    total = len(FINS_MAJEURES) + len(CODEX_ENTRIES) + len(SOUVENIRS_ENTRIES) + len(SUCCES_NARRATIFS)
    courant = (
        len(data.get("fins_atteintes", []))
        + len(data.get("codex", {}))
        + len(data.get("souvenirs", []))
        + len(data.get("succes_narratifs", []))
    )
    return round((courant / total) * 100) if total else 0


def afficher_progression_fins(joueur=None):
    fins_atteintes = getattr(joueur, "fins_atteintes", None) if joueur is not None else None
    if fins_atteintes is None:
        fins_atteintes = lire_fins_atteintes_sauvegarde()
    print(f"Fins découvertes : {len(fins_atteintes)} / {len(FINS_MAJEURES)}")


def afficher_vue_progression(data):
    print("\nPROGRESSION")
    print(f"Fins découvertes : {len(data.get('fins_atteintes', []))} / {len(FINS_MAJEURES)}")
    print(f"Chronique : {len(data.get('codex', {}))} / {len(CODEX_ENTRIES)} entrées")
    print(f"Souvenirs persistants : {len(data.get('souvenirs', []))} / {len(SOUVENIRS_ENTRIES)}")
    print(f"Succès narratifs : {len(data.get('succes_narratifs', []))} / {len(SUCCES_NARRATIFS)}")
    print(f"Histoires achevées : {len(data.get('historique_runs', []))}")
    print(f"Découverte globale : {calculer_completion_meta(data)} %")


def afficher_vue_codex(data):
    print("\nCHRONIQUE")
    codex = data.get("codex", {})
    if not codex:
        print("- Aucune entrée découverte")
        return
    categories = {}
    for entree in codex.values():
        categories.setdefault(entree.get("categorie", "Divers"), []).append(entree)
    for categorie, entrees in categories.items():
        print(f"{categorie} :")
        for entree in sorted(entrees, key=lambda item: item.get("titre", "")):
            print(f"- {entree.get('titre', 'Entrée inconnue')} : {entree.get('texte', '')}")


def afficher_vue_souvenirs(data):
    print("\nSOUVENIRS PERSISTANTS")
    souvenirs = data.get("souvenirs", [])
    if not souvenirs:
        print("- Aucun souvenir persistant")
        return
    for souvenir in souvenirs:
        print(f"- {souvenir}")


def afficher_vue_routes(data):
    print("\nROUTES, SUCCÈS ET RELIQUES")
    traits = data.get("traits_route", [])
    succes = data.get("succes_narratifs", [])
    reliques = data.get("reliques_run", [])
    print("Traits de route :")
    print("- " + "\n- ".join(traits) if traits else "- Aucun")
    print("Succès narratifs :")
    print("- " + "\n- ".join(succes) if succes else "- Aucun")
    print("Reliques de run :")
    print("- " + "\n- ".join(reliques) if reliques else "- Aucune")


def afficher_vue_historique(data):
    print("\nHISTORIQUE DES RUNS")
    runs = data.get("historique_runs", [])
    if not runs:
        print("- Aucune histoire achevée")
        return
    for index, run in enumerate(runs, 1):
        print(f"{index}. {run.get('fin', 'Fin inconnue')} | {run.get('classe', 'classe ?')} | {run.get('allie') or 'sans allié'} | {run.get('cristal') or 'aucun Cristal prioritaire'}")


def afficher_indices_fins(data):
    print("\nINDICES DE FINS")
    print(f"Fins découvertes : {len(data.get('fins_atteintes', []))} / {len(FINS_MAJEURES)}")
    indices = [
        "Une fin exige de préserver une montagne plutôt que de poursuivre la Chasse.",
        "Une fin exige de refuser qu'une coalition devienne une tyrannie utile.",
        "Une fin exige de sceller les Cristaux au moment où ils seraient le plus efficaces.",
        "Une fin exige de laisser une porte fermée, même gardée par un ennemi.",
        "Une fin exige de choisir le sacrifice plutôt que la couronne.",
        "Une fin exige une autorité que les royaumes accepteront peut-être trop vite.",
        "Une fin exige de devenir le gardien plutôt que le vainqueur.",
        "Une fin exige de retirer au monde les pouvoirs qui l'ont sauvé.",
        "Une fin exige d'écarter le garde-fou avant de prendre le Sceau.",
        "Une fin exige assez de vérité, de souvenirs et de garde-fous humains pour tenter l'impossible.",
    ]
    for indice in indices:
        print(f"- {indice}")


def afficher_menu_chronique_progression():
    data = lire_sauvegarde_meta()
    if not data:
        print("\nAucune sauvegarde trouvée. La Chronique se remplira au fil des runs.")
        return
    while True:
        print("\nCHRONIQUE & PROGRESSION")
        options = [
            "Vue d'ensemble",
            "Voir le Codex",
            "Voir les souvenirs persistants",
            "Voir traits, succès et reliques",
            "Voir l'historique des runs",
            "Voir les indices de fins",
            "Retour",
        ]
        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")
        choix = demander_choix("Chronique > ", options)
        if choix == 0:
            afficher_vue_progression(data)
        elif choix == 1:
            afficher_vue_codex(data)
        elif choix == 2:
            afficher_vue_souvenirs(data)
        elif choix == 3:
            afficher_vue_routes(data)
        elif choix == 4:
            afficher_vue_historique(data)
        elif choix == 5:
            afficher_indices_fins(data)
        else:
            return


def conserver_meta(nouveau_joueur, source):
    nouveau_joueur.fins_atteintes = list(getattr(source, "fins_atteintes", []))
    nouveau_joueur.codex = dict(getattr(source, "codex", {}))
    nouveau_joueur.souvenirs = list(getattr(source, "souvenirs", []))
    nouveau_joueur.succes_narratifs = list(getattr(source, "succes_narratifs", []))
    nouveau_joueur.historique_runs = list(getattr(source, "historique_runs", []))
    nouveau_joueur.reliques_run = list(getattr(source, "reliques_run", []))
    nouveau_joueur.options = dict(getattr(source, "options", OPTIONS_DEFAUT))


def nouvelle_partie(source=None):
    print("\nNouvelle partie")
    joueur = creer_personnage()
    if source is not None:
        conserver_meta(joueur, source)
    joueur.options = dict(charger_options())
    sauvegarder(joueur)
    return act_1.jouer(joueur)


def continuer_partie():
    charger_options()
    joueur = charger()
    if joueur is None:
        print("Aucune sauvegarde à continuer.")
        return None
    options = dict(OPTIONS_DEFAUT)
    options.update(getattr(joueur, "options", {}))
    options.update(charger_options())
    joueur.options = options
    appliquer_options(options)
    for numero, fonction in ACTES.items():
        if joueur.acte_courant.startswith(f"Acte {['', 'I', 'II', 'III', 'IV', 'V'][numero]}"):
            return fonction(joueur)
    print("La sauvegarde est à l'épilogue. Utilisez Nouvelle partie ou Nouvelle Route+.")
    return joueur


def menu_options():
    options = dict(charger_options())
    while True:
        print("\nOPTIONS")
        entrees = [
            f"Vitesse du texte : {options['vitesse_texte']}",
            f"Bilans d'acte : {'affichés' if options['afficher_bilans'] else 'masqués'}",
            f"Confirmation fins prématurées : {'oui' if options['confirmer_fins_prematurees'] else 'non'}",
            "Retour",
        ]
        for index, entree in enumerate(entrees, 1):
            print(f"{index}. {entree}")
        choix = demander_choix("Options > ", entrees)
        if choix == 0:
            vitesses = ["lente", "normale", "rapide", "instantanee"]
            for index, vitesse in enumerate(vitesses, 1):
                print(f"{index}. {vitesse}")
            options["vitesse_texte"] = vitesses[demander_choix("Vitesse > ", vitesses)]
        elif choix == 1:
            options["afficher_bilans"] = not options["afficher_bilans"]
        elif choix == 2:
            options["confirmer_fins_prematurees"] = not options["confirmer_fins_prematurees"]
        else:
            sauvegarder_options(options)
            return


def relancer_histoire(joueur_precedent):
    cycles = activer_nouvelle_route_plus(joueur_precedent)
    fins_atteintes = list(getattr(joueur_precedent, "fins_atteintes", []))
    codex = dict(getattr(joueur_precedent, "codex", {}))
    souvenirs = list(getattr(joueur_precedent, "souvenirs", []))
    succes = list(getattr(joueur_precedent, "succes_narratifs", []))
    historique = list(getattr(joueur_precedent, "historique_runs", []))
    reliques = list(getattr(joueur_precedent, "reliques_run", []))
    print("\nNouvelle histoire")
    print(f"Nouvelle Route+ : cycle {cycles}")
    nouveau_joueur = creer_personnage()
    nouveau_joueur.fins_atteintes = fins_atteintes
    nouveau_joueur.codex = codex
    nouveau_joueur.souvenirs = souvenirs
    nouveau_joueur.succes_narratifs = succes
    nouveau_joueur.historique_runs = historique
    nouveau_joueur.reliques_run = reliques
    nouveau_joueur.options = dict(charger_options())
    nouveau_joueur.variables["nouvelle_route_plus"] = True
    nouveau_joueur.variables["cycles_termines"] = cycles
    nouveau_joueur.traits_route = list(getattr(joueur_precedent, "traits_route", []))
    if "Souvenir d'un autre âge" not in nouveau_joueur.traits_route:
        nouveau_joueur.traits_route.append("Souvenir d'un autre âge")
    ajouter_souvenir(nouveau_joueur, "autre_age")
    sauvegarder(nouveau_joueur)
    return act_1.jouer(nouveau_joueur)


def proposer_relance(joueur):
    if joueur.acte_courant != "Épilogue":
        return joueur
    afficher_progression_fins(joueur)
    options = ["Relancer l'histoire depuis l'Acte I", "Retourner au menu des actes", "Quitter"]
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    choix = demander_choix("Après la fin > ", options)
    if choix == 0:
        return relancer_histoire(joueur)
    if choix == 1:
        return lancer_menu()
    return joueur


def lancer_menu():
    return menu_principal()


def menu_principal():
    charger_options()
    while True:
        print("\nLES CHRONIQUES D'ELDERIA")
        afficher_progression_fins()
        options = [
            "Nouvelle partie",
            "Continuer",
            "Choisir un acte",
            "Chronique & progression",
            "Options",
            "Quitter",
        ]
        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")
        choix = demander_choix("Menu > ", options)
        if choix == 0:
            source = charger() if lire_sauvegarde_meta() else None
            joueur = nouvelle_partie(source)
        elif choix == 1:
            joueur = continuer_partie()
        elif choix == 2:
            joueur = lancer_menu_actes()
        elif choix == 3:
            afficher_menu_chronique_progression()
            continue
        elif choix == 4:
            menu_options()
            continue
        else:
            return None
        if joueur is not None:
            print(f"\nActe terminé : {joueur.acte_courant}")
            return proposer_relance(joueur)


def lancer_menu_actes():
    acte = choisir_acte()
    joueur = ACTES[acte]()
    return joueur
