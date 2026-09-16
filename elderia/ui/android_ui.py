import random
import threading
import time
from collections import Counter
import flet as ft

from elderia.core.combat import calculer_degats, creer_ennemi, defense_totale, donner_loot, type_ennemi
from elderia.core.equipment import generer_stock, objets_vendables, prix_revente
from elderia.core.models import Joueur
from elderia.core.save import charger, sauvegarder
from elderia.core.options import (
    VITESSES_TEXTE,
    charger_options,
    sauvegarder_options,
)
from elderia.core.systems import MARCHAND_STOCK_ACTE_1
from elderia.data.tables import ARMES, ARMURES, BIJOUX, BOUCLIERS, CLASSES, DIFFICULTES, ORIGINES

PORTRAITS_CLASSE = {
    "Guerrier": "/images/portraits/P02_guerrier.jpg",
    "Rôdeur": "/images/portraits/P03_rodeur.jpg",
    "Mage": "/images/portraits/P04_mage.jpg",
    "Paladin": "/images/portraits/P05_paladin.jpg",
    "Nécromancien": "/images/portraits/P06_necromancien.jpg",
}
PORTRAIT_HEROS_DEFAUT = "/images/portraits/P01_hero_neutral.jpg"

PORTRAITS_ENNEMIS = {
    "Porteur de Cendres": "/images/enemies/E01_porteur_cendres.jpg",
    "Garde Cendreux": "/images/enemies/E02_garde_cendreux.jpg",
    "Squelette": "/images/enemies/E03_spectre_enchaine.jpg",
    "Gardien du Cristal": "/images/enemies/E04_gardien_cristal.jpg",
    "Chasseur du Cristal": "/images/enemies/E05_chasseur_cristal.jpg",
}
PORTRAIT_ENNEMI_DEFAUT = "/images/enemies/E08_echo_temps.jpg"


def _fmt_stat_equipement(total, bonus):
    """Formatte une stat en affichant la part apportée par l'équipement, ex: '11(+2)'."""
    if bonus > 0:
        return f"{total}(+{bonus})"
    if bonus < 0:
        return f"{total}({bonus})"
    return f"{total}"

# Palette de secours pour distinguer visuellement les types d'ennemis qui partagent le même portrait
# par défaut (faute d'illustration dédiée) : une bordure teintée selon le nom du type.
_PALETTE_TYPES_ENNEMIS = ["#5a3a1a", "#1a5a3a", "#3a1a5a", "#5a1a4a", "#1a4a5a", "#4a5a1a"]


def _couleur_type_ennemi(type_ennemi_nom):
    # somme des codes de caractères plutôt que hash() (randomisé par process en Python) pour une
    # couleur stable d'une partie à l'autre pour un même type d'ennemi.
    indice = sum(ord(c) for c in type_ennemi_nom) % len(_PALETTE_TYPES_ENNEMIS)
    return _PALETTE_TYPES_ENNEMIS[indice]

class ElderiaAndroidApp:
    def __init__(self):
        self.joueur = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Elderia - RPG"
        page.theme_mode = "dark"
        page.padding = 0
        page.bgcolor = "black"

        # Police thematique (serif medievale) pour coller a l'univers du jeu
        page.fonts = {
            "Cinzel": "https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf"
        }
        page.theme = ft.Theme(font_family="Cinzel")
        page.dark_theme = ft.Theme(font_family="Cinzel")

        # Fenêtre au format portrait smartphone (ratio 9:16)
        page.window.width = 405
        page.window.height = 720
        page.window.min_width = 405
        page.window.min_height = 720
        page.window.max_width = 405
        page.window.max_height = 720
        page.window.resizable = False

        # Background
        self.global_bg = ft.Image(src="/images/backgrounds/S02_main_menu.jpg", fit="cover", expand=True, opacity=0.8)

        # HUD (hors combat) - véritable bandeau héros : portrait, nom/classe/niveau, PV/NRJ, stats, or
        self.hero_portrait = ft.Image(src="", width=52, height=52, fit="cover")
        self.hero_portrait_frame = ft.Container(
            content=self.hero_portrait, width=52, height=52, border_radius=10,
            clip_behavior="antiAlias", border=ft.border.all(1, "#3a3a3a"),
        )
        self.hud_name_text = ft.Text("", size=14, color="white", weight="bold")
        self.hud_class_text = ft.Text("", size=11, color="#bbbbbb")
        self.hp_text = ft.Text("PV: -/-", size=11, color="white")
        self.nrj_text = ft.Text("NRJ: -/-", size=11, color="white")
        self.hud_hp_bar = ft.ProgressBar(value=1.0, color="red", bgcolor="#3a0000", width=120, height=7)
        self.hud_nrj_bar = ft.ProgressBar(value=1.0, color="cyan", bgcolor="#0a1a2a", width=120, height=7)
        self.hud_stats_text = ft.Text("", size=10, color="#aaccdd")
        self.hud_xp_bar = ft.ProgressBar(value=0.0, color="amber", bgcolor="#2a1f0a", width=120, height=5)
        self.or_text = ft.Text("-g", size=14, color="amber", weight="bold")

        self.hud_panel = ft.Container(
            content=ft.Row([
                ft.GestureDetector(content=self.hero_portrait_frame, on_tap=self.show_fiche),
                ft.Column([
                    ft.Row([self.hud_name_text, self.hud_class_text], spacing=6),
                    ft.Row([self.hp_text, self.hud_hp_bar], spacing=6),
                    ft.Row([self.nrj_text, self.hud_nrj_bar], spacing=6),
                    self.hud_stats_text,
                    self.hud_xp_bar,
                ], spacing=2, tight=True, expand=True),
                ft.Column([ft.Text("OR", size=10, color="#bbbbbb"), self.or_text], horizontal_alignment="center", spacing=0),
            ], alignment="start", vertical_alignment="center", spacing=10),
            padding=10, bgcolor="#101010", visible=False,
            border=ft.border.only(bottom=ft.border.BorderSide(2, "#3a3a3a")),
        )

        # Illustration de narration - plein écran en arrière-plan (derrière le texte semi-transparent)
        self.illustration = ft.Image(src="", visible=False, expand=True, fit="cover", opacity=0.85)

        # Zone de combat - deux cadres compacts côte à côte : ennemi (gauche) et héros (droite)
        self.enemy_name_text = ft.Text("", color="#ff8888", weight="bold", size=13)
        self.enemy_portrait = ft.Image(src="", width=70, height=76, fit="contain")
        self.enemy_hp_bar = ft.ProgressBar(value=1.0, color="red", bgcolor="#3a0000", width=140, height=8)
        self.enemy_hp_text = ft.Text("PV: -/-", size=11, color="white")
        self.enemy_stats_text = ft.Text("", size=10, color="#ddaaaa")
        self.enemy_card = ft.Container(
            expand=True, padding=8, bgcolor="#1a0808", border=ft.border.all(2, "#5a1a1a"), border_radius=10,
            content=ft.Column([
                ft.Text("ENNEMI", size=10, color="#ff8888", weight="bold"),
                self.enemy_name_text, self.enemy_portrait,
                self.enemy_hp_text, self.enemy_hp_bar, self.enemy_stats_text,
            ], horizontal_alignment="center", spacing=2, tight=True)
        )

        self.hero_name_text = ft.Text("", color="#88bbff", weight="bold", size=13)
        self.hero_combat_portrait = ft.Image(src="", width=70, height=76, fit="contain")
        self.combat_hp_bar = ft.ProgressBar(value=1.0, color="green", bgcolor="#0a2a0a", width=140, height=8)
        self.combat_nrj_bar = ft.ProgressBar(value=1.0, color="cyan", bgcolor="#0a1a2a", width=140, height=8)
        self.combat_hp_text = ft.Text("PV: -/-", size=11, color="white")
        self.combat_nrj_text = ft.Text("NRJ: -/-", size=11, color="white")
        self.hero_stats_text = ft.Text("", size=10, color="#aaccdd")
        self.hero_card = ft.Container(
            expand=True, padding=8, bgcolor="#081420", border=ft.border.all(2, "#1a3a5a"), border_radius=10,
            content=ft.Column([
                ft.Text("HÉROS", size=10, color="#88bbff", weight="bold"),
                self.hero_name_text, self.hero_combat_portrait,
                self.combat_hp_text, self.combat_hp_bar,
                self.combat_nrj_text, self.combat_nrj_bar,
                self.hero_stats_text,
            ], horizontal_alignment="center", spacing=2, tight=True)
        )

        self.combat_panel = ft.Container(
            visible=False, alignment=ft.Alignment(0, 0), padding=ft.Padding(10, 10, 10, 0),
            animate_offset=100, offset=ft.Offset(0, 0),
            content=ft.Row(
                [self.enemy_card, self.hero_card],
                alignment="center", vertical_alignment="start", spacing=8
            )
        )

        # Effet visuel plein écran (flash) pour les coups portés/reçus, critiques et victoires en combat
        self.combat_flash = ft.Container(
            expand=True, visible=False, opacity=0, animate_opacity=150, bgcolor="red",
        )

        # Texte de narration - occupe l'espace restant (agrandi au maximum) hors combat ; le cadre de
        # choix ci-dessous est dimensionné dynamiquement par set_layout_mode() pour que toutes les
        # options restent visibles sans défilement.
        self.story_box = ft.Text("L'aventure commence...", size=16, color="white", font_family="Cinzel")
        self.continue_indicator = ft.Text("▼ Toucher pour continuer", size=12, color="#cccccc", visible=False)
        self.story_panel = ft.Container(
            content=ft.Column([self.story_box, self.continue_indicator], scroll="auto"),
            padding=16, bgcolor=ft.Colors.with_opacity(0.55, "#141414"), expand=True, visible=False,
            border=ft.border.all(2, "#3a3a3a"), ink=False, width=405, # Force l'alignement sur TOUTE la largeur de l'écran du smartphone (405px)
        )

        # Choix / résultats (achat, butin, forge...) - cadre séparé sous le texte, dimensionné par
        # set_layout_mode() pour contenir toutes les options (marchand, forge...) sans défilement
        self.choice_panel = ft.Column(spacing=6, scroll="auto", horizontal_alignment="stretch")
        self.choice_frame = ft.Container(
            content=self.choice_panel,
            padding=ft.Padding(14, 10, 14, 10), bgcolor=ft.Colors.with_opacity(0.85, "#101018"), height=150, visible=False,
            border=ft.border.all(2, "#3a3a3a"),
            border_radius=ft.border_radius.only(top_left=18, top_right=18),
        )

        # Menu Principal
        self.name_field = ft.TextField(label="Nom du Héros", width=250)
        self.class_field = ft.Dropdown(label="Classe", width=250, options=[ft.DropdownOption(c) for c in CLASSES], value="Guerrier")
        self.difficulte_field = ft.Dropdown(label="Difficulté", width=250, options=[ft.DropdownOption(d) for d in DIFFICULTES], value="Normal")
        self.origine_field = ft.Dropdown(label="Origine", width=250, options=[ft.DropdownOption(o) for o in ORIGINES], value=next(iter(ORIGINES)))
        self.setup_panel = ft.Container(
            content=ft.Column([
                ft.Text("ELDERIA", size=40, weight="bold", color="amber"),
                self.name_field, self.class_field, self.difficulte_field, self.origine_field,
                ft.ElevatedButton("COMMENCER", on_click=self.create_game, bgcolor="amber", color="black", width=200),
                ft.TextButton("Charger une partie", on_click=self.load_game),
                ft.TextButton("Options", on_click=self.show_options)
            ], horizontal_alignment="center", spacing=20, scroll="auto"),
            alignment=ft.Alignment(0, 0), expand=True
        )

        # Panneau Options
        options = charger_options()
        self.vitesse_field = ft.Dropdown(
            label="Vitesse du texte", width=250,
            options=[ft.DropdownOption(v) for v in VITESSES_TEXTE],
            value=options["vitesse_texte"]
        )
        self.bilans_switch = ft.Switch(label="Afficher les bilans d'acte", value=options["afficher_bilans"])
        self.confirm_switch = ft.Switch(label="Confirmer les fins prématurées", value=options["confirmer_fins_prematurees"])
        self.options_panel = ft.Container(
            content=ft.Column([
                ft.Text("OPTIONS", size=30, weight="bold", color="amber"),
                self.vitesse_field, self.bilans_switch, self.confirm_switch,
                ft.ElevatedButton("ENREGISTRER", on_click=self.save_options, bgcolor="amber", color="black", width=200),
                ft.TextButton("Retour", on_click=self.hide_options)
            ], horizontal_alignment="center", spacing=20, scroll="auto"),
            alignment=ft.Alignment(0, 0), expand=True, visible=False
        )

        # Panneau Fiche personnage (caractéristiques, équipement, inventaire, quêtes, compagnons)
        self.fiche_titre = ft.Text("", size=22, weight="bold", color="amber")
        self.fiche_ressources = ft.Text("", size=13, color="white")
        self.fiche_carac = ft.Text("", size=13, color="#aaccdd")
        self.fiche_equipement = ft.Text("", size=13, color="white")
        self.fiche_inventaire = ft.Text("", size=12, color="#dddddd")
        self.fiche_quetes = ft.Text("", size=12, color="#cceecc")
        self.fiche_compagnons = ft.Text("", size=12, color="#cce0ff")
        self.fiche_panel = ft.Container(
            content=ft.Column([
                self.fiche_titre,
                ft.Text("RESSOURCES", size=12, weight="bold", color="#888888"), self.fiche_ressources,
                ft.Text("CARACTÉRISTIQUES", size=12, weight="bold", color="#888888"), self.fiche_carac,
                ft.Text("ÉQUIPEMENT", size=12, weight="bold", color="#888888"), self.fiche_equipement,
                ft.Text("INVENTAIRE", size=12, weight="bold", color="#888888"), self.fiche_inventaire,
                ft.Text("QUÊTES", size=12, weight="bold", color="#888888"), self.fiche_quetes,
                ft.Text("COMPAGNONS", size=12, weight="bold", color="#888888"), self.fiche_compagnons,
                ft.TextButton("Fermer", on_click=self.hide_fiche),
            ], spacing=6, scroll="auto"),
            padding=16, bgcolor="#101010", expand=True, visible=False,
            border=ft.border.all(2, "#3a3a3a"),
        )

        # Assemblage
        self.main_view = ft.Stack([
            self.global_bg,
            self.illustration,
            ft.Column([
                self.hud_panel,
                self.combat_panel,
                self.story_panel,
                self.choice_frame
            ], expand=True),
            self.combat_flash,
            self.fiche_panel,
            self.setup_panel,
            self.options_panel
        ], expand=True)

        page.add(self.main_view)

    def show_fiche(self, _e):
        if not self.joueur: return
        self.refresh_fiche()
        self.fiche_panel.visible = True
        self.page.update()

    def hide_fiche(self, _e):
        self.fiche_panel.visible = False
        self.page.update()

    def refresh_fiche(self):
        j = self.joueur
        if not j: return
        self.fiche_titre.value = f"{j.nom} — {j.classe} niv. {j.niveau} ({j.difficulte})"
        self.fiche_ressources.value = (
            f"PV {j.pv}/{j.pv_max}  |  Énergie {j.energie}/{j.energie_max}  |  Mana {j.pm}/{j.pm_max}\n"
            f"XP {j.xp}/{j.xp_prochain_niveau}  |  Or {j.or_poches}g  |  Réputation {j.reputation}"
        )
        self.fiche_carac.value = (
            f"FOR {j.force_totale} | AGI {j.agilite_totale} | END {j.endurance} | "
            f"INT {j.intelligence_totale} | VOL {j.volonte} | CHA {j.charisme}"
        )
        self.fiche_equipement.value = (
            f"Arme : {j.arme}\nArmure : {j.armure}\n"
            f"Bouclier : {j.bouclier or 'Aucun'}\nBijou : {j.bijou or 'Aucun'}\n"
            f"Compétence : {j.competence}"
        )
        self.fiche_inventaire.value = (
            f"({j.emplacements_utilises}/{j.capacite_inventaire}) " + (", ".join(j.inventaire) if j.inventaire else "Vide")
        )
        self.fiche_quetes.value = "\n".join(
            f"{'[x]' if fait else '[ ]'} {nom}" for nom, fait in j.quetes.items()
        ) or "Aucune"
        self.fiche_compagnons.value = "\n".join(
            f"{nom} (loyauté {j.loyautes.get(nom, 0)}/100)" for nom in j.compagnons
        ) or "Aucun compagnon recruté"
        self.page.update()

    def show_options(self, _e):
        self.setup_panel.visible = False
        self.options_panel.visible = True
        self.page.update()

    def hide_options(self, _e):
        self.options_panel.visible = False
        self.setup_panel.visible = True
        self.page.update()

    def save_options(self, _e):
        sauvegarder_options({
            "vitesse_texte": self.vitesse_field.value,
            "afficher_bilans": self.bilans_switch.value,
            "confirmer_fins_prematurees": self.confirm_switch.value,
        })
        self.hide_options(_e)

    def create_game(self, _e):
        nom = self.name_field.value.strip()
        if not nom: return
        self.joueur = Joueur(nom, self.class_field.value, self.difficulte_field.value, self.origine_field.value)
        self.start_engine()

    def load_game(self, _e):
        j = charger()
        if not j: return
        self.joueur = j
        self.start_engine()

    def start_engine(self):
        self.setup_panel.visible = False
        self.hud_panel.visible = True
        self.story_panel.visible = True
        self.choice_frame.visible = True
        self.refresh_hero_panel()

        from elderia.core.io import set_io_handler, AndroidIOHandler
        set_io_handler(AndroidIOHandler(self))
        self.page.update()

        self._demarrer_thread_acte(self.joueur)

    def _demarrer_thread_acte(self, joueur):
        # Empêche deux threads d'acte de tourner en même temps (double-clic, création puis chargement rapide, etc.)
        if getattr(self, "_act_thread", None) and self._act_thread.is_alive():
            return
        self._act_thread = threading.Thread(target=self._jouer_histoire, args=(joueur,), daemon=True)
        self._act_thread.start()

    def _jouer_histoire(self, joueur):
        # Enchaîne automatiquement les actes (I à V) selon joueur.acte_courant, au lieu de s'arrêter
        # silencieusement après la sauvegarde de fin d'acte comme le faisait l'ancien lancement direct.
        from elderia.acts import act_1, act_2, act_3, act_4, act_5
        actes = [
            ("Acte I", act_1.jouer),
            ("Acte II", act_2.jouer),
            ("Acte III", act_3.jouer),
            ("Acte IV", act_4.jouer),
            ("Acte V", act_5.jouer),
        ]
        while joueur.pv > 0 and joueur.acte_courant != "Épilogue":
            # Comparaison EXACTE du numéro d'acte (avant le " - ") : un simple startswith() est piégé
            # car "Acte II - ...".startswith("Acte I") est vrai (bouclait indéfiniment sur l'Acte I).
            numero = joueur.acte_courant.split(" - ")[0].strip()
            fonction = next((f for prefixe, f in actes if numero == prefixe), None)
            if fonction is None:
                break
            joueur = fonction(joueur) or joueur

        if joueur.pv <= 0:
            # Mort ou abandon : on nettoie complètement le panneau de choix pour retirer
            # l'ancien écran Game Over de Flet avant de réafficher le menu de création d'un nouveau héros.
            self.choice_panel.controls.clear()
            self._retour_menu_creation()

    def _retour_menu_creation(self):
        self.joueur = None
        self.name_field.value = ""
        self.hud_panel.visible = False
        self.story_panel.visible = False
        self.choice_frame.visible = False
        self.combat_panel.visible = False
        self.setup_panel.visible = True
        self.page.update()

    def refresh_hero_panel(self):
        if not self.joueur: return
        j = self.joueur
        self.hero_portrait.src = PORTRAITS_CLASSE.get(j.classe, PORTRAIT_HEROS_DEFAUT)
        self.hud_name_text.value = j.nom
        self.hud_class_text.value = f"{j.classe} niv. {j.niveau}"
        self.hp_text.value = f"PV {j.pv}/{j.pv_max}"
        self.nrj_text.value = f"NRJ {j.energie}/{j.energie_max}"
        self.hud_hp_bar.value = max(0.0, j.pv / j.pv_max) if j.pv_max else 0
        self.hud_nrj_bar.value = max(0.0, j.energie / j.energie_max) if j.energie_max else 0
        force = _fmt_stat_equipement(j.force_totale, j.force_totale - j.force)
        agilite = _fmt_stat_equipement(j.agilite_totale, j.agilite_totale - j.agilite)
        self.hud_stats_text.value = (
            f"FOR {force} | AGI {agilite} | END {j.endurance} | "
            f"RED {j.defense} | Défense {j.defense_combat}"
        )
        self.hud_xp_bar.value = min(1.0, j.xp / j.xp_prochain_niveau) if j.xp_prochain_niveau else 0
        self.or_text.value = f"{j.or_poches}g"
        self.page.update()

    def set_combat_mode(self, is_combat):
        # Bascule entre l'illustration de narration et les cadres dédiés au combat (ennemi + héros)
        self.illustration.visible = (not is_combat) and bool(self.illustration.src)
        self.combat_panel.visible = is_combat
        self.hud_panel.visible = not is_combat
        self.page.update()

    def set_layout_mode(self, nb_options):
        # Augmente la hauteur estimée par option (passant de 58 à 75) pour prendre en compte les retours
        # à la ligne automatiques des textes longs, garantissant ainsi que tout soit visible sans coupure.
        hauteur = 45 + nb_options * 75
        self.choice_frame.height = min(560, max(110, hauteur))
        self.choice_frame.width = 405  # Force l'alignement sur TOUTE la largeur de l'écran du smartphone (405px)
        self.choice_frame.expand = None
        self.story_panel.expand = True
        self.page.update()

    def update_combat_stats(self, joueur, ennemi, pv_ennemi):
        pv_max_ennemi = ennemi.get("pv", pv_ennemi) or 1
        type_actuel = type_ennemi(ennemi)
        self.enemy_name_text.value = ennemi.get("nom", "Ennemi")
        self.enemy_portrait.src = PORTRAITS_ENNEMIS.get(type_actuel, PORTRAIT_ENNEMI_DEFAUT)
        # Sans portrait dédié, une teinte de bordure propre au type aide au moins à distinguer les ennemis.
        self.enemy_card.border = ft.border.all(
            2, "#5a1a1a" if type_actuel in PORTRAITS_ENNEMIS else _couleur_type_ennemi(type_actuel)
        )
        self.enemy_hp_text.value = f"PV: {max(0, pv_ennemi)}/{pv_max_ennemi}"
        self.enemy_hp_bar.value = max(0.0, min(1.0, pv_ennemi / pv_max_ennemi))
        self.enemy_stats_text.value = f"AGI {ennemi.get('agilite', 0)} | Armure {ennemi.get('armure', 0)}"

        self.hero_name_text.value = f"{joueur.nom} | {joueur.classe} niv. {joueur.niveau}"
        self.hero_combat_portrait.src = PORTRAITS_CLASSE.get(joueur.classe, PORTRAIT_HEROS_DEFAUT)
        self.combat_hp_text.value = f"PV: {joueur.pv}/{joueur.pv_max}"
        self.combat_nrj_text.value = f"NRJ: {joueur.energie}/{joueur.energie_max}"
        self.combat_hp_bar.value = max(0.0, joueur.pv / joueur.pv_max) if joueur.pv_max else 0
        self.combat_nrj_bar.value = max(0.0, joueur.energie / joueur.energie_max) if joueur.energie_max else 0
        force = _fmt_stat_equipement(joueur.force_totale, joueur.force_totale - joueur.force)
        agilite = _fmt_stat_equipement(joueur.agilite_totale, joueur.agilite_totale - joueur.agilite)
        self.hero_stats_text.value = (
            f"FOR {force} | AGI {agilite} | END {joueur.endurance} | "
            f"RED {joueur.defense} | Défense {joueur.defense_combat}"
        )
        self.page.update()

    def handle_resize(self, _e): self.page.update()

    # Effets visuels de combat : flash coloré plein écran + secousse des cartes de combat
    EFFETS_COMBAT = {
        "joueur_touche": ("#cc2222", True),
        "ennemi_touche": ("#eeeeee", False),
        "critique": ("#ffb300", True),
        "victoire": ("#33cc66", False),
        "soin": ("#33cc99", False),
        "bloque": ("#4488ff", False),
        "levelup": ("#ffd700", False),
    }

    def jouer_effet_combat(self, nom):
        couleur, secousse = self.EFFETS_COMBAT.get(nom, ("#ffffff", False))
        if secousse:
            self.shake()
        if nom == "levelup":
            self.flash(couleur, opacite=0.45, duree=0.3)
        else:
            self.flash(couleur)

    def flash(self, couleur, opacite=0.35, duree=0.12):
        # Désactivation complète des flashs colorés bloquants sur Android/Flet.
        # Seul l'effet shake() ou l'actualisation directe des cartes reste actif pour éviter tout freeze graphique.
        pass

    def shake(self):
        for dx in (0.02, -0.02, 0.015, -0.015, 0):
            self.combat_panel.offset = ft.Offset(dx, 0)
            self.page.update()
            time.sleep(0.04)

    def play_sfx(self, p): pass
    def play_bgm(self, p): pass

if __name__ == "__main__":
    app = ElderiaAndroidApp()
    ft.app(target=app.main, assets_dir="assets")
