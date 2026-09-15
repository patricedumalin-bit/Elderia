import random
import sys
import threading
import time

from elderia.core import dev_testing
from elderia.core.options import vitesse_texte

try:
    import msvcrt
except ImportError:
    msvcrt = None


def _paginer_texte(texte, taille_page=600):
    """Découpe un long texte en pages qui tiennent dans le cadre de narration, en coupant de
    préférence entre paragraphes (puis entre phrases si un paragraphe dépasse à lui seul la page)."""
    pages = []
    page = ""
    for paragraphe in texte.split("\n\n"):
        if len(paragraphe) > taille_page:
            for phrase in paragraphe.replace("\n", " ").split(". "):
                phrase = phrase if phrase.endswith(".") else phrase + "."
                candidat = f"{page}\n\n{phrase}" if page else phrase
                if len(candidat) > taille_page and page:
                    pages.append(page)
                    page = phrase
                else:
                    page = candidat
            continue
        candidat = f"{page}\n\n{paragraphe}" if page else paragraphe
        if len(candidat) > taille_page and page:
            pages.append(page)
            page = paragraphe
        else:
            page = candidat
    if page:
        pages.append(page)
    return pages or [texte]

class IOHandler:
    def raconter(self, texte, vitesse=None): pass
    def illustrer(self, image_path): pass
    def demander_choix(self, invite, options, combat=False, interaction=False): pass
    def lancer_de(self, n, avantage=False, desavantage=False): pass
    def afficher_titre(self): pass
    def maj_combat(self, joueur, ennemi, pv_ennemi): pass
    def effet_combat(self, nom): pass

class TerminalIOHandler(IOHandler):
    def raconter(self, texte, vitesse=None): print(texte)
    def demander_choix(self, invite, options, combat=False, interaction=False):
        return int(input(invite)) - 1
    def lancer_de(self, n, avantage=False, desavantage=False):
        if avantage and desavantage:
            return random.randint(1, n)
        jets = [random.randint(1, n)]
        if avantage or desavantage:
            jets.append(random.randint(1, n))
        return max(jets) if avantage else min(jets) if desavantage else jets[0]
    def illustrer(self, path): print(f"[Image: {path}]")

class AndroidIOHandler(IOHandler):
    def __init__(self, app_instance):
        self.app = app_instance
        self._choix = None
        self._event = threading.Event()
        self._continue_event = threading.Event()
        self.app.story_panel.on_click = self._on_story_click

    def _on_story_click(self, e):
        self._continue_event.set()

    def _attendre_validation(self):
        self._continue_event.clear()
        self.app.continue_indicator.visible = True
        self.app.page.update()
        self._continue_event.wait()
        self.app.continue_indicator.visible = False
        self.app.page.update()

    def illustrer(self, path):
        if not path: return
        p = path.replace("assets/", "").replace(".png", ".jpg")
        if not p.startswith("/"): p = "/" + p

        # Fond vs Illustration
        if "backgrounds" in p or "S0" in p:
            self.app.global_bg.src = p
        else:
            self.app.illustration.src = p
            self.app.illustration.visible = True
        self.app.page.update()

    def raconter(self, texte, vitesse=None):
        if not texte: return
        v = vitesse if vitesse is not None else vitesse_texte()
        for page in _paginer_texte(texte):
            self.app.story_box.value = ""
            if v <= 0:
                self.app.story_box.value = page
                self.app.page.update()
                time.sleep(0.05)
            else:
                for char in page:
                    self.app.story_box.value += char
                    self.app.page.update()
                    time.sleep(v)
            # Chaque page de narration attend un clic avant de laisser place à la suivante.
            self._attendre_validation()

    def maj_combat(self, joueur, ennemi, pv_ennemi):
        self.app.update_combat_stats(joueur, ennemi, pv_ennemi)

    def effet_combat(self, nom):
        self.app.jouer_effet_combat(nom)

    def demander_choix(self, invite, options, combat=False, interaction=False):
        import flet as ft
        self._choix = None
        self._event.clear()

        # Update HUD / cadres de combat
        self.app.refresh_hero_panel()
        self.app.set_combat_mode(combat)
        self.app.set_layout_mode(len(options))

        def on_click(e):
            self._choix = e.control.data
            self._event.set()

        def bouton_choix(libelle, data, disabled=False, bgcolor="#26263a", color=None):
            # Texte justifié à gauche (y compris sur plusieurs lignes) au lieu du centrage par défaut ;
            # bordure ambrée + fond distinct + texte teinté parchemin pour bien ressortir du bouton.
            return ft.ElevatedButton(
                content=ft.Container(
                    content=ft.Text(
                        libelle, size=14, color=color or ("#707070" if disabled else "#f0dfb0"),
                        text_align="left",
                        expand=True,
                    ),
                    alignment=ft.Alignment(-1, 0), padding=ft.Padding(2, 0, 2, 0),
                ),
                data=data, on_click=on_click, expand=True, disabled=disabled,
                style=ft.ButtonStyle(
                    bgcolor=bgcolor,
                    side=ft.BorderSide(1, "#5a4a2a" if not disabled else "#3a3a3a"),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            )

        self.app.choice_panel.controls.clear()
        est_marchand = invite.strip().startswith("Acheter")
        joueur = getattr(self.app, "joueur", None)
        for i, opt in enumerate(options):
            if est_marchand and isinstance(opt, tuple) and joueur is not None:
                nom, prix = opt
                if nom == "Utiliser la Forge":
                    from elderia.core.crafting import peut_forger
                    indisponible = not peut_forger(joueur)
                    libelle = f"{nom}{' (aucune recette prête)' if indisponible else ''}"
                    self.app.choice_panel.controls.append(
                        bouton_choix(
                            libelle, i, disabled=indisponible,
                            bgcolor="#2a2a2a" if indisponible else "black26",
                            color="#707070" if indisponible else None,
                        )
                    )
                    continue
                trop_cher = bool(prix) and joueur.or_poches < prix
                deltas = joueur.delta_equipement(nom)
                if not deltas:
                    suffixe = ""
                else:
                    suffixe = "  (" + " ".join(
                        f"{abrev}{'+' if valeur > 0 else ''}{valeur}" for abrev, valeur in deltas
                    ) + ")"
                libelle = f"{nom} — {prix}g{suffixe}" if prix else f"{nom}{suffixe}"
                self.app.choice_panel.controls.append(
                    bouton_choix(
                        libelle, i, disabled=trop_cher,
                        bgcolor="#2a2a2a" if trop_cher else "black26",
                        color="#707070" if trop_cher else None,
                    )
                )
            else:
                self.app.choice_panel.controls.append(bouton_choix(str(opt), i))
        self.app.choice_frame.visible = True
        self.app.page.update()

        self._event.wait()
        self.app.choice_frame.visible = False
        self.app.page.update()
        return self._choix

    def lancer_de(self, n, avantage=False, desavantage=False):
        if avantage and desavantage:
            res = random.randint(1, n)
        else:
            jets = [random.randint(1, n)]
            if avantage or desavantage:
                jets.append(random.randint(1, n))
            res = max(jets) if avantage else min(jets) if desavantage else jets[0]
        return res

_handler = TerminalIOHandler()
def set_io_handler(h): global _handler; _handler = h
def illustrer(p): _handler.illustrer(p)
def raconter(t, v=None): _handler.raconter(t, v)
def demander_choix(invite, options, combat=False, interaction=False): return _handler.demander_choix(invite, options, combat, interaction)
def lancer_de(n, avantage=False, desavantage=False): return _handler.lancer_de(n, avantage, desavantage)
def afficher_titre(): _handler.afficher_titre()
def maj_combat(joueur, ennemi, pv_ennemi): _handler.maj_combat(joueur, ennemi, pv_ennemi)
def effet_combat(nom): _handler.effet_combat(nom)
