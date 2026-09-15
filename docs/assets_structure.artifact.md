# Structure des Actifs Visuels Attendus - Les Chroniques d'Elderia

Pour intégrer les illustrations générées à partir de votre bibliothèque de prompts `VISUAL_PROMPTS.txt`, voici l'arborescence et l'emplacement exact attendu par l'application pour charger correctement les fichiers d'images.

Il est recommandé de créer un dossier racine `assets/images/` à la racine du projet pour stocker ces fichiers au format `.png` ou `.jpg`.

---

## 1. Emplacements des Fichiers Attendus

```text
elderia/
  assets/
    images/
      backgrounds/
        S01_master_key.png
        S02_main_menu.png
        S03_narrative_panel.png
        S04_combat_arena.png
        S05_act_transition.png
      portraits/
        P01_hero_neutral.png
        P02_guerrier.png
        P03_rodeur.png
        P04_mage.png
        P05_paladin.png
        P06_necromancien.png
        P07_lyra.png
```

---

## 2. Table de Correspondance Complète

| Code Prompt | Emplacement Relatif Recommandé | Format Cible | Description Visuelle attendue (16:9 ou 4:5) |
| :--- | :--- | :--- | :--- |
| **S01** | `assets/images/backgrounds/S01_master_key.png` | `16:9` | Héros fatigué devant un sceau brisé sous un ciel bleu-noir. |
| **S02** | `assets/images/backgrounds/S02_main_menu.png` | `16:9` | Tour de guet en ruine à l'aurore, village lointain lueurs ambrées. |
| **S03** | `assets/images/backgrounds/S03_narrative_panel.png` | `16:9` | Texture subtile parchemin noirci et fer fumé. |
| **S04** | `assets/images/backgrounds/S04_combat_arena.png` | `16:9` | Cour en ruines sous un ciel d'orage, failles temporelles bleues. |
| **S05** | `assets/images/backgrounds/S05_act_transition.png` | `16:9` | Route de pierre traversant 5 paysages (village, cité, montagne...). |
| **P01** | `assets/images/portraits/P01_hero_neutral.png` | `4:5` | Portrait rapproché de l'aventurier, cape de voyage. |
| **P02** | `assets/images/portraits/P02_guerrier.png` | `4:5` | Guerrier en armure lourde de fer avec épée et bouclier de bois. |
| **P03** | `assets/images/portraits/P03_rodeur.png` | `4:5` | Rôdeur vigilant avec arc elfique sous la lumière de la lune. |
| **P04** | `assets/images/portraits/P04_mage.png` | `4:5` | Mage en robes bleues avec bâton runique sculpté. |
| **P05** | `assets/images/portraits/P05_paladin.png` | `4:5` | Paladin épuisé en armure d'acier et ivoire. |
| **P06** | `assets/images/portraits/P06_necromancien.png` | `4:5` | Nécromancien en robes sombres, feu froid dans la main. |
| **P07** | `assets/images/portraits/P07_lyra.png` | `4:5` | Lyra, l'archère elfe, cape vert-gris, regard bienveillant mais sur ses gardes. |

---

## 3. Exemple d'Intégration d'Image dans le Code

Une fois vos images placées dans ces dossiers, vous pourrez ajouter l'image au moment souhaité dans n'importe quelle scène avec la ligne suivante :

```python
from elderia.core.io import illustrer

def scene_2a_les_premiers_cris(joueur):
    # Affichage de l'arène de combat ou du background de panique
    illustrer("assets/images/backgrounds/S04_combat_arena.png")
    raconter("Des cris déchirent soudain la nuit paisible de Brumebois...")
```
