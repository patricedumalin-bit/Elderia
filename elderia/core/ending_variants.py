import unicodedata


VARIANTES_FINS = {
    "Fin du Sacrifice": {
        "brumebois": "Parce que les souvenirs de Brumebois vous accompagnent encore, votre sacrifice garde une chaleur simple : quelque part, le pain de Mira, le marteau de Garrick et les rires du festival survivent dans ce que vous sauvez.",
        "cosmique": "Votre connaissance du Temps transforme le sacrifice en geste précis. Vous ne donnez pas seulement votre vie : vous placez votre nom au bon endroit dans la serrure du Sceau.",
        "compagnons": "Vos compagnons ne vous sauvent pas de la fin, mais ils empêchent votre disparition de devenir abstraite. Le monde perd un Porteur ; eux perdent quelqu'un qu'ils avaient choisi.",
        "mira": "Parce que vous avez vraiment écouté Mira, votre fin ne devient jamais seulement une prophétie. Elle garde la forme d'une main posée sur un front fiévreux et d'une voix qui refusait de confondre courage et solitude.",
        "marque_instable": "Votre marque n'a jamais fini de se stabiliser, et c'est peut-être ce qui rend ce sacrifice possible : une frontière déjà incertaine se referme plus facilement qu'une certitude.",
    },
    "Fin du Roi": {
        "militaire": "Votre règne naît dans la discipline des armées. Les frontières tiennent, les routes se rouvrent, et chacun comprend que la paix aura le pas régulier des soldats.",
        "diplomatie": "Votre règne commence par des serments plutôt que par des chaînes. La coalition vous suit parce qu'elle sait ce que coûterait votre absence, pas seulement parce qu'elle craint votre force.",
        "varken": "Sous votre autorité, Varken prospère vite. Les marchés appellent cela stabilité ; les poètes, plus prudents, parlent d'un royaume où même la paix tient un registre de dettes.",
        "gardien_secrets": "Les secrets que vous avez gardés vous rendent plus difficile à juger. Vos sujets ne sauront jamais si votre silence protège le royaume ou prépare simplement la prochaine obéissance.",
        "commandement_partage": "Vous n'avez jamais régné seul. Le commandement partagé avec vos compagnons laisse au trône une forme étrange, plus fragile en apparence, mais que personne n'a encore réussi à renverser.",
    },
    "Fin du Gardien": {
        "lyra": "Lyra devient l'une des rares voix capables de parler au Gardien sans prière. Ses visites rappellent aux générations futures que même les puissances immobiles doivent être contredites.",
        "garrick": "Garrick laisse près de la Chambre du Sceau un marteau trop usé pour servir encore. Vous ne l'utiliserez jamais, mais sa présence empêche le sanctuaire de devenir entièrement froid.",
        "cristaux": "Les Cristaux se calment différemment selon votre route. Le second Cristal garde votre marque comme une nuance dans sa lumière, preuve que la garde n'est pas une prison sans mémoire.",
        "verite_pardon": "Parce que vous avez exigé la vérité avant le pardon, votre garde ne repose pas sur l'oubli. Les Cristaux apprennent de vous qu'une blessure peut rester ouverte sans devenir une arme.",
    },
    "Fin du Héros": {
        "peuple": "Le peuple retient surtout que vous avez rendu le monde à ses propres mains. Les miracles disparaissent, mais les villages apprennent à appeler courage ce qu'ils demandaient autrefois à la magie.",
        "ashkar": "Ashkar comprend mieux que les autres ce que signifie briser une puissance nécessaire. Les clans nains gravent votre nom près des serments qui refusent les outils trop faciles.",
        "mage": "Pour un Mage, détruire les Cristaux est une amputation volontaire. Vous survivez à la perte de la grande musique du monde, et c'est peut-être votre plus grand acte de lucidité.",
        "invocateur": "Pour un Nécromancien, détruire les Cristaux revient à éteindre la braise par laquelle les cendres vous répondaient. Elles se taisent une à une, et ce silence pèse plus lourd que n'importe quel adieu.",
        "lecteur_cendres": "Les ordres brûlés, les traces de Morvayn et les phrases sauvées des cendres vous ont appris une chose : certains pouvoirs doivent être détruits avant que leurs justifications deviennent trop convaincantes.",
    },
    "Fin du Tyran": {
        "lyra_ecartee": "Parce que vous avez écarté le garde-fou de Lyra, votre règne porte dès le premier jour une absence très nette. Les révoltes futures apprendront son nom avant le vôtre.",
        "main_de_fer": "Votre commandement militaire rend la tyrannie presque efficace. Les famines reculent, les routes sont sûres, les guerres cessent, et c'est précisément ce qui rend la contestation si difficile.",
        "cristaux": "L'usage dangereux des Cristaux vous a préparé à cette autorité. Le Sceau n'est plus une tentation nouvelle, seulement l'outil définitif d'une logique déjà acceptée.",
        "solitude": "Le poids gardé seul depuis les premiers Cristaux trouve ici son aboutissement. Personne ne vous a arraché aux autres d'un coup ; vous avez seulement appris, choix après choix, à appeler solitude responsabilité.",
        "hors_la_loi": "Aldorath vous a un jour traité en hors-la-loi, et cette étiquette n'a jamais vraiment disparu. Votre tyrannie ressemble parfois à une vengeance patiente contre une ville qui vous a jugé trop tôt.",
    },
    "Fin Secrète": {
        "morvayn": "Si Morvayn a survécu jusqu'à cette vérité, sa cendre cesse enfin de tomber en sens inverse. Il ne devient pas innocent, mais il assiste à une fin qu'il n'avait jamais réussi à imaginer.",
        "codex": "Votre Chronique presque complète donne au Temps assez de noms pour se réparer sans effacer ceux qui ont payé. Ce qui est connu peut enfin cesser de se répéter comme une malédiction.",
        "souvenirs": "Les souvenirs persistants empêchent la restauration de devenir une correction froide. Le Temps ne revient pas à zéro : il revient avec du pain chaud, des voix, des cicatrices et des promesses.",
    },
}


def normaliser_trait(texte):
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(caractere for caractere in texte if not unicodedata.combining(caractere)).casefold()


def variantes_pour_fin(joueur):
    variantes = VARIANTES_FINS.get(joueur.fin_majeure, {})
    resultats = []
    souvenirs = set(getattr(joueur, "souvenirs", []))
    codex = getattr(joueur, "codex", {})
    traits = {normaliser_trait(trait) for trait in getattr(joueur, "traits_route", [])}

    if joueur.fin_majeure == "Fin du Sacrifice":
        if "Le pain chaud de Mira" in souvenirs or "La main de Garrick sur votre épaule" in souvenirs:
            resultats.append(variantes["brumebois"])
        if joueur.connaissance_temporelle >= 4:
            resultats.append(variantes["cosmique"])
        if joueur.variables.get("serment_final_compagnons") or joueur.variables.get("compagnons_dans_vision_finale"):
            resultats.append(variantes["compagnons"])
        if normaliser_trait("Écouté par Mira") in traits or normaliser_trait("Confiance de Mira") in traits:
            resultats.append(variantes["mira"])
        if normaliser_trait("Marque instable") in traits:
            resultats.append(variantes["marque_instable"])
    elif joueur.fin_majeure == "Fin du Roi":
        if getattr(joueur, "armee", 0) >= getattr(joueur, "diplomatie", 0):
            resultats.append(variantes["militaire"])
        if getattr(joueur, "diplomatie", 0) >= 4 or joueur.variables.get("coalition_entraidee"):
            resultats.append(variantes["diplomatie"])
        if joueur.allie_politique == "Ligue de Varken":
            resultats.append(variantes["varken"])
        if normaliser_trait("Gardien de secrets") in traits or normaliser_trait("Gardien des lettres") in traits:
            resultats.append(variantes["gardien_secrets"])
        if normaliser_trait("Commandement partagé") in traits:
            resultats.append(variantes["commandement_partage"])
    elif joueur.fin_majeure == "Fin du Gardien":
        if joueur.variables.get("lyra_garde_fou"):
            resultats.append(variantes["lyra"])
        if joueur.loyautes.get("Garrick", 0) >= 50:
            resultats.append(variantes["garrick"])
        if joueur.variables.get("cristal_prioritaire"):
            resultats.append(variantes["cristaux"])
        if normaliser_trait("Vérité avant pardon") in traits:
            resultats.append(variantes["verite_pardon"])
    elif joueur.fin_majeure == "Fin du Héros":
        if joueur.reputation >= 8:
            resultats.append(variantes["peuple"])
        if "ashkar" in codex:
            resultats.append(variantes["ashkar"])
        if joueur.classe == "Mage":
            resultats.append(variantes["mage"])
        if joueur.classe == "Nécromancien":
            resultats.append(variantes["invocateur"])
        if normaliser_trait("Lecteur des cendres") in traits or normaliser_trait("Piste de Morvayn") in traits:
            resultats.append(variantes["lecteur_cendres"])
    elif joueur.fin_majeure == "Fin du Tyran":
        if joueur.variables.get("choisit_tyrannie_malgre_lyra"):
            resultats.append(variantes["lyra_ecartee"])
        if joueur.variables.get("commandement_efficace"):
            resultats.append(variantes["main_de_fer"])
        if joueur.variables.get("cristaux_utilises_dangereusement"):
            resultats.append(variantes["cristaux"])
        if normaliser_trait("Porteur Solitaire") in traits or "Solitude du Porteur" in getattr(joueur, "blessures_narratives", []):
            resultats.append(variantes["solitude"])
        if normaliser_trait("Hors-la-loi d'Aldor") in traits:
            resultats.append(variantes["hors_la_loi"])
    elif joueur.fin_majeure == "Fin Secrète":
        if joueur.variables.get("morvayn_recrute") or joueur.variables.get("morvayn_epargne"):
            resultats.append(variantes["morvayn"])
        if len(codex) >= 10:
            resultats.append(variantes["codex"])
        if len(souvenirs) >= 7:
            resultats.append(variantes["souvenirs"])
    return resultats[:3]


def texte_variantes_fin(joueur):
    variantes = variantes_pour_fin(joueur)
    if not variantes:
        return ""
    lignes = ["\nÉCHOS DE VOTRE ROUTE"]
    lignes.extend(variantes)
    return "\n\n".join(lignes)


def activer_nouvelle_route_plus(joueur):
    joueur.variables["nouvelle_route_plus"] = True
    joueur.variables["cycles_termines"] = joueur.variables.get("cycles_termines", 0) + 1
    if hasattr(joueur, "traits_route") and "Souvenir d'un autre âge" not in joueur.traits_route:
        joueur.traits_route.append("Souvenir d'un autre âge")
    return joueur.variables["cycles_termines"]