def niveau_relation(score):
    if score >= 80:
        return "lien indéfectible"
    if score >= 50:
        return "confiance solide"
    if score >= 20:
        return "alliance prudente"
    if score > 0:
        return "respect fragile"
    if score < 0:
        return "rupture ouverte"
    return "lien incertain"


def ajouter_trait_route(joueur, trait):
    if not hasattr(joueur, "traits_route"):
        joueur.traits_route = []
    if trait not in joueur.traits_route:
        joueur.traits_route.append(trait)
        return True
    return False


def faction_dominante(joueur):
    if not joueur.factions:
        return None
    faction = max(joueur.factions, key=joueur.factions.get)
    return faction if joueur.factions[faction] > 0 else None


def route_commandement(joueur):
    if joueur.variables.get("commandement_efficace"):
        return "commandement militaire"
    if joueur.variables.get("commandement_compatissant"):
        return "commandement compatissant"
    if joueur.variables.get("commandement_equilibre") or joueur.variables.get("commandement_partage"):
        return "commandement partagé"
    scores = {
        "commandement militaire": getattr(joueur, "armee", 0),
        "guerre d'ombres": getattr(joueur, "espionnage", 0),
        "coalition diplomatique": getattr(joueur, "diplomatie", 0),
    }
    route = max(scores, key=scores.get)
    return route if scores[route] > 0 else "commandement indécis"


def route_morale(joueur):
    if joueur.alignement >= 3:
        return "route lumineuse"
    if joueur.alignement <= -3:
        return "route sombre"
    if joueur.variables.get("renonce_tyrannie"):
        return "route retenue"
    if joueur.variables.get("cristaux_utilises_dangereusement"):
        return "route du pouvoir dangereux"
    return "route ambivalente"


def signature_classe_finale(joueur):
    textes = {
        "Guerrier": "Votre corps comprend la fin comme une ligne à tenir : protéger assez longtemps pour que les autres puissent choisir.",
        "Rôdeur": "Votre instinct cherche encore les routes que personne ne surveille : même devant le Sceau, une issue se gagne parfois par l'angle mort.",
        "Mage": "Votre esprit entend les fractures comme une grammaire ancienne : le Temps ne se brise pas au hasard, il conjugue une peur plus vieille que les royaumes.",
        "Paladin": "Votre serment pèse plus lourd que votre arme : sauver Elderia ne vaudra rien si la lumière apprend à justifier n'importe quel prix.",
        "Nécromancien": "Les cendres que vous avez appris à réveiller se pressent contre le Sceau comme si elles reconnaissaient enfin la porte qu'elles cherchaient depuis toujours.",
    }
    return textes.get(joueur.classe, "Votre histoire personnelle colore le dernier choix plus sûrement que n'importe quelle prophétie.")


def attribuer_traits_route(joueur):
    ajouter_trait_route(joueur, f"Porteur {joueur.classe}")
    if joueur.allie_politique:
        ajouter_trait_route(joueur, f"Allié de {joueur.allie_politique}")
    if joueur.reputation >= 8:
        ajouter_trait_route(joueur, "Héros du peuple")
    if joueur.reputation_criminelle >= 3:
        ajouter_trait_route(joueur, "Hors-la-loi d'Aldor")
    if joueur.tension_fragment >= 8:
        ajouter_trait_route(joueur, "Marque instable")
    if joueur.connaissance_temporelle >= 4 or joueur.variables.get("secret_arthen", 0) >= 3:
        ajouter_trait_route(joueur, "Héritier des Veilleurs")
    if joueur.variables.get("garrick_sauve"):
        ajouter_trait_route(joueur, "Sauveur de Garrick")
    if joueur.loyautes.get("Garrick", 0) >= 50:
        ajouter_trait_route(joueur, "Pupille de Garrick")
    if joueur.loyautes.get("Lyra", 0) >= 50:
        ajouter_trait_route(joueur, "Confiance de Lyra")
    if joueur.variables.get("lyra_garde_fou") or joueur.variables.get("compagnons_garde_fou"):
        ajouter_trait_route(joueur, "Garde-fou de Lyra")
    if joueur.variables.get("morvayn_recrute"):
        ajouter_trait_route(joueur, "Alliance de cendre")
    elif joueur.variables.get("morvayn_epargne"):
        ajouter_trait_route(joueur, "Clémence envers Morvayn")
    elif joueur.variables.get("morvayn_tue"):
        ajouter_trait_route(joueur, "Tombeur de Morvayn")
    if joueur.variables.get("cristal_prioritaire"):
        ajouter_trait_route(joueur, f"Appelé par {joueur.variables['cristal_prioritaire']}")
    if joueur.variables.get("commandement_efficace"):
        ajouter_trait_route(joueur, "Main de fer")
    if joueur.variables.get("commandement_compatissant"):
        ajouter_trait_route(joueur, "Protecteur des réfugiés")
    if joueur.variables.get("commandement_equilibre") or joueur.variables.get("commandement_partage"):
        ajouter_trait_route(joueur, "Commandement partagé")
    if joueur.variables.get("cristaux_utilises_dangereusement"):
        ajouter_trait_route(joueur, "Porteur du pouvoir dangereux")
    if joueur.variables.get("renonce_tyrannie"):
        ajouter_trait_route(joueur, "Renoncement au Sceau")
    if joueur.fin_majeure:
        ajouter_trait_route(joueur, f"A atteint : {joueur.fin_majeure}")
    return joueur.traits_route


def bilan_acte(joueur, titre_acte):
    from elderia.core.codex import progression_codex, progression_souvenirs
    from elderia.core.meta_progression import resume_meta, statuts_compagnons

    attribuer_traits_route(joueur)
    traits = joueur.traits_route[-6:] if joueur.traits_route else []
    codex_courant, codex_total = progression_codex(joueur)
    souvenirs_courant, souvenirs_total = progression_souvenirs(joueur)
    statuts = statuts_compagnons(joueur)
    lignes = [
        "\n" + "=" * 60,
        f"BILAN NARRATIF - {titre_acte}",
        "=" * 60,
        f"Route morale : {route_morale(joueur)}.",
        f"Route de commandement : {route_commandement(joueur)}.",
        f"Faction dominante : {joueur.allie_politique or faction_dominante(joueur) or 'aucune'}.",
        f"Cristaux : {', '.join(joueur.cristaux) if joueur.cristaux else 'aucun'}.",
        f"Secrets découverts : {len(joueur.secrets)} | Rêves/visions : {len(joueur.reves)}.",
        f"Chronique : {codex_courant} / {codex_total} entrées.",
        f"Souvenirs persistants : {souvenirs_courant} / {souvenirs_total}.",
        f"Fins découvertes : {len(getattr(joueur, 'fins_atteintes', []))}.",
        "Statuts des compagnons : " + ", ".join(f"{nom} ({statut})" for nom, statut in statuts.items()) + ".",
        resume_meta(joueur),
        "Traits de route récents :",
    ]
    lignes.extend([f"- {trait}" for trait in traits] if traits else ["- Aucun trait de route révélé"])
    lignes.append("=" * 60)
    return "\n".join(lignes)


def afficher_bilan_acte(joueur, titre_acte):
    from elderia.core.options import option_active
    from elderia.core.gameplay import accorder_recompense_bilan

    accorder_recompense_bilan(joueur, titre_acte)

    if not option_active("afficher_bilans"):
        return ""
    texte = bilan_acte(joueur, titre_acte)
    print(texte)
    entree = f"Bilan narratif {titre_acte} : {', '.join(joueur.traits_route[-6:]) if joueur.traits_route else 'aucun trait'}"
    if entree not in joueur.journal:
        joueur.journal.append(entree)
    return texte


def bilan_narratif(joueur):
    from elderia.core.codex import progression_codex, progression_souvenirs
    from elderia.core.meta_progression import resume_meta, statuts_compagnons

    attribuer_traits_route(joueur)
    codex_courant, codex_total = progression_codex(joueur)
    souvenirs_courant, souvenirs_total = progression_souvenirs(joueur)
    statuts = statuts_compagnons(joueur)
    faction = joueur.allie_politique or faction_dominante(joueur) or "aucune faction dominante"
    cristal = joueur.variables.get("cristal_prioritaire") or "aucun Cristal prioritaire"
    compagnons = [nom for nom in ["Garrick", "Lyra", "Borin", "Morvayn", "Kael", "Selene", "Elara", "Mira aux Corbeaux"] if nom in joueur.compagnons]
    compagnons_texte = ", ".join(compagnons) if compagnons else "aucun compagnon majeur à vos côtés"
    lignes = [
        "\nBILAN DE VOTRE ROUTE",
        f"Faction dominante : {faction}.",
        f"Cristaux portés : {', '.join(joueur.cristaux) if joueur.cristaux else 'aucun'}.",
        f"Cristal prioritaire : {cristal}.",
        f"Commandement : {route_commandement(joueur)}.",
        f"Route morale : {route_morale(joueur)}.",
        f"Compagnons présents : {compagnons_texte}.",
        f"Lien avec Garrick : {niveau_relation(joueur.loyautes.get('Garrick', 0))}.",
        f"Lien avec Lyra : {niveau_relation(joueur.loyautes.get('Lyra', 0))}.",
        f"Connaissance temporelle : {joueur.connaissance_temporelle}.",
        f"Tension du Fragment : {joueur.tension_fragment}.",
        f"Chronique : {codex_courant} / {codex_total} entrées.",
        f"Souvenirs persistants : {souvenirs_courant} / {souvenirs_total}.",
        "Statuts des compagnons : " + ", ".join(f"{nom} ({statut})" for nom, statut in statuts.items()) + ".",
        resume_meta(joueur),
        f"Traits de route : {', '.join(joueur.traits_route) if joueur.traits_route else 'aucun'}.",
    ]
    return "\n".join(lignes)