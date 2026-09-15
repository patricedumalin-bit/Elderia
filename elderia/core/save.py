import json

from elderia.core.meta_progression import actualiser_meta_progression
from elderia.core.io import raconter
from elderia.core.models import Joueur, normaliser_joueur
from elderia.data.tables import SAUVEGARDE_FICHIER


def sauvegarder(joueur, fichier=SAUVEGARDE_FICHIER):
	joueur.enregistrer_fin_atteinte()
	actualiser_meta_progression(joueur)
	with open(fichier, "w", encoding="utf-8") as sauvegarde:
		json.dump(joueur.__dict__, sauvegarde, ensure_ascii=False, indent=4)
	raconter(f"💾 Partie sauvegardée dans {fichier}.")


def charger(fichier=SAUVEGARDE_FICHIER):
	try:
		with open(fichier, "r", encoding="utf-8") as sauvegarde:
			data = json.load(sauvegarde)
	except FileNotFoundError:
		raconter("Aucune sauvegarde trouvée.")
		return None
	joueur = Joueur(data["nom"], data["classe"])
	joueur.__dict__.update(data)
	normaliser_joueur(joueur)
	raconter(f"📂 Partie chargée depuis {fichier}.")
	return joueur

__all__ = ["SAUVEGARDE_FICHIER", "charger", "sauvegarder"]
