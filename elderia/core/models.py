from elderia.core.io import demander_choix, effet_combat, lancer_de, raconter
from elderia.data.tables import (
    ARBRE_TALENTS,
    AFFINITES_CLASSE,
    ARMES,
    ARMURES,
    BOUCLIERS,
    BIJOUX,
    CLASSES,
    COMPAGNONS_DETAILS,
    COMPAGNONS_DISPONIBLES,
    DIFFICULTES,
    FACTIONS,
    FINS_MAJEURES,
    INFLUENCES_POLITIQUES,
    LOYautes_DEPART,
    QUETES_PRINCIPALES,
    VARIABLES_DEPART,
)
from elderia.core.options import OPTIONS_DEFAUT

# Stats de puissance affectées par l'affinité de classe (pas 'agilite', qui reste un encombrement physique fixe).
_STATS_AFFINITE = ("degats", "bonus_force", "bonus_intelligence", "reduction", "defense", "blocage")


def _appliquer_affinite_classe(classe, emplacement, stats_base):
    categorie = stats_base.get("categorie", "neutre")
    multiplicateur = AFFINITES_CLASSE.get(classe, {}).get(emplacement, {}).get(categorie, 1.0)
    if multiplicateur == 1.0:
        return stats_base
    stats = dict(stats_base)
    for cle in _STATS_AFFINITE:
        if cle in stats:
            stats[cle] = round(stats[cle] * multiplicateur)
    return stats


def _score_arme(stats):
    return stats.get("degats", 0) + stats.get("bonus_force", 0) + stats.get("bonus_intelligence", 0)


def _score_armure(stats):
    return stats.get("reduction", 0) + stats.get("defense", 0)


def _score_bouclier(stats):
    return (
        stats.get("blocage", 0)
        + stats.get("defense", 0)
        + stats.get("bonus_force", 0)
        + stats.get("bonus_intelligence", 0)
    )

class Joueur:
    def __init__(self, nom, classe_choisie, difficulte="Normal", origine=None):
        if classe_choisie not in CLASSES:
            raise ValueError(f"Classe inconnue : {classe_choisie}")
        if difficulte not in DIFFICULTES:
            raise ValueError(f"Difficulté inconnue : {difficulte}")

        donnees = CLASSES[classe_choisie]
        self.nom = nom
        self.race = "Humain"
        self.classe = classe_choisie
        self.origine = origine or "Inconnu"
        self.difficulte = difficulte
        self.niveau = 1
        self.xp = 0
        self.reputation = 0
        self.reputation_criminelle = 0
        self.alignement = 0
        self.cristaux = []
        self.fragments_temps = 0
        self.compagnons = []
        self.quetes = {quete: False for quete in QUETES_PRINCIPALES}
        self.factions = dict(FACTIONS)
        self.loyautes = dict(LOYautes_DEPART)
        self.influences = dict(INFLUENCES_POLITIQUES)
        self.variables = dict(VARIABLES_DEPART)
        self.consequences = []
        self.secrets = []
        self.reves = ["Tour noire"]
        self.tension_fragment = 0
        self.corruption = 0
        self.connaissance_temporelle = 0
        self.respect_morvayn = 0
        self.armee = 0
        self.espionnage = 0
        self.diplomatie = 0
        self.rival = "Marek"
        self.quartiers_visites = []
        self.artefacts = []
        self.talents = []
        self.talents_arbre = []
        self.talent_vision_utilisee = None
        self.talent_relance_utilisee = None
        self.allie_politique = None
        self.portes_fermees = []
        self.acte_courant = "Acte I - L'Éveil"
        self.fin_majeure = None
        self.fins_atteintes = []
        self.traits_route = []
        self.codex = {}
        self.souvenirs = []
        self.composants = {}
        self.effets_actifs = {}
        self.blessures_graves = []
        self.blessures_narratives = []
        self.succes_narratifs = []
        self.historique_runs = []
        self.reliques_run = []
        self.options = dict(OPTIONS_DEFAUT)
        self.journal = [
            "Jour 1 : Le Festival des Moissons commence à Brumebois.",
            "Rêve récurrent : une tour noire, un monde en flammes, puis les mots 'Le Septième Sceau est brisé'.",
        ]

        self.force = donnees["force"]
        self.agilite = donnees["agilite"]
        self.endurance = donnees["endurance"]
        self.intelligence = donnees["intelligence"]
        self.volonte = donnees["volonte"]
        self.charisme = donnees["charisme"]

        # Bonus de départ selon l'origine : donne un vrai poids mécanique au choix, pas seulement
        # narratif (en plus de l'avantage systématique accordé par ORIGINES_AVANTAGE sur certains tests).
        if self.origine == "Noble Déchu":
            self.charisme += 1
        elif self.origine == "Enfant des Rues":
            self.agilite += 1
        elif self.origine == "Ancien Soldat":
            self.force += 1
        elif self.origine == "Érudit Errant":
            self.intelligence += 1

        self.pv_max = self.calculer_pv_max()
        self.pm_max = self.calculer_mana_max()
        self.energie_max = self.calculer_energie_max()
        self.or_poches = donnees["or"] + (15 if self.origine == "Noble Déchu" else 0)
        self.competence = donnees["competence"]

        self.pv = self.pv_max
        self.pm = self.pm_max
        self.energie = self.energie_max
        self.arme = (
            "Épée Longue"
            if classe_choisie == "Guerrier"
            else "Bâton runique"
            if classe_choisie == "Mage"
            else "Dague rouillée"
        )
        self.armure = "Armure de cuir" if classe_choisie == "Guerrier" else "Vêtements simples"
        self.inventaire = [
            "Sac à dos",
            "Gourde d'eau",
            "Ration",
            "Ration",
            "Ration",
            self.arme,
            self.armure,
            "Carte incomplète d'Elderia",
        ]
        if classe_choisie == "Guerrier":
            self.inventaire.append("Bouclier en bois")
        else:
            self.inventaire.append("Potion de soin")
        if self.origine == "Enfant des Rues":
            self.inventaire.append("Passe-partout rouillé")
        elif self.origine == "Érudit Errant":
            self.inventaire.append("Notes de recherche personnelles")
        self.bouclier_equipe = "Bouclier en bois" if classe_choisie == "Guerrier" else None
        self.bijou_equipe = None

    @property
    def bonus_arme(self):
        return _appliquer_affinite_classe(self.classe, "armes", ARMES[self.arme])

    @property
    def modificateurs(self):
        return DIFFICULTES.get(self.difficulte, DIFFICULTES["Normal"])

    @property
    def bonus_armure(self):
        return _appliquer_affinite_classe(self.classe, "armures", ARMURES[self.armure])

    @property
    def defense(self):
        return self.bonus_armure["reduction"]

    @property
    def bonus_defense(self):
        return self.bonus_armure["defense"] + self.bonus_bouclier["defense"]

    @property
    def defense_combat(self):
        effet_bijou, valeur_bijou = self.effet_bijou
        bonus_esquive = valeur_bijou if effet_bijou == "bonus_esquive" else 0
        return self.agilite_totale + self.bonus_defense + bonus_esquive

    @property
    def agilite_totale(self):
        bonus_talent = self.effets_talents_arbre().get("bonus_agilite", {}).get("valeur", 0)
        return self.agilite + self.bonus_armure["agilite"] + bonus_talent

    @property
    def force_totale(self):
        return self.force + self.bonus_arme["bonus_force"] + self.bonus_bouclier["bonus_force"]

    @property
    def intelligence_totale(self):
        return self.intelligence + self.bonus_arme["bonus_intelligence"] + self.bonus_bouclier["bonus_intelligence"]

    @property
    def bonus_bouclier(self):
        neutre = {"blocage": 0, "defense": 0, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "neutre"}
        if not self.bouclier:
            return neutre
        return _appliquer_affinite_classe(self.classe, "secondaire", BOUCLIERS[self.bouclier])

    @property
    def bouclier(self):
        return self.bouclier_equipe if self.bouclier_equipe in BOUCLIERS else None

    @property
    def bijou(self):
        return self.bijou_equipe if self.bijou_equipe in BIJOUX else None

    @property
    def effet_bijou(self):
        if not self.bijou:
            return None, 0
        info = BIJOUX[self.bijou]
        return info["effet"], info["valeur"]

    @property
    def xp_prochain_niveau(self):
        return self.niveau * (self.niveau + 1) // 2 * 100

    @property
    def capacite_inventaire(self):
        # +2 emplacements tous les 10 niveaux : le sac s'organise avec l'expérience du porteur.
        return 20 + (self.niveau // 10) * 2

    @property
    def emplacements_utilises(self):
        return len(set(self.inventaire))

    def contenu_inventaire(self):
        lignes = []
        for objet in dict.fromkeys(self.inventaire):
            quantite = self.inventaire.count(objet)
            lignes.append(f"{objet} x{quantite}" if quantite > 1 else objet)
        return lignes

    def a_talent(self, prefixe):
        return any(talent.startswith(prefixe) for talent in self.talents)

    def ajouter_consequence(self, texte):
        if texte not in self.consequences:
            self.consequences.append(texte)

    def a_consequence(self, fragment):
        return any(fragment in consequence for consequence in self.consequences)

    def fermer_porte(self, texte):
        if texte not in self.portes_fermees:
            self.portes_fermees.append(texte)

    def terminer_quete(self, nom):
        self.quetes[nom] = True

    def ajouter_objet(self, objet):
        if self.emplacements_utilises >= self.capacite_inventaire and objet not in self.inventaire:
            raconter(f"❌ Inventaire plein ({self.capacite_inventaire} emplacements). Impossible d'emporter : {objet}.")
            return False
        self.inventaire.append(objet)
        return True

    def equiper_bouclier(self, nom_bouclier):
        if nom_bouclier not in BOUCLIERS:
            raconter("Ce bouclier n'existe pas.")
            return False
        if nom_bouclier not in self.inventaire:
            raconter("Ce bouclier n'est pas dans votre inventaire.")
            return False
        self.bouclier_equipe = nom_bouclier
        raconter(f"{nom_bouclier} équipé.")
        return True

    def equiper_bijou(self, nom_bijou):
        if nom_bijou not in BIJOUX:
            raconter("Ce bijou n'existe pas.")
            return False
        if nom_bijou not in self.inventaire:
            raconter("Ce bijou n'est pas dans votre inventaire.")
            return False
        self.bijou_equipe = nom_bijou
        raconter(f"{nom_bijou} équipé.")
        return True

    def arme_est_meilleure(self, nom_arme):
        if nom_arme not in ARMES:
            return False
        actuelle = _appliquer_affinite_classe(self.classe, "armes", ARMES[self.arme])
        candidate = _appliquer_affinite_classe(self.classe, "armes", ARMES[nom_arme])
        return _score_arme(candidate) > _score_arme(actuelle)

    def armure_est_meilleure(self, nom_armure):
        if nom_armure not in ARMURES:
            return False
        actuelle = _appliquer_affinite_classe(self.classe, "armures", ARMURES[self.armure])
        candidate = _appliquer_affinite_classe(self.classe, "armures", ARMURES[nom_armure])
        return _score_armure(candidate) > _score_armure(actuelle)

    def bouclier_est_meilleure(self, nom_bouclier):
        if nom_bouclier not in BOUCLIERS:
            return False
        if not self.bouclier:
            return True
        actuelle = _appliquer_affinite_classe(self.classe, "secondaire", BOUCLIERS[self.bouclier])
        candidate = _appliquer_affinite_classe(self.classe, "secondaire", BOUCLIERS[nom_bouclier])
        return _score_bouclier(candidate) > _score_bouclier(actuelle)

    def bijou_est_meilleur(self, nom_bijou):
        if nom_bijou not in BIJOUX:
            return False
        if not self.bijou:
            return True
        candidat = BIJOUX[nom_bijou]
        actuel = BIJOUX[self.bijou]
        if candidat["effet"] != actuel["effet"]:
            return False
        return candidat["valeur"] > actuel["valeur"]

    # Abréviations affichées chez le marchand pour préciser à quelle stat correspond chaque écart.
    _ABREVIATIONS_STATS = {
        "degats": "DG", "bonus_force": "FOR", "bonus_intelligence": "INT",
        "reduction": "RED", "defense": "DEF", "agilite": "AGI", "blocage": "BLQ",
    }
    _ABREVIATIONS_EFFETS_BIJOUX = {
        "regen_pv": "PV", "regen_ressource": "RES", "bonus_critique": "CRI", "bonus_loot": "LOOT",
        "vol_vie": "VOL", "reduction_degats": "RD", "bonus_esquive": "ESQ", "bonus_soin": "SOIN",
        "reduction_prix": "PRIX", "bonus_test_stat": "TEST",
    }

    def delta_equipement(self, nom_article):
        """Écart de stats (par abréviation) entre `nom_article` et l'équipement actuellement porté
        dans son emplacement (arme/armure/bouclier/bijou). Retourne une liste de tuples
        (abréviation, delta) non nuls, ou None si l'article n'est pas comparable (consommable,
        service du marchand, ou bijou à effet différent du bijou actuel)."""
        if nom_article in ARMES:
            actuelle = _appliquer_affinite_classe(self.classe, "armes", ARMES[self.arme])
            candidate = _appliquer_affinite_classe(self.classe, "armes", ARMES[nom_article])
            cles = ("degats", "bonus_force", "bonus_intelligence")
        elif nom_article in ARMURES:
            actuelle = _appliquer_affinite_classe(self.classe, "armures", ARMURES[self.armure])
            candidate = _appliquer_affinite_classe(self.classe, "armures", ARMURES[nom_article])
            cles = ("reduction", "defense", "agilite")
        elif nom_article in BOUCLIERS:
            neutre = {"blocage": 0, "defense": 0, "bonus_force": 0, "bonus_intelligence": 0, "categorie": "neutre"}
            actuelle = _appliquer_affinite_classe(self.classe, "secondaire", BOUCLIERS[self.bouclier]) if self.bouclier else neutre
            candidate = _appliquer_affinite_classe(self.classe, "secondaire", BOUCLIERS[nom_article])
            cles = ("blocage", "defense", "bonus_force", "bonus_intelligence")
        elif nom_article in BIJOUX:
            candidat = BIJOUX[nom_article]
            abrev = self._ABREVIATIONS_EFFETS_BIJOUX.get(candidat["effet"], "EFF")
            if not self.bijou:
                return [(abrev, candidat["valeur"])]
            actuel = BIJOUX[self.bijou]
            if candidat["effet"] != actuel["effet"]:
                return None
            delta = candidat["valeur"] - actuel["valeur"]
            return [(abrev, delta)] if delta else []
        else:
            return None
        return [
            (self._ABREVIATIONS_STATS[cle], candidate.get(cle, 0) - actuelle.get(cle, 0))
            for cle in cles
            if candidate.get(cle, 0) - actuelle.get(cle, 0) != 0
        ]

    def equiper_arme(self, nom_arme):
        if nom_arme not in ARMES:
            raconter("Cette arme n'existe pas.")
            return False
        if nom_arme not in self.inventaire:
            raconter("Cette arme n'est pas dans votre inventaire.")
            return False
        self.arme = nom_arme
        self.actualiser_mana_max()
        raconter(f"{nom_arme} équipée.")
        return True

    def equiper_armure(self, nom_armure):
        if nom_armure not in ARMURES:
            raconter("Cette armure n'existe pas.")
            return False
        if nom_armure not in self.inventaire:
            raconter("Cette armure n'est pas dans votre inventaire.")
            return False
        self.armure = nom_armure
        raconter(f"{nom_armure} équipée.")
        return True

    def choisir_talent_arbre(self):
        noeuds = ARBRE_TALENTS.get(self.classe, [])
        candidats = [
            noeud for noeud in noeuds
            if noeud["palier"] == self.niveau
            and noeud["id"] not in self.talents_arbre
            and (noeud["prerequis"] is None or noeud["prerequis"] in self.talents_arbre)
        ]
        if not candidats:
            return
        raconter(f"\n🌟 Palier de talent atteint (niveau {self.niveau}).")
        noms = [noeud["nom"] for noeud in candidats]
        for index, nom in enumerate(noms, 1):
            print(f"{index}. {nom}")
        noeud = candidats[demander_choix("Talent > ", noms)]
        self.talents_arbre.append(noeud["id"])
        raconter(f"Talent acquis : {noeud['nom']}.")

    def effets_talents_arbre(self):
        """Agrège les effets des talents acquis dans l'arbre : le palier le plus haut d'un même type prime."""
        effets = {}
        for noeud in ARBRE_TALENTS.get(self.classe, []):
            if noeud["id"] in self.talents_arbre:
                effet = noeud["effet"]
                type_effet = effet["type"]
                if type_effet not in effets or effet["valeur"] > effets[type_effet]["valeur"]:
                    effets[type_effet] = effet
        return effets

    def modifier_faction(self, faction, valeur):
        self.factions[faction] = max(-100, min(100, self.factions[faction] + valeur))

    def calculer_pv_max(self):
        # Base relevée pour éviter aux classes à faible endurance (Mage) une mort trop rapide en combat.
        base = 14 + self.endurance * 2 + (self.niveau - 1) * 3
        return max(1, round(base * self.modificateurs["pv_joueur"]))

    def calculer_energie_max(self):
        return 10 + self.volonte

    def calculer_mana_max(self):
        base = self.intelligence_totale * 2 if hasattr(self, "arme") else self.intelligence * 2
        bonus_sagesse = 10 if self.a_talent("Sagesse Antique") else 0
        bonus_arbre = self.effets_talents_arbre().get("bonus_mana", {}).get("valeur", 0)
        return base + bonus_sagesse + bonus_arbre

    def actualiser_mana_max(self):
        ancien_max = self.pm_max
        self.pm_max = self.calculer_mana_max()
        if self.pm_max > ancien_max:
            self.pm += self.pm_max - ancien_max
        self.pm = min(self.pm, self.pm_max)

    @property
    def nom_alignement(self):
        if self.alignement >= 3:
            return "Lumière"
        if self.alignement <= -3:
            return "Ombre"
        return "Neutre"

    def afficher_statistiques(self):
        print("\n" + "=" * 72)
        print(f"{self.nom} | {self.classe} niv. {self.niveau} | {self.nom_alignement}")
        print(f"PV {self.pv}/{self.pv_max} | Énergie {self.energie}/{self.energie_max} | Mana {self.pm}/{self.pm_max} | XP {self.xp} | Or {self.or_poches}g")
        print(
            f"FOR {self.force_totale} | AGI {self.agilite_totale} | END {self.endurance} | "
            f"INT {self.intelligence_totale} | VOL {self.volonte} | CHA {self.charisme} | "
            f"Défense {self.defense_combat} | Réduction {self.defense}"
        )
        print(f"Arme : {self.arme} | Armure : {self.armure} | Compétence : {self.competence}")
        print(f"Compagnons : {', '.join(self.compagnons) if self.compagnons else 'Aucun'}")
        print(f"Cristaux : {', '.join(self.cristaux) if self.cristaux else 'Aucun'} | Fragments du Temps : {self.fragments_temps}/25")
        print(f"Inventaire : {', '.join(self.inventaire) if self.inventaire else 'Vide'}")
        print("=" * 72)

    def afficher_fiche_personnage(self):
        print("\n" + "=" * 72)
        print("FICHE DE PERSONNAGE")
        print("=" * 72)
        print(f"Nom : {self.nom}")
        print(f"Race : {self.race}")
        print(f"Classe : {self.classe}")
        print(f"Difficulté : {self.difficulte}")
        print(f"Niveau : {self.niveau}")
        print(f"Alignement : {self.nom_alignement}")
        print(f"Réputation : {self.reputation}")
        print(f"Réputation criminelle : {self.reputation_criminelle}")
        print(f"Expérience : {self.xp} / {self.xp_prochain_niveau} XP")
        print(f"Or : {self.or_poches}")
        print("\nCARACTÉRISTIQUES")
        print(f"FOR {self.force} | AGI {self.agilite} | END {self.endurance} | INT {self.intelligence} | VOL {self.volonte} | CHA {self.charisme}")
        print("\nRESSOURCES")
        print(f"PV = 14 + ({self.endurance} x 2) + progression : {self.pv}/{self.pv_max}")
        print(f"Énergie = 10 + {self.volonte} : {self.energie}/{self.energie_max}")
        print(f"Mana = {self.intelligence_totale} x 2 : {self.pm}/{self.pm_max}")
        print("\nCOMBAT RAPIDE")
        print(f"Initiative : 1d20 + {self.agilite_totale}")
        print(f"Attaque : 1d20 + {self.force_totale}")
        print(f"Dégâts sans compétence : {self.bonus_arme['degats']} + {self.force_totale} = {self.bonus_arme['degats'] + self.force_totale}")
        print(f"Dégâts avec {self.competence} : {self.bonus_arme['degats'] + self.force_totale + 5 if self.competence == 'Coup Puissant' else 'selon compétence'}")
        print(f"Défense : AGI {self.agilite_totale} + équipement {self.bonus_defense} = {self.defense_combat}")
        print(f"Réduction d'armure : {self.defense}")
        print("\nÉQUIPEMENT")
        print(f"Arme principale : {self.arme} ({self.bonus_arme['degats']} dégâts)")
        print(f"Main secondaire : {self.bouclier if self.bouclier else 'Aucun'}")
        print(f"Armure : {self.armure} (réduction {self.defense}, défense +{self.bonus_armure['defense']})")
        print("Accessoires : Aucun")
        print("\nINVENTAIRE")
        print(f"Capacité : {self.emplacements_utilises} / {self.capacite_inventaire}")
        for objet in self.contenu_inventaire():
            print(f"- {objet}")
        print("\nQUÊTES")
        for quete, terminee in self.quetes.items():
            print(f"{'[x]' if terminee else '[ ]'} {quete}")
        print("\nCAMPAGNE")
        print(f"Acte courant : {self.acte_courant}")
        print("Factions :")
        for faction, score in self.factions.items():
            print(f"- {faction} : {score}")
        print("Influences politiques :")
        for influence, score in self.influences.items():
            print(f"- {influence} : {score}")
        print("Variables majeures :")
        for nom, valeur in self.variables.items():
            print(f"- {nom} : {valeur}")
        print("Loyautés :")
        for nom, score in self.loyautes.items():
            print(f"- {nom} : {score}")
        print("Traits de route :")
        if self.traits_route:
            for trait in self.traits_route:
                print(f"- {trait}")
        else:
            print("- Aucun")
        from elderia.core.codex import afficher_chronique
        from elderia.core.meta_progression import resume_meta, statuts_compagnons

        afficher_chronique(self)
        print("\nSTATUTS DES COMPAGNONS")
        for nom, statut in statuts_compagnons(self).items():
            print(f"- {nom} : {statut}")
        print("\nPROGRESSION MÉTA")
        print(resume_meta(self))
        print("Conséquences à long terme :")
        if self.consequences:
            for consequence in self.consequences:
                print(f"- {consequence}")
        else:
            print("- Aucune conséquence majeure révélée")
        print("Secrets découverts :")
        if self.secrets:
            for secret in self.secrets:
                print(f"- {secret}")
        else:
            print("- Aucun")
        print("Rêves et visions :")
        for reve in self.reves:
            print(f"- {reve}")
        print(f"Tension du Fragment du Temps : {self.tension_fragment}")
        print(f"Connaissance temporelle : {self.connaissance_temporelle}")
        print(f"Respect caché de Morvayn : {self.respect_morvayn}")
        print("Quartiers visités :")
        if self.quartiers_visites:
            for quartier in self.quartiers_visites:
                print(f"- {quartier}")
        else:
            print("- Aucun")
        print("Artefacts majeurs :")
        if self.artefacts:
            for artefact in self.artefacts:
                print(f"- {artefact}")
        else:
            print("- Aucun")
        print("Talents d'alliance :")
        if self.talents:
            for talent in self.talents:
                print(f"- {talent}")
        else:
            print("- Aucun")
        print("Arbre de talents :")
        noeuds = {noeud["id"]: noeud["nom"] for noeud in ARBRE_TALENTS.get(self.classe, [])}
        if self.talents_arbre:
            for talent_id in self.talents_arbre:
                print(f"- {noeuds.get(talent_id, talent_id)}")
        else:
            print("- Aucun")
        print(f"Allié politique : {self.allie_politique if self.allie_politique else 'Aucun'}")
        print("Portes fermées :")
        if self.portes_fermees:
            for porte in self.portes_fermees:
                print(f"- {porte}")
        else:
            print("- Aucune")
        print("\nCOMPAGNONS")
        for compagnon in COMPAGNONS_DISPONIBLES:
            statut = "recruté" if compagnon in self.compagnons else "non recruté"
            print(f"{compagnon} : loyauté {self.loyautes.get(compagnon, 0)}/100, {statut} - {COMPAGNONS_DETAILS[compagnon]}")
        print("\nJOURNAL D'AVENTURE")
        for entree in self.journal:
            print(f"- {entree}")
        print("\nFINS MAJEURES POSSIBLES")
        print(f"Fins découvertes : {len(self.fins_atteintes)} / {len(FINS_MAJEURES)}")
        print("=" * 72)

    def enregistrer_fin_atteinte(self):
        if self.fin_majeure and self.fin_majeure in FINS_MAJEURES and self.fin_majeure not in self.fins_atteintes:
            self.fins_atteintes.append(self.fin_majeure)
            return True
        return False

    def ajouter_xp(self, montant):
        montant = max(1, round(montant * self.modificateurs["xp"]))
        self.xp += montant
        raconter(f"✨ Vous gagnez {montant} XP.")
        while self.xp >= self.xp_prochain_niveau:
            self.niveau += 1
            self.pv_max = self.calculer_pv_max()
            self.pv = self.pv_max
            self.energie_max = self.calculer_energie_max()
            self.energie = self.energie_max
            self.pm_max = self.calculer_mana_max()
            self.pm = self.pm_max
            self.choisir_progression()
            if self.niveau in (5, 15, 30, 45):
                self.choisir_talent_arbre()

    def choisir_progression(self):
        raconter(f"\n⭐ Niveau {self.niveau} atteint ! +3 PV.")
        effet_combat("levelup")
        options = ["Force", "Agilité", "Endurance", "Intelligence", "Volonté", "Charisme"]
        print("Choisissez une statistique à améliorer :")
        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")
        choix = options[demander_choix("> ", options)]
        if choix == "Force":
            self.force += 1
        elif choix == "Agilité":
            self.agilite += 1
        elif choix == "Endurance":
            self.endurance += 1
            self.pv_max = self.calculer_pv_max()
            self.pv = self.pv_max
        elif choix == "Intelligence":
            self.intelligence += 1
            self.actualiser_mana_max()
        elif choix == "Volonté":
            self.volonte += 1
            self.energie_max = self.calculer_energie_max()
            self.energie = self.energie_max
        else:
            self.charisme += 1
        raconter(f"{choix} augmente de 1.")

    def utiliser_potion(self):
        # Le soin est un pourcentage des PV max (avec un plancher 2d6) pour rester utile jusqu'en fin d'histoire.
        if "Potion de soin" in self.inventaire:
            objet, fraction = "Potion de soin", 0.2
        elif "Potion supérieure" in self.inventaire:
            objet, fraction = "Potion supérieure", 0.4
        else:
            raconter("❌ Vous n'avez plus de potion de soin.")
            return False
        self.inventaire.remove(objet)
        soin = max(lancer_de(6) + lancer_de(6), round(self.pv_max * fraction))
        effet_bijou, valeur_bijou = self.effet_bijou
        if effet_bijou == "bonus_soin":
            soin = round(soin * (1 + valeur_bijou / 100))
        self.pv = min(self.pv_max, self.pv + soin)
        raconter(f"❤️ {objet} : vous récupérez {soin} PV.")
        return True

    def utiliser_ration(self):
        if "Ration" not in self.inventaire:
            raconter("Votre sac ne contient plus aucune ration.")
            return False
        self.inventaire.remove("Ration")
        soin = max(5, round(self.pv_max * 0.08))
        effet_bijou, valeur_bijou = self.effet_bijou
        if effet_bijou == "bonus_soin":
            soin = round(soin * (1 + valeur_bijou / 100))
        self.pv = min(self.pv_max, self.pv + soin)
        raconter(f"Vous mangez une ration et récupérez {soin} PV.")
        return True

    def niveau_lien(self, compagnon):
        loyaute = self.loyautes.get(compagnon, 0)
        if loyaute >= 80: return 4 # Âme soeur
        if loyaute >= 50: return 3 # Allié fidèle
        if loyaute >= 25: return 2 # Compagnon d'arme
        if loyaute >= 10: return 1 # Connaissance
        return 0

    def ajouter_composant(self, nom, quantite=1):
        self.composants[nom] = self.composants.get(nom, 0) + quantite
        raconter(f"📦 +{quantite} {nom}")

    def retirer_composant(self, nom, quantite=1):
        if self.composants.get(nom, 0) >= quantite:
            self.composants[nom] -= quantite
            return True
        return False

    def ajouter_corruption(self, montant):
        self.corruption += montant
        if self.corruption >= 10:
            raconter("\n💀 [CORRUPTION] Le Temps pèse sur votre âme. Des ombres s'agitent à la limite de votre vision.")
        if self.corruption >= 20:
            raconter("⚠️ La distorsion temporelle affecte votre corps. (Désavantage sur les tests de Charisme)")

    def subir_blessure_grave(self, nom):
        if nom not in self.blessures_graves:
            self.blessures_graves.append(nom)
            raconter(f"🩹 [BLESSURE GRAVE] Vous souffrez de : {nom}.")


def normaliser_joueur(joueur):
    joueur.quetes = {**{quete: False for quete in QUETES_PRINCIPALES}, **getattr(joueur, "quetes", {})}
    joueur.factions = {**FACTIONS, **getattr(joueur, "factions", {})}
    joueur.loyautes = {**LOYautes_DEPART, **getattr(joueur, "loyautes", {})}
    joueur.influences = {**INFLUENCES_POLITIQUES, **getattr(joueur, "influences", {})}
    joueur.variables = {**VARIABLES_DEPART, **getattr(joueur, "variables", {})}
    for attribut, defaut in {
        "consequences": [],
        "secrets": [],
        "reves": ["Tour noire"],
        "quartiers_visites": [],
        "artefacts": [],
        "talents": [],
        "portes_fermees": [],
        "compagnons": [],
        "cristaux": [],
        "inventaire": [],
        "journal": [],
        "bouclier_equipe": None,
        "bijou_equipe": None,
        "talents_arbre": [],
        "talent_vision_utilisee": None,
        "talent_relance_utilisee": None,
        "allie_politique": None,
        "reputation_criminelle": 0,
        "tension_fragment": 0,
        "corruption": 0,
        "connaissance_temporelle": 0,
        "respect_morvayn": 0,
        "armee": 0,
        "espionnage": 0,
        "diplomatie": 0,
        "difficulte": "Normal",
        "origine": "Inconnu",
        "fin_majeure": None,
        "fins_atteintes": [],
        "traits_route": [],
        "codex": {},
        "souvenirs": [],
        "composants": {},
        "effets_actifs": {},
        "blessures_graves": [],
        "blessures_narratives": [],
        "succes_narratifs": [],
        "historique_runs": [],
        "reliques_run": [],
        "options": dict(OPTIONS_DEFAUT),
    }.items():
        if not hasattr(joueur, attribut):
            setattr(joueur, attribut, defaut.copy() if isinstance(defaut, (list, dict)) else defaut)
    if joueur.bouclier_equipe not in BOUCLIERS:
        joueur.bouclier_equipe = next((objet for objet in joueur.inventaire if objet in BOUCLIERS), None)
    return joueur

__all__ = ["Joueur", "normaliser_joueur"]
