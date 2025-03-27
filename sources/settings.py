# Paramètres du jeu ———————————————————————————————————————————————————————————————————————————————————
# —————————————————————————————————————————————————————————————————————————————————————————————————————

# Dimensions de l'écran
SCREEN_WIDTH = 940
SCREEN_HEIGHT = 605

# Paramètres de la fenêtre
BORDERLESS_WINDOW = True  # True pour une fenêtre sans bordure, False pour une fenêtre normale

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Répertoire des ressources (fonctionne à la fois depuis le répertoire racine et le répertoire sources)
import os
ASSETS_DIR = "../assets" if os.path.basename(os.getcwd()) == "sources" else "assets"

# Dossier pour sauvegarder les meilleurs scores
HIGHSCORE_DIR = "../highscore" if os.path.basename(os.getcwd()) == "sources" else "highscore"
HIGHSCORE_FILE = "score.txt"

# Points par type de pixel
WHITE_PIXEL_POINTS = 1    # Points pour chaque pixel blanc détruit
ORANGE_PIXEL_POINTS = 3   # Points pour chaque pixel orange (jaune) détruit
RED_PIXEL_BASE_POINTS = 5 # Points pour chaque pixel rouge touchant la base

# Paramètres de position - toutes les positions sont des décalages x,y depuis l'origine (0,0)
# Paramètres du titre
TITLE_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
TITLE_Y_POSITION = 140
TITLE_HOVER_SPEED = 3  # Vitesse de l'animation de survol
TITLE_HOVER_AMPLITUDE = 10  # Amplitude de mouvement du titre
TITLE_SCALE = 1.0  # Échelle par défaut
TITLE_MAX_SCALE = 1.15  # Échelle maximale lors du survol
TITLE_SCALE_SPEED = 0.01  # Vitesse d'agrandissement/réduction du titre

# Paramètres du score
SCORE_FONT_SIZE = 36  # Taille de la police pour le score en jeu
SCORE_FONT_BOLD = False  # Police sans gras pour le score en jeu
SCORE_FONT_NAME = "Arial"  # Nom de la police pour le score en jeu
SCORE_TEXT_COLOR = WHITE  # Couleur du texte du score en jeu
SCORE_X_POSITION = SCREEN_WIDTH // 2  # Position X du score en jeu
SCORE_Y_POSITION = 40  # Position Y du score en jeu
SCORE_PREFIX = "SCORE: "  # Préfixe du score en jeu
HIGHSCORE_FONT_SIZE = 15  # Taille de la police pour le meilleur score sur l'écran d'accueil
HIGHSCORE_X_POSITION = SCREEN_WIDTH // 2 + 10 # Position X du meilleur score sur l'écran d'accueil (centré)
HIGHSCORE_Y_POSITION = 30  # Position Y du meilleur score sur l'écran d'accueil

# Paramètres de la couronne à côté du meilleur score
CROWN_SCALE = 1.8  # Échelle de l'image de la couronne
CROWN_SPACING = -8  # Espacement entre le texte du meilleur score et la couronne (en pixels)
CROWN_Y_OFFSET = 0  # Décalage vertical de la couronne par rapport au texte (négatif = vers le haut)

# Paramètres du bouton Play
PLAY_BUTTON_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
PLAY_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 - 20  # Légèrement au-dessus du centre
PLAY_BUTTON_SCALE = 0.40

# Paramètres du bouton Options
OPTIONS_BUTTON_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
OPTIONS_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 + 90  # Sous le bouton Play
OPTIONS_BUTTON_SCALE = 0.40
BUTTON_SPACING_MULTIPLIER = 1.2  # Espacement entre les boutons (multiplicateur de la hauteur du bouton)

# Paramètres du bouton Exit
EXIT_BUTTON_X_POSITION = SCREEN_WIDTH // 2 - 3  # Légèrement à gauche du centre
EXIT_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 + 200  # Loin en dessous du centre
EXIT_BUTTON_SCALE = 0.18

# Paramètres de la bordure
BORDER_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
BORDER_Y_POSITION = SCREEN_HEIGHT // 2  # Centré verticalement
BORDER_SCALE = 2.9

# Paramètres de l'image du nom
NAME_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
NAME_Y_POSITION = SCREEN_HEIGHT - 30  # Bas de l'écran avec rembourrage
NAME_SCALE = 0.5

# Paramètres du bouton de sortie du jeu
GAME_EXIT_ICON_X_POSITION = SCREEN_WIDTH // 2  # Centré horizontalement
GAME_EXIT_ICON_Y_POSITION = SCREEN_HEIGHT - 30  # Bas avec rembourrage
GAME_EXIT_ICON_SCALE = 0.125

# Paramètres du cœur
HEART_X_POSITION = SCREEN_WIDTH // 2  # Centre de l'écran horizontalement
HEART_Y_POSITION = SCREEN_HEIGHT // 2  # Centre de l'écran verticalement
HEART_SCALE = 0.1  # Échelle pour l'image du cœur
HEART_BASE_SCALE = 1.3  # Échelle pour la base sous le cœur
INITIAL_LIVES = 5  # Le joueur commence avec 5 vies

# Paramètres du curseur
CURSOR_NORMAL = "cursor_normal.png"
CURSOR_HOVER = "cursor_hovering_selectable_item.png"
CURSOR_CLICK = "cursor_click.png"
CURSOR_ZOOM = "cursor_zoom.png"  # Nouveau curseur de zoom pour le survol du titre
CURSOR_PAINT = "cursor_paint.png"  # Curseur pour le mode jeu
CURSOR_VISIBLE = False  # Masquer le curseur système par défaut

# Paramètres d'échelle du curseur
CURSOR_NORMAL_SCALE = 0.7
CURSOR_HOVER_SCALE = 0.7
CURSOR_CLICK_SCALE = 0.7
CURSOR_ZOOM_SCALE = 0.7
CURSOR_PAINT_SCALE = 0.7

# Effet de survol des boutons
HOVER_DARKNESS = 50  # 0-255, plus élevé est plus sombre

# Paramètres d'animation
FPS = 60  # Images par seconde

# Paramètres d'animation des pixels
PIXEL_MIN_SIZE = 2
PIXEL_MAX_SIZE = 4
PIXEL_MIN_COUNT = 5
PIXEL_MAX_COUNT = 15
PIXEL_MIN_INTERVAL = 1.0  # Intervalle minimum en secondes entre les animations aléatoires
PIXEL_MAX_INTERVAL = 5.0  # Intervalle maximum en secondes entre les animations aléatoires
PIXEL_CLICK_COUNT = 10
PIXEL_BUTTON_HOVER_COUNT = 5  # Nombre de particules à générer lors du survol des boutons
PIXEL_GRAVITY = 2.0      # Force de gravité (0 = pas de gravité, valeurs plus élevées = gravité plus forte)

# Paramètres d'animation de transition
TRANSITION_GRAVITY = 8.0       # Force de gravité pour l'animation de transition (augmentée pour une chute plus rapide)
TRANSITION_MIN_ANGLE = -45     # Angle minimum en degrés pour les éléments de transition (plage d'angle plus large)
TRANSITION_MAX_ANGLE = 45      # Angle maximum en degrés pour les éléments de transition (plage d'angle plus large)
TRANSITION_MIN_SPEED = 100     # Vitesse initiale minimale pour les éléments de transition (augmentée)
TRANSITION_MAX_SPEED = 250     # Vitesse initiale maximale pour les éléments de transition (augmentée)
TRANSITION_ROTATION_SPEED = 3.0  # Facteur de vitesse de rotation pour les éléments de transition (augmenté)
TRANSITION_DURATION = 3.0      # Durée maximale de l'animation de transition en secondes (délai de sécurité)

# Paramètres d'animation du flash d'écran
FLASH_DURATION = 1          # Durée de l'animation du flash d'écran en secondes
FLASH_FADE_SPEED = 1.5

# Paramètres des pixels du jeu
GAME_PIXEL_MIN_SIZE = 17   # Taille minimale des pixels du jeu
GAME_PIXEL_MAX_SIZE = 45  # Taille maximale des pixels du jeu
GAME_PIXEL_BASE_SPEED = 15  # Vitesse de base des pixels
GAME_PIXEL_ACCELERATION = 3.0  # Facteur d'accélération exponentielle (augmenté pour un effet plus dramatique)
GAME_PIXEL_PROXIMITY_THRESHOLD = 400  # Distance à laquelle les pixels commencent à accélérer

# Paramètres d'apparition
GAME_PIXEL_SPAWN_INTERVAL = 3.0  # Intervalle initial en secondes entre les apparitions
GAME_PIXEL_SPAWN_DECREASE_RATE = 0.015  # Diminution de l'intervalle d'apparition par seconde
GAME_PIXEL_SPAWN_MIN_INTERVAL = 0.5  # Intervalle d'apparition minimum
GAME_PIXEL_SPEED_INCREASE_RATE = 0.025  # Augmentation de la vitesse de base par seconde

# Probabilités d'apparition des pixels spéciaux (pourcentage)
RED_PIXEL_ODDS = 10  # 10% de chance pour un pixel rouge
GREEN_PIXEL_ODDS = 2.5  # 2.5% de chance pour un pixel vert
ORANGE_PIXEL_ODDS = 10  # 10% de chance pour un pixel orange

# Paramètres des pixels orange
ORANGE_SPLASH_RADIUS = 150  # Rayon dans lequel le pixel orange génère des pixels blancs
ORANGE_SPLASH_COUNT = 3  # Nombre de pixels blancs générés par le pixel orange

# Paramètres sonores
MUSIC_VOLUME = 0.4  # Volume de la musique de fond (0.0 à 1.0)
SFX_VOLUME = 0.5    # Volume des effets sonores (0.0 à 1.0)
EXPLOSION_VOLUME = 0.4  # Volume des sons d'explosion
COLLECT_VOLUME = 0.5    # Volume des sons de collecte
DEATH_VOLUME = 0.6      # Volume des sons de mort
GAME_OVER_VOLUME = 0.7  # Volume du son de fin de jeu (légèrement plus fort que le son de mort)

# Paramètres du menu options
MUSIC_LABEL_X_POSITION = SCREEN_WIDTH // 2 - 40 # Centré horizontalement
MUSIC_LABEL_Y_POSITION = SCREEN_HEIGHT // 2 - 50  # Au-dessus du centre
MUSIC_LABEL_SCALE = 0.7

SOUND_EFFECTS_LABEL_X_POSITION = SCREEN_WIDTH // 2 - 40 # Centré horizontalement
SOUND_EFFECTS_LABEL_Y_POSITION = SCREEN_HEIGHT // 2 + 50  # En dessous du centre
SOUND_EFFECTS_LABEL_SCALE = 0.7

# Séparation des paramètres pour chaque bouton toggle
# Bouton toggle pour la musique
MUSIC_TOGGLE_OFFSET_X = 150  # Distance horizontale entre le label et le bouton
MUSIC_TOGGLE_SCALE = 0.7
MUSIC_TOGGLE_SHADOW_OFFSET = 3  # Décalage de l'ombre des boutons
MUSIC_TOGGLE_SHADOW_ALPHA = 128  # Transparence de l'ombre (0-255)

# Bouton toggle pour les effets sonores
SOUND_TOGGLE_OFFSET_X = 250  # Distance horizontale entre le label et le bouton
SOUND_TOGGLE_SCALE = 0.7
SOUND_TOGGLE_SHADOW_OFFSET = 3  # Décalage de l'ombre des boutons
SOUND_TOGGLE_SHADOW_ALPHA = 128  # Transparence de l'ombre (0-255)

# Paramètres du bouton de retour (dans le menu options)
OPTIONS_EXIT_BUTTON_X_POSITION = SCREEN_WIDTH // 2
OPTIONS_EXIT_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 + 170
OPTIONS_EXIT_BUTTON_SCALE = 0.25
