# Les Chroniques d'Elderia

Jeu narratif RPG en Python, structure comme un livre dont vous etes le heros avec combats, choix persistants, compagnons, factions, Cristaux, fins multiples et progression meta.

## Lancer le jeu

Depuis la racine du projet :

```powershell
python main.py
```

## Compilation / Build pour Android (Flet)

Pour packager l'application pour Android et obtenir un fichier `.apk` installable, assurez-vous d'avoir installé Flet avec les outils de build requis, puis exécutez la commande suivante depuis la racine du projet :

```powershell
flet build apk
```

> [!NOTE]
> Le code prend automatiquement en compte la structure de stockage d'Android pour enregistrer la sauvegarde (`save.json`) et les options de confort (`options.json`) de manière sécurisée dans le répertoire privé de l'application sans provoquer de `PermissionError`.

Menu principal :

```text
LES CHRONIQUES D'ELDERIA
1. Nouvelle partie
2. Continuer
3. Choisir un acte
4. Chronique & progression
5. Options
6. Quitter
```

Lanceurs directs disponibles :

```powershell
python scripts/run_acte_1.py
python scripts/run_acte_2.py
python scripts/run_acte_3.py
python scripts/run_acte_4.py
python scripts/run_acte_5.py
```

## Tests

```powershell
python -m unittest discover -s tests
```

## Test d'equilibrage rapide

Pour traverser rapidement les textes et les choix narratifs pendant le developpement :

```powershell
python scripts/dev_test_equilibrage.py Guerrier Normal 1 5 premier
```

Le mode test d'equilibrage :

- affiche les textes instantanement
- auto-selectionne les choix narratifs selon la strategie (`premier` ou `aleatoire`)
- garde les combats manuels
- garde les marchands manuels
- garde les repos, soins et ravitaillements manuels
- garde les confirmations de fins prematurees manuelles

Cela permet de tester rapidement le rythme general sans perdre les points importants pour l'equilibrage.

Validation rapide de compilation :

```powershell
python -c "from pathlib import Path; import py_compile; [py_compile.compile(str(path), doraise=True) for path in Path('elderia').rglob('*.py')]; print('PY_COMPILE OK')"
```

## Architecture

```text
elderia/
  acts/       Orchestration jouable des actes
  content/    Textes externalises : scenes, choix, outcomes
  core/       Moteurs et systemes : combat, sauvegarde, scene engine, meta progression
  data/       Tables statiques : classes, armes, factions, fins
  ui/         Interfaces utilisateur
  tests/      Tests automatises unittest
```

## Modules principaux

- `core/models.py` : etat du joueur, progression, inventaire, loyautes, sauvegarde-compatible.
- `core/scene_engine.py` : helpers narratifs (`dire`, `transition`, `consequence`, `secret`, `fin_prematuree`, etc.).
- `core/combat.py` : resolution des combats.
- `core/save.py` : sauvegarde/chargement JSON.
- `core/narrative_state.py` : traits de route, bilans d'acte, route morale, commandement, faction dominante.
- `core/codex.py` : Codex/Chronique et souvenirs persistants.
- `core/ending_variants.py` : variantes internes de fins et Nouvelle Route+.
- `core/meta_progression.py` : compagnons formalises, blessures narratives, reves dynamiques, succes, historique, reliques, completion.
- `core/options.py` : options de confort persistantes dans `options.json`.
- `ui/terminal_ui.py` : menu d'actes, Chronique & progression, relance apres fin.

## Flux de contenu

Chaque acte suit ce principe :

- `content/act_X_scenes.py` contient les textes de scenes longues.
- `content/act_X_choices.py` contient les choix affiches au joueur.
- `content/act_X_outcomes.py` contient reponses, consequences, secrets, journaux, transitions et fins.
- `acts/act_X.py` applique les effets et controle l'ordre des scenes.

Les clefs doivent rester synchronisees entre ces fichiers.

## Ajouter une scene

1. Ajouter le texte dans `content/act_X_scenes.py`.
2. Ajouter les choix dans `content/act_X_choices.py` si la scene est interactive.
3. Ajouter les outcomes dans `content/act_X_outcomes.py`.
4. Ajouter une fonction `scene_...` dans `acts/act_X.py`.
5. Brancher la fonction dans `jouer_acte_X` avec une transition si necessaire.
6. Compiler et lancer les tests.

## Ajouter une fin

1. Ajouter le nom dans `data/tables.py` si elle compte comme fin decouvrable.
2. Ajouter le texte long dans le bon fichier `*_outcomes.py`.
3. Pour une fin prematuree, utiliser `fin_prematuree(joueur, outcomes, key, nom_fin)`.
4. Pour une fin finale, ajouter la condition dans `fins_disponibles` de `acts/act_5.py`.
5. Ajouter une variante interne si necessaire dans `core/ending_variants.py`.
6. Tester l'unicite avec `enregistrer_fin_atteinte`.

## Systemes narratifs

Le jeu utilise maintenant :

- fins conditionnelles et fins prematurees non letales
- compteur de fins distinctes decouvertes
- Nouvelle Route+
- Codex / Chronique
- souvenirs persistants
- traits de route
- bilan d'acte
- variantes internes de fins
- scenes exclusives de Cristal, faction, Morvayn et Lyra
- statuts formalises des compagnons (8 compagnons : Lyra, Garrick, Borin, Morvayn, Kael, Selene, Elara, Mira aux Corbeaux)
- interactions entre compagnons (`core/gameplay.py::interaction_compagnons`, table `BANTERS_COMPAGNONS` dans `data/tables.py`) : dialogues declenches quand deux compagnons precis sont presents ensemble, au camp et a plusieurs moments-cles de l'histoire (serment des compagnons, conseil de guerre, veille avant Malakar)
- blessures et reparations narratives
- reves dynamiques
- succes narratifs non spoilants
- historique des runs
- reliques de run
- score de completion discret
- menu principal complet
- indices de fins non spoilants
- options de confort

## Systemes RPG et equilibrage

- **Combat** (`core/combat.py`) : formules de degats/defense, capacites speciales de boss (`CAPACITES_SPECIALES`), vagues d'ennemis (`lancer_combat_vague`).
- **Progression des ennemis** : PV/force/armure des ennemis calibres pour monter en cours des 5 actes (Acte I ~15-22 PV -> Acte V ~115-140 PV).
- **Equipement** (`core/equipment.py`, `data/tables.py`) :
  - Systeme de rarete Commun/Rare/Epique (`RARETES`, `RARETES_AUTORISEES_PAR_PALIER`) avec verrou par palier d'ennemi (`palier_ennemi`) et par difficulte (`DIFFICULTE_BONUS_RARETE`).
  - Affinite de classe (`AFFINITES_CLASSE`) : chaque arme/armure a une `categorie` (lourde/dague/distance/arcane/legere), et son efficacite varie selon la classe qui la porte.
  - Auto-equipement uniquement si l'objet est reellement meilleur (`Joueur.arme_est_meilleure`/`armure_est_meilleure`).
  - Revente d'equipement non porte a 1/4 du prix chez le marchand (`objets_vendables`, `prix_revente`).
  - Marchand par acte (`MARCHAND_STOCK_ACTE_1..4`) avec remise liee au Charisme et au talent "Influence Marchande".
  - Equipement exclusif de fin de jeu (Tranche-Sceau, Sceptre du Devoreur, Arc du Jugement, Egide du Dernier Age, Voile du Sceau) reserve aux boss de l'Acte V.
- **Arbre de talents** (`ARBRE_TALENTS` dans `data/tables.py`, `Joueur.choisir_talent_arbre`/`effets_talents_arbre`) : 4 paliers par classe (niveaux 5/15/30/45), 2 branches qui se subdivisent au palier 3 pour 4 profils finaux par classe.
- **Difficulte** (`DIFFICULTES`) : 4 modes (Facile/Normal/Difficile/Hardcore), chacun ajustant PV, degats, XP/or et rarete du butin.
- **Effort de guerre** (Acte IV, `armee`/`espionnage`/`diplomatie`) : score cumule qui reduit les PV des boss de l'Acte IV (`bonus_effort_guerre` dans `acts/act_4.py`).

Tests : `tests/test_meta_systems.py` inclut un smoke test complet des 5 actes et un test qui exerce des branches de choix aleatoires pour couvrir la logique au-dela du chemin par defaut.

## Menu Chronique & Progression

Le menu Chronique permet de consulter la progression meta sans reveler les fins non decouvertes par leur nom :

- vue d'ensemble
- Codex
- souvenirs persistants
- traits, succes et reliques
- historique des runs
- indices de fins non spoilants

Les indices donnent des directions vagues comme "preserver une montagne" ou "laisser une porte fermee", sans afficher directement les fins manquantes.

## Options de confort

Les options sont sauvegardees dans `options.json`, separement de `save.json`.

Options disponibles :

- vitesse du texte : `lente`, `normale`, `rapide`, `instantanee`
- bilans d'acte affiches ou masques
- confirmation des fins prematurees activee ou desactivee

## Sauvegarde

La sauvegarde est `save.json`.
Les options de confort sont stockees separement dans `options.json`.

Elle conserve :

- etat courant du joueur
- fins atteintes
- Codex
- souvenirs
- traits de route
- succes narratifs
- historique des runs
- reliques de run

La Nouvelle Route+ conserve la progression meta tout en recreant un nouveau personnage.

## Bonnes pratiques

- Garder la logique systemique dans `core/`.
- Garder les textes dans `content/`.
- Eviter les anciens fichiers legacy.
- Ajouter une clef de contenu explicite et stable pour chaque nouvel outcome.
- Valider apres chaque changement important avec `py_compile` et `unittest`.
- Ne pas afficher les fins non decouvertes par leur nom dans les menus de progression.
