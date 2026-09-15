# Guide des Ressources Audio - Les Chroniques d'Elderia

Pour activer l'immersion sonore, vous devez placer les fichiers audio suivants dans le dossier `assets/audio/`.

---

## 1. Structure des dossiers

```text
elderia/
  assets/
    audio/
      bgm/ (Musiques de fond)
        menu_theme.mp3
        exploration_theme.mp3
        combat_theme.mp3
      sfx/ (Effets sonores)
        parchment.mp3 (Bruit de papier/choix narratif)
        sword_clash.mp3 (Bruit de combat)
        level_up.mp3
        dice_roll.mp3
```

---

## 2. Recommandations de sources (Libre de droit)

Voici des liens directs vers des sons correspondant parfaitement à l'ambiance Dark Fantasy :

### Musiques (BGM)
*   **Menu/Ambiance** : [LonePeakMusic - Dark Ethereal Soundscapes](https://lonepeakmusic.itch.io/)
*   **Combat** : Cherchez "Epic Dark Battle" sur [Uppbeat](https://uppbeat.io/browse/music/dark-fantasy).

### Effets Sonores (SFX)
*   **Parchment** : [Freesound - Paper Parchment Rustling](https://freesound.org/people/duckduckpony/sounds/204434/) (Gratuit, CC0).
*   **Sword Clash** : [Mixkit - Sword impacts](https://mixkit.co/free-sound-effects/sword/) (Gratuit, pas d'attribution requise).

---

## 3. Intégration technique
L'application Android est déjà configurée pour chercher ces fichiers. Par exemple, à chaque fois qu'un menu de choix apparaît :
- En mode **Narratif**, le son `assets/audio/sfx/parchment.mp3` est joué.
- En mode **Combat**, le son `assets/audio/sfx/sword_clash.mp3` est déclenché avec un **flash rouge** à l'écran.
