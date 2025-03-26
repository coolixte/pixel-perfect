# Pixel Perfect

Un jeu de réflexes au style pixel art où vous devez protéger votre cœur des pixels envahisseurs.

## Fonctionnalités

- Écran d'accueil animé avec titre flottant et boutons interactifs
- Système de score et de meilleurs scores
- Différents types de pixels avec des comportements uniques :
  - **Pixels blancs** : Donnent 1 point lorsqu'ils sont détruits
  - **Pixels orange** : Donnent 3 points et créent des pixels blancs supplémentaires
  - **Pixels rouges** : Donnent 5 points mais provoquent un Game Over si cliqués
  - **Pixels verts** : Activent des bonus aléatoires quand ils sont cliqués
- Effets visuels de particules
- Musique et effets sonores
- Curseur personnalisé qui change selon le contexte

## Prérequis

- Python 3.6 ou supérieur
- Pygame 2.5.2 ou supérieur

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers
2. Installez les dépendances requises :

```
pip install -r requirements.txt
```

3. Assurez-vous que le dossier "assets" contient toutes les ressources nécessaires

## Comment jouer

Lancez le jeu en exécutant le fichier main.py :

```
python main.py
```

### Règles du jeu

- Vous commencez avec 5 vies représentées par un cœur
- Des pixels apparaissent depuis les bords de l'écran et se dirigent vers le cœur
- Cliquez sur les pixels pour les détruire avant qu'ils n'atteignent votre cœur
- Chaque type de pixel a un comportement différent :
  - **Pixels blancs** : Les plus communs, donnent 1 point par clic
  - **Pixels orange** : Génèrent 2 pixels blancs quand ils sont détruits, 3 points par clic
  - **Pixels rouges** : Dangereux ! Provoquent un Game Over immédiat si vous cliquez dessus, mais donnent 5 points s'ils touchent le cœur
  - **Pixels verts** : Suppriment tout les pixels jaunes et blancs sur l'écran: ils sont rares alors cliquez au moment opportun!
- Perdez une vie quand un pixel blanc ou orange touche votre cœur
- Le jeu devient de plus en plus difficile avec le temps
- Le jeu se termine quand vous perdez vos 5 vies

### Contrôles

- Utilisez la souris pour viser et cliquer sur les pixels 
- Cliquez sur l'icône de sortie en bas de l'écran pour revenir au menu principal

## Structure du projet

```
pixel-perfect/
├── assets/              - Ressources graphiques et sonores
├── sources/             - Code source Python
│   ├── main.py          - Point d'entrée du jeu
│   ├── game.py          - Logique principale du jeu
│   ├── settings.py      - Paramètres configurables
│   ├── cursor_manager.py - Gestion du curseur
│   ├── pixel_animation.py - Animation des pixels
│   └── transition.py    - Effets de transition
├── highscore/           - Sauvegarde des meilleurs scores
```
