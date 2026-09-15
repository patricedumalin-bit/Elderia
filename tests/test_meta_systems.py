import contextlib
import io
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from elderia.acts import act_1, act_2, act_3, act_4, act_5
from elderia.acts.act_5 import fins_disponibles
from elderia.core.codex import ajouter_souvenir, decouvrir_codex, progression_codex, progression_souvenirs
from elderia.core.meta_progression import actualiser_meta_progression, score_completion
from elderia.core.models import Joueur
from elderia.core.scene_engine import fin_prematuree


class MetaSystemsTest(unittest.TestCase):
    def make_player(self):
        joueur = Joueur("Test", "Guerrier")
        joueur.niveau = 45
        joueur.pv_max = joueur.calculer_pv_max()
        joueur.pv = joueur.pv_max
        joueur.pm = joueur.pm_max
        joueur.energie = joueur.energie_max
        joueur.cristaux = ["Cristal de Vie", "Cristal des Ombres"]
        return joueur

    def test_endings_are_counted_once(self):
        joueur = self.make_player()
        joueur.fin_majeure = "Fin du Roi"
        self.assertTrue(joueur.enregistrer_fin_atteinte())
        self.assertFalse(joueur.enregistrer_fin_atteinte())
        self.assertEqual(joueur.fins_atteintes, ["Fin du Roi"])

    def test_conditional_endings(self):
        normal = self.make_player()
        self.assertNotIn("Fin du Tyran", [nom for nom, _, _ in fins_disponibles(normal)])
        self.assertNotIn("Fin Secrète", [nom for nom, _, _ in fins_disponibles(normal)])

        tyran = self.make_player()
        tyran.alignement = -2
        self.assertIn("Fin du Tyran", [nom for nom, _, _ in fins_disponibles(tyran)])

        secret = self.make_player()
        secret.variables["secret_de_voreur"] = True
        secret.variables["malakar_transmet_savoir"] = True
        secret.variables["lyra_garde_fou"] = True
        secret.connaissance_temporelle = 4
        self.assertIn("Fin Secrète", [nom for nom, _, _ in fins_disponibles(secret)])

    def test_codex_and_souvenirs_are_unique(self):
        joueur = self.make_player()
        self.assertTrue(decouvrir_codex(joueur, "garrick"))
        self.assertFalse(decouvrir_codex(joueur, "garrick"))
        self.assertTrue(ajouter_souvenir(joueur, "main_garrick"))
        self.assertFalse(ajouter_souvenir(joueur, "main_garrick"))
        self.assertEqual(progression_codex(joueur)[0], 1)
        self.assertEqual(progression_souvenirs(joueur)[0], 1)

    def test_premature_ending_records_epilogue(self):
        joueur = self.make_player()
        outcomes = {"ending": "Une fin de test."}
        with patch("builtins.input", lambda prompt="": "1"), patch("time.sleep", lambda _: None), contextlib.redirect_stdout(io.StringIO()):
            fin_prematuree(joueur, outcomes, "ending", "Fin du Roi")
        self.assertEqual(joueur.acte_courant, "Épilogue")
        self.assertEqual(joueur.fin_majeure, "Fin du Roi")
        self.assertEqual(joueur.fins_atteintes, ["Fin du Roi"])

    def test_meta_progression_is_bounded_and_idempotent(self):
        joueur = self.make_player()
        joueur.fin_majeure = "Fin du Sacrifice"
        joueur.enregistrer_fin_atteinte()
        decouvrir_codex(joueur, "brumebois")
        ajouter_souvenir(joueur, "pain_mira")
        actualiser_meta_progression(joueur)
        actualiser_meta_progression(joueur)
        self.assertLessEqual(score_completion(joueur), 100)
        self.assertEqual(len(joueur.historique_runs), 1)
        self.assertEqual(len(joueur.reliques_run), 1)

    def test_full_runtime_smoke(self):
        random.seed(7)
        joueur = Joueur("Smoke", "Guerrier")

        def fake_input(prompt=""):
            return "7" if prompt == "Acheter > " else "1"

        with patch("builtins.input", fake_input), patch("time.sleep", lambda _: None), \
            patch("elderia.acts.act_1.lancer_combat", lambda joueur, ennemi: True), \
            patch("elderia.acts.act_2.lancer_combat", lambda joueur, ennemi: True), \
            patch("elderia.acts.act_3.lancer_combat", lambda joueur, ennemi: True), \
            patch("elderia.acts.act_4.lancer_combat", lambda joueur, ennemi: True), \
            patch("elderia.acts.act_5.lancer_combat", lambda joueur, ennemi: True), \
            patch("elderia.acts.act_2.lancer_combat_vague", lambda joueur, ennemis: True), \
            patch("elderia.acts.act_3.lancer_combat_vague", lambda joueur, ennemis: True), \
            patch("elderia.acts.act_1.visiter_marchand", lambda *args, **kwargs: None), \
            patch("elderia.acts.act_2.visiter_marchand", lambda *args, **kwargs: None), \
            patch("elderia.acts.act_3.visiter_marchand", lambda *args, **kwargs: None), \
            patch("elderia.acts.act_4.visiter_marchand", lambda *args, **kwargs: None), \
            patch("elderia.acts.act_1.lancer_evenement_aleatoire", lambda *args, **kwargs: None), \
            contextlib.redirect_stdout(io.StringIO()):
            act_1.jouer(joueur, sauvegarder=False)
            act_2.jouer(joueur, sauvegarder=False)
            act_3.jouer(joueur, sauvegarder=False)
            act_4.jouer(joueur, sauvegarder=False)
            act_5.jouer(joueur, sauvegarder=False)

        self.assertEqual(joueur.acte_courant, "Épilogue")
        self.assertIsNotNone(joueur.fin_majeure)
        self.assertGreaterEqual(len(joueur.codex), 1)
        self.assertGreaterEqual(len(joueur.souvenirs), 1)

    def test_all_choice_branches_execute_without_error(self):
        """Exercise choice indices other than 0 across every act, to catch bugs in elif/else branches
        that the fixed-input smoke test above never reaches."""
        from elderia.core import dev_testing

        def fake_input(prompt=""):
            return "1"

        dev_testing.activer_mode_test("aleatoire")
        try:
            with patch("builtins.input", fake_input), patch("time.sleep", lambda _: None), \
                patch("elderia.acts.act_1.lancer_combat", lambda joueur, ennemi: True), \
                patch("elderia.acts.act_2.lancer_combat", lambda joueur, ennemi: True), \
                patch("elderia.acts.act_3.lancer_combat", lambda joueur, ennemi: True), \
                patch("elderia.acts.act_4.lancer_combat", lambda joueur, ennemi: True), \
                patch("elderia.acts.act_5.lancer_combat", lambda joueur, ennemi: True), \
                patch("elderia.acts.act_1.visiter_marchand", lambda *args, **kwargs: None), \
                patch("elderia.acts.act_2.visiter_marchand", lambda *args, **kwargs: None), \
                patch("elderia.acts.act_3.visiter_marchand", lambda *args, **kwargs: None), \
                patch("elderia.acts.act_4.visiter_marchand", lambda *args, **kwargs: None), \
                contextlib.redirect_stdout(io.StringIO()):
                for seed in range(15):
                    random.seed(seed)
                    joueur = Joueur("Branches", "Guerrier")
                    try:
                        act_1.jouer(joueur, sauvegarder=False)
                        act_2.jouer(joueur, sauvegarder=False)
                        act_3.jouer(joueur, sauvegarder=False)
                        act_4.jouer(joueur, sauvegarder=False)
                        act_5.jouer(joueur, sauvegarder=False)
                    except Exception as exc:
                        self.fail(f"Seed {seed} raised {type(exc).__name__}: {exc}")
        finally:
            dev_testing.desactiver_mode_test()


if __name__ == "__main__":
    unittest.main()
