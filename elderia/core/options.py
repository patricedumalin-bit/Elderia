import json
import os


OPTIONS_DEFAUT = {
    "vitesse_texte": "normale",
    "afficher_bilans": True,
    "confirmer_fins_prematurees": True,
}

def obtenir_chemin_securise(nom_fichier):
    dir_priv = os.environ.get("ANDROID_PRIVATE_DATA")
    if not dir_priv:
        if os.environ.get("HOME") and "android" in os.environ.get("HOME", "").lower():
            dir_priv = os.environ.get("HOME")
    if dir_priv:
        return os.path.join(dir_priv, nom_fichier)
    return nom_fichier

OPTIONS_FICHIER = obtenir_chemin_securise("options.json")

VITESSES_TEXTE = {
    "lente": 0.04,
    "normale": 0.025,
    "rapide": 0.008,
    "instantanee": 0,
}

options_courantes = dict(OPTIONS_DEFAUT)


def appliquer_options(options=None):
    options_courantes.update(OPTIONS_DEFAUT)
    if options:
        options_courantes.update(options)
    return options_courantes


def vitesse_texte():
    return VITESSES_TEXTE.get(options_courantes.get("vitesse_texte"), VITESSES_TEXTE["normale"])


def option_active(nom):
    return bool(options_courantes.get(nom, OPTIONS_DEFAUT.get(nom)))


def charger_options(fichier=OPTIONS_FICHIER):
    try:
        with open(fichier, "r", encoding="utf-8") as flux:
            return appliquer_options(json.load(flux))
    except FileNotFoundError:
        return appliquer_options()


def sauvegarder_options(options=None, fichier=OPTIONS_FICHIER):
    options = appliquer_options(options)
    with open(fichier, "w", encoding="utf-8") as flux:
        json.dump(options, flux, ensure_ascii=False, indent=4)
    return options