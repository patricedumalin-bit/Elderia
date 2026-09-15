"""Outils reserves a la phase de developpement.

Permet de traverser rapidement la narration (textes et choix) sans toucher
au deroulement des combats, pour tester la jouabilite/l'equilibrage.
"""
import random

_ETAT = {"actif": False, "strategie": "premier"}


def activer_mode_test(strategie="premier"):
    """Active le mode test. strategie: 'premier' ou 'aleatoire'."""
    _ETAT["actif"] = True
    _ETAT["strategie"] = strategie if strategie in ("premier", "aleatoire") else "premier"


def desactiver_mode_test():
    _ETAT["actif"] = False


def mode_test_actif():
    return _ETAT["actif"]


def choisir_automatiquement(options):
    if _ETAT["strategie"] == "aleatoire":
        return random.randrange(len(options))
    return 0
