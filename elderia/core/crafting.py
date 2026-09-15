from elderia.core.io import demander_choix, raconter
from elderia.data.tables import RECETTES_FORGE, ARMES, ARMURES, BOUCLIERS, BIJOUX


def recette_prete(joueur, nom_recette):
    data = RECETTES_FORGE[nom_recette]
    if data['base'] not in joueur.inventaire:
        return False
    return all(joueur.composants.get(comp, 0) >= qt for comp, qt in data['composants'].items())


def peut_forger(joueur):
    """Indique si au moins une recette est actuellement réalisable (base + composants réunis)."""
    return any(recette_prete(joueur, nom) for nom in RECETTES_FORGE)


def visiter_forge(joueur):
    """Affiche les recettes disponibles et permet de forger."""
    raconter("\n--- LA FORGE ---")
    recettes = list(RECETTES_FORGE.keys())

    while True:
        raconter("\nRecettes disponibles :")
        options = []
        for nom, data in RECETTES_FORGE.items():
            base = data['base']
            manque = []
            for comp, qt in data['composants'].items():
                if joueur.composants.get(comp, 0) < qt:
                    manque.append(f"{comp} ({joueur.composants.get(comp,0)}/{qt})")

            status = " [PRÊT]" if not manque and base in joueur.inventaire else " [MANQUE COMPOSANTS]"
            options.append(f"{nom} (Base: {base}){status}")

        options.append("Quitter la forge")
        choix = demander_choix("Forger > ", options, interaction=True)

        if choix >= len(recettes):
            break

        nom_recette = recettes[choix]
        data = RECETTES_FORGE[nom_recette]
        base = data['base']

        if base not in joueur.inventaire:
            raconter(f"❌ Vous n'avez pas l'objet de base : {base}")
            continue

        # Vérifier composants
        peut_forger = True
        for comp, qt in data['composants'].items():
            if joueur.composants.get(comp, 0) < qt:
                peut_forger = False
                raconter(f"❌ Manque : {comp}")

        if peut_forger:
            # Consommer
            joueur.inventaire.remove(base)
            for comp, qt in data['composants'].items():
                joueur.retirer_composant(comp, qt)

            # Ajouter nouvel objet
            joueur.ajouter_objet(nom_recette)
            raconter(f"✨ ÉTINCELLES ! Vous avez forgé : {nom_recette} !")

            # Équipement automatique
            if nom_recette in ARMES and joueur.arme_est_meilleure(nom_recette):
                joueur.equiper_arme(nom_recette)
            elif nom_recette in ARMURES and joueur.armure_est_meilleure(nom_recette):
                joueur.equiper_armure(nom_recette)
