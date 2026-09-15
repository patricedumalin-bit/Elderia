"""Outil de developpement : traverse rapidement la narration (textes et
choix narratifs) pour tester la jouabilite/l'equilibrage, sans modifier le
deroulement des combats ni les interactions de gameplay.

Usage:
    python scripts/dev_test_equilibrage.py [classe] [difficulte] [acte_debut] [acte_fin] [strategie]

    classe      : Guerrier, Rôdeur, Mage, Paladin (defaut: Guerrier)
    difficulte  : Facile, Normal, Difficile, Hardcore (defaut: Normal)
    acte_debut  : 1-5 (defaut: 1)
    acte_fin    : 1-5 (defaut: 5)
    strategie   : premier ou aleatoire (defaut: premier)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elderia.acts import act_1, act_2, act_3, act_4, act_5
from elderia.core import dev_testing
from elderia.core.models import Joueur

ACTES = {1: act_1.jouer, 2: act_2.jouer, 3: act_3.jouer, 4: act_4.jouer, 5: act_5.jouer}


def executer(classe="Guerrier", difficulte="Normal", acte_debut=1, acte_fin=5, strategie="premier"):
    """Lance une traversee rapide de la narration. Les combats restent joues normalement."""
    dev_testing.activer_mode_test(strategie)
    try:
        joueur = Joueur("Testeur d'équilibrage", classe, difficulte)
        print(f"\n=== MODE TEST D'ÉQUILIBRAGE (stratégie: {strategie}) ===")
        print(f"Classe : {classe} | Difficulté : {difficulte} | Actes {acte_debut} à {acte_fin}")
        print("Les textes et choix narratifs sont auto-passés.")
        print("Combats, marchands, repos, soins et ravitaillements restent manuels.\n")
        for numero in range(acte_debut, acte_fin + 1):
            if joueur.pv <= 0:
                print(f"\nLe joueur est tombé avant l'Acte {numero}. Arrêt du test.")
                break
            if joueur.acte_courant == "Épilogue":
                print(f"\nL'histoire est déjà à l'épilogue avant l'Acte {numero}. Arrêt du test.")
                break
            joueur = ACTES[numero](joueur, sauvegarder=False)
            print(
                f"\n--- Fin de l'Acte {numero} : niveau {joueur.niveau}, XP {joueur.xp}, "
                f"or {joueur.or_poches}g, PV {joueur.pv}/{joueur.pv_max} ---"
            )
        return joueur
    finally:
        dev_testing.desactiver_mode_test()


if __name__ == "__main__":
    args = sys.argv[1:]
    classe_arg = args[0] if len(args) > 0 else "Guerrier"
    difficulte_arg = args[1] if len(args) > 1 else "Normal"
    acte_debut_arg = int(args[2]) if len(args) > 2 else 1
    acte_fin_arg = int(args[3]) if len(args) > 3 else 5
    strategie_arg = args[4] if len(args) > 4 else "premier"
    executer(classe_arg, difficulte_arg, acte_debut_arg, acte_fin_arg, strategie_arg)
