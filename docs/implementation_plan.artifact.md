# Plan d'action pour le débogage et la création de l'APK

Ce plan vise à corriger les erreurs dans `android_ui.py` et à préparer le projet pour une compilation réussie en APK à l'aide de Flet et Buildozer.

## Modifications proposées

### 1. Débogage de [android_ui.py](file:///C:/Users/diane/StudioProjects/elderia/ui/android_ui.py)

#### [MODIFY] [android_ui.py](file:///C:/Users/diane/StudioProjects/elderia/ui/android_ui.py)
- **Correction des Imports** : Remplacer l'import erroné `flet_audio` par les contrôles natifs de `flet`.
- **Simplification de l'Architecture** : Supprimer les méthodes redondantes (`start_act_3`, `start_act_4`, `start_act_5`, etc.) qui tentent de réimplémenter la logique du jeu. Le moteur de jeu est déjà défini dans les fichiers `acts/act_1.py` à `act_5.py` et communique avec l'UI via `AndroidIOHandler`.
- **Unification du lancement** : S'assurer que `create_game` et `load_game` utilisent systématiquement le `threading` pour lancer les actes, permettant ainsi à `AndroidIOHandler` de gérer les interactions sans bloquer l'UI.
- **Optimisation des effets visuels** : S'assurer que les appels à `time.sleep` ne bloquent pas le thread principal de Flet.

### 2. Configuration pour l'APK

#### [MODIFY] [buildozer.spec](file:///C:/Users/diane/StudioProjects/elderia/buildozer.spec)
- Ajouter les `requirements` manquants (flet, pygame, pillow, etc.).
- Rectifier l'entry point pour pointer sur `main.py`.

#### [MODIFY] [requirements.txt](file:///C:/Users/diane/StudioProjects/elderia/requirements.txt)
- Vérifier que toutes les dépendances nécessaires sont listées.

## Plan de vérification

### Tests automatisés
- Exécution de `main.py` sur PC pour vérifier que l'interface Flet se lance sans erreur d'import.
- Simulation d'un début de partie pour vérifier que le `AndroidIOHandler` intercepte bien les textes et les choix.

### Vérification Manuelle
- Lancement de la commande de build APK (soit via Buildozer, soit via `flet build apk`).
- Installation de l'APK sur un émulateur ou un appareil physique.
