import pygame
import sys
import os
import math
import random
import settings
from cursor_manager import CursorManager
from pixel_animation import PixelAnimation
from transition import TransitionAnimation

# Logique du Jeu —————————————————————————————————————————————————————————————————————————————————————————
# ————————————————————————————————————————————————————————————————————————————————————————————————————————

# Fonction utilitaire pour gérer les high scores
def load_highscore():
    """
    Charge le meilleur score à partir du fichier.
    
    Returns:
        int: Le meilleur score enregistré, 0 si aucun score n'existe
    """
    # Vérifie si le dossier highscore existe, sinon le crée
    if not os.path.exists(settings.HIGHSCORE_DIR):
        try:
            os.makedirs(settings.HIGHSCORE_DIR)
        except OSError as e:
            print(f"Erreur lors de la création du dossier highscore: {e}")
            return 0

    highscore_path = os.path.join(settings.HIGHSCORE_DIR, settings.HIGHSCORE_FILE)
    try:
        if os.path.exists(highscore_path):
            with open(highscore_path, 'r') as f:
                return int(f.read().strip())
    except (IOError, ValueError) as e:
        print(f"Erreur lors du chargement du meilleur score: {e}")
    
    return 0

def save_highscore(score):
    """
    Sauvegarde le meilleur score dans le fichier.
    
    Args:
        score (int): Le score à sauvegarder
    """
    # Vérifie si le dossier highscore existe, sinon le crée
    if not os.path.exists(settings.HIGHSCORE_DIR):
        try:
            os.makedirs(settings.HIGHSCORE_DIR)
        except OSError as e:
            print(f"Erreur lors de la création du dossier highscore: {e}")
            return

    highscore_path = os.path.join(settings.HIGHSCORE_DIR, settings.HIGHSCORE_FILE)
    try:
        with open(highscore_path, 'w') as f:
            f.write(str(score))
    except IOError as e:
        print(f"Erreur lors de la sauvegarde du meilleur score: {e}")

class GamePixel:
    """Représente un pixel de jeu qui se déplace vers le cœur."""
    def __init__(self, x, y, angle, size, pixel_type="white"):
        """
        Initialise un pixel de jeu.
        
        Args:
            x (float): Position x initiale
            y (float): Position y initiale
            angle (float): Angle de mouvement en radians
            size (int): Taille du pixel
            pixel_type (str): Type de pixel - "white", "red", "green", ou "orange"
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size  # La taille est maintenant utilisée uniquement pour la mise à l'échelle
        self.type = pixel_type
        self.speed = settings.GAME_PIXEL_BASE_SPEED
        self.dead = False
        self.alpha = 0  # Commence complètement transparent
        self.fade_in_duration = 1.0  # Temps en secondes pour apparaître complètement
        self.fade_in_timer = 0.0  # Minuteur pour l'effet d'apparition
        
        # Ajoute des variables d'état de clignotement
        self.is_blinking = False
        self.blink_timer = 0.0
        self.blink_interval = 0.5  # Commence avec un clignotement plus lent
        self.blink_count = 0
        self.max_blinks = 4  # Nombre de clignotements avant d'éclater
        self.is_visible = True  # Contrôle la visibilité pendant le clignotement
        
        # Ajoute un indicateur pour suivre si ce pixel causera des dommages
        self.will_damage_heart = False
        self.will_apply_powerup = False
        
        # Charge l'image appropriée en fonction du type
        self.load_image()
        
    def load_image(self):
        """Charge l'image appropriée pour ce type de pixel."""
        filename = ""
        if self.type == "white":
            filename = "whitepx.png"
        elif self.type == "red":
            filename = "redpx.png"
        elif self.type == "green":
            filename = "greenpx.png"
        elif self.type == "orange":
            filename = "orangepx.png"
        
        try:
            filepath = os.path.join(settings.ASSETS_DIR, filename)
            if not os.path.exists(filepath):
                print(f"Erreur : Image de pixel '{filepath}' introuvable.")
                # Crée un carré coloré de secours
                base_size = 10  # Taille de base avant d'appliquer le facteur d'échelle
                scaled_size = int(base_size * (self.size / 10.0))  # Échelle relative à la taille de base
                self.image = pygame.Surface((scaled_size, scaled_size))
                if self.type == "white":
                    self.image.fill((255, 255, 255))
                elif self.type == "red":
                    self.image.fill((255, 0, 0))
                elif self.type == "green":
                    self.image.fill((0, 255, 0))
                elif self.type == "orange":
                    self.image.fill((255, 165, 0))
            else:
                self.image = pygame.image.load(filepath)
                # Obtient la taille originale de l'image
                original_size = self.image.get_size()
                # Calcule le facteur d'échelle basé sur la taille demandée
                scale_factor = self.size / max(original_size)
                # Redimensionne l'image
                scaled_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                self.image = pygame.transform.scale(self.image, scaled_size)
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image de pixel {filename}: {e}")
            # Crée un carré coloré de secours avec une taille cohérente
            base_size = 10  # Taille de base avant d'appliquer le facteur d'échelle
            scaled_size = int(base_size * (self.size / 10.0))  # Échelle relative à la taille de base
            self.image = pygame.Surface((scaled_size, scaled_size))
            if self.type == "white":
                self.image.fill((255, 255, 255))
            elif self.type == "red":
                self.image.fill((255, 0, 0))
            elif self.type == "green":
                self.image.fill((0, 255, 0))
            elif self.type == "orange":
                self.image.fill((255, 165, 0))
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # Après que l'image est chargée et que le rectangle est défini, crée une copie pour la manipulation de l'alpha
        if hasattr(self, 'image') and self.image:
            self.original_image = self.image.copy()
            # Crée une version transparente pour l'affichage initial
            self.image = self.original_image.copy()
            self.image.set_alpha(0)
        
    def start_blinking(self):
        """Commence l'effet de clignotement lors de la collision avec la base du cœur"""
        self.is_blinking = True
        self.blink_timer = 0.0
        self.blink_count = 0
        self.blink_interval = 0.5  # Commence avec un clignotement plus lent
        self.is_visible = True
        
    def update(self, dt, heart_x, heart_y):
        """
        Met à jour la position du pixel et vérifie la proximité du cœur.
        
        Args:
            dt (float): Delta temps en secondes
            heart_x (float): Position x du cœur
            heart_y (float): Position y du cœur
            
        Returns:
            bool: True si le pixel est toujours actif, False s'il doit être supprimé
        """
        if self.dead:
            return False
        
        # Gère l'état de clignotement
        if self.is_blinking:
            self.blink_timer += dt
            
            if self.blink_timer >= self.blink_interval:
                # Bascule la visibilité
                self.is_visible = not self.is_visible
                
                # Applique l'alpha en fonction de la visibilité
                if self.is_visible:
                    self.image = self.original_image.copy()
                    self.image.set_alpha(255)
                else:
                    self.image = self.original_image.copy()
                    self.image.set_alpha(0)
                
                # Réinitialise le minuteur et augmente la vitesse de clignotement
                self.blink_timer = 0
                self.blink_count += 0.5  # Compte la moitié pour chaque basculement
                
                # Rend le clignotement plus rapide au fur et à mesure de sa progression
                self.blink_interval = max(0.05, 0.5 - (0.1 * self.blink_count))
                
                # Vérifie si nous avons suffisamment clignoté
                if self.blink_count >= self.max_blinks:
                    self.dead = True
                    return False
            
            # Ne bouge pas pendant le clignotement
            return True
            
        # Met à jour l'effet d'apparition
        if self.fade_in_timer < self.fade_in_duration:
            self.fade_in_timer += dt
            # Calcule le nouvel alpha
            self.alpha = int(255 * min(self.fade_in_timer / self.fade_in_duration, 1.0))
            # Applique l'alpha à l'image
            self.image = self.original_image.copy()
            self.image.set_alpha(self.alpha)
        
        # Calcule le vecteur de direction vers le cœur
        dx = heart_x - self.x
        dy = heart_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalise la direction
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Augmentation exponentielle de la vitesse à mesure que le pixel se rapproche du cœur
        # Utilise une formule exponentielle basée sur la distance
        if distance < settings.GAME_PIXEL_PROXIMITY_THRESHOLD:
            # Calcule la progression (0 = loin, 1 = au cœur)
            progress = 1.0 - distance / settings.GAME_PIXEL_PROXIMITY_THRESHOLD
            # Accélération exponentielle (puissance de 2 pour un effet modéré, augmenter pour un effet plus fort)
            acceleration_factor = 1.0 + (progress * progress * settings.GAME_PIXEL_ACCELERATION)
            current_speed = self.speed * acceleration_factor
        else:
            current_speed = self.speed
            
        # Déplace le pixel vers le cœur
        self.x += dx * current_speed * dt
        self.y += dy * current_speed * dt
        
        # Met à jour la position du rectangle
        self.rect.center = (self.x, self.y)
        
        return True
        
    def draw(self, surface):
        """
        Dessine le pixel sur la surface donnée.
        
        Args:
            surface (Surface): Surface Pygame sur laquelle dessiner
        """
        # Ne dessine le pixel que s'il a une certaine visibilité
        if (not self.is_blinking) or (self.is_blinking and self.is_visible):
            if self.alpha > 0:
                surface.blit(self.image, self.rect)
        
    def check_collision(self, heart_rect):
        """
        Vérifie si le pixel est en collision avec le cœur.
        
        Args:
            heart_rect (Rect): Rectangle Pygame pour le cœur
            
        Returns:
            bool: True si collision, False sinon
        """
        return self.rect.colliderect(heart_rect)
        
    def check_click(self, pos):
        """
        Vérifie si le pixel a été cliqué.
        
        Args:
            pos (tuple): Position de la souris (x, y)
            
        Returns:
            bool: True si cliqué, False sinon
        """
        return self.rect.collidepoint(pos)
        
    def mark_as_dead(self):
        """Marque le pixel comme mort pour qu'il soit supprimé lors de la prochaine mise à jour."""
        self.dead = True

class Game:
    """Classe principale du jeu qui gère l'état et la logique du jeu."""
    def __init__(self, screen, skip_entry_flash=False, music_enabled=True, sound_effects_enabled=True):
        """
        Initialise le jeu.
        
        Args:
            screen (Surface): Surface Pygame sur laquelle dessiner
            skip_entry_flash (bool): Si True, ignore l'effet de fondu initial
            music_enabled (bool): Si False, désactive la musique
            sound_effects_enabled (bool): Si False, désactive les effets sonores
        """
        self.screen = screen
        self.skip_entry_flash = skip_entry_flash
        self.music_enabled = music_enabled
        self.sound_effects_enabled = sound_effects_enabled
        self.running = True
        self.return_to_menu = False  # Indicateur pour retourner au menu
        self.game_over_pending = False  # Indicateur pour suivre la transition différée de fin de jeu
        
        # Système de score
        self.score = 0
        self.highscore = load_highscore()
        
        # Initialise la police pour l'affichage du score
        pygame.font.init()
        try:
            self.font = pygame.font.SysFont(settings.SCORE_FONT_NAME, settings.SCORE_FONT_SIZE, bold=settings.SCORE_FONT_BOLD)
        except pygame.error as e:
            print(f"Erreur lors du chargement de la police: {e}")
            self.font = None
        
        # État de fondu à l'entrée
        self.fading_in = skip_entry_flash
        self.fade_timer = 0
        self.fade_duration = settings.FLASH_DURATION  # Réutilise la durée du flash
        
        # État de transition de sortie
        self.exiting = False
        self.exit_timer = 0
        self.exit_fade_timer = 0
        self.exit_elements = []  # Éléments à animer lors de la sortie
        
        # Initialise l'animation de pixel (pour les effets)
        self.pixel_animation = PixelAnimation(auto_spawn=False)  # Désactive l'apparition automatique pour la scène de jeu
        
        # Initialise le gestionnaire de curseur
        self.cursor_manager = CursorManager()
        
        # Charge les sons
        self.load_sounds()
        
        # Démarre la musique de fond du jeu
        self.start_background_music()
        
        # Charge les images du bouton de sortie
        try:
            self.exit_normal = pygame.image.load(os.path.join(settings.ASSETS_DIR, "ExitIcon.png"))
            self.exit_click = pygame.image.load(os.path.join(settings.ASSETS_DIR, "ExitIconClick.png"))
            
            # Redimensionne le bouton en utilisant les paramètres
            scale = settings.GAME_EXIT_ICON_SCALE
            orig_size = self.exit_normal.get_size()
            new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
            self.exit_normal = pygame.transform.scale(self.exit_normal, new_size)
            self.exit_click = pygame.transform.scale(self.exit_click, new_size)
            
            # Crée une version survolée avec un effet d'assombrissement
            self.exit_hover = self.exit_normal.copy()
            dark_surface = pygame.Surface(self.exit_hover.get_size(), pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Noir semi-transparent
            self.exit_hover.blit(dark_surface, (0, 0))
            
            # Positionne le bouton en utilisant les paramètres de position absolue
            self.exit_rect = self.exit_normal.get_rect(
                midbottom=(settings.GAME_EXIT_ICON_X_POSITION, settings.GAME_EXIT_ICON_Y_POSITION)
            )
            self.exit_image = self.exit_normal
            self.exit_clicked = False
            self.exit_hovered = False
        except pygame.error as e:
            print(f"Erreur lors du chargement des images du bouton de sortie: {e}")
            self.exit_normal = None
            self.exit_click = None
            self.exit_hover = None
        
        # Charge l'image de bordure du menu principal
        try:
            self.border_img = pygame.image.load(os.path.join(settings.ASSETS_DIR, "fullborder.png"))
            original_border_size = self.border_img.get_size()
            scaled_border_size = (
                int(original_border_size[0] * settings.BORDER_SCALE), 
                int(original_border_size[1] * settings.BORDER_SCALE)
            )
            self.scaled_border_img = pygame.transform.scale(self.border_img, scaled_border_size)
            self.border_rect = self.scaled_border_img.get_rect(
                center=(settings.BORDER_X_POSITION, settings.BORDER_Y_POSITION)
            )
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image de bordure: {e}")
            self.scaled_border_img = None
        
        # Charge l'image de base du cœur
        try:
            self.base_img = pygame.image.load(os.path.join(settings.ASSETS_DIR, "base.png"))
            original_base_size = self.base_img.get_size()
            scaled_base_size = (
                int(original_base_size[0] * settings.HEART_BASE_SCALE), 
                int(original_base_size[1] * settings.HEART_BASE_SCALE)
            )
            self.scaled_base_img = pygame.transform.scale(self.base_img, scaled_base_size)
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image de base: {e}")
            self.scaled_base_img = None
        
        # Charge les images du cœur
        self.heart_images = []
        for i in range(1, 6):  # heart_1.png à heart_5.png - maintenant avec une nomenclature cohérente
            filename = f"heart_{i}.png"
            try:
                image = pygame.image.load(os.path.join(settings.ASSETS_DIR, filename))
                # Redimensionne l'image en utilisant le paramètre HEART_SCALE
                original_size = image.get_size()
                scaled_size = (
                    int(original_size[0] * settings.HEART_SCALE),
                    int(original_size[1] * settings.HEART_SCALE)
                )
                self.heart_images.append(pygame.transform.scale(image, scaled_size))
            except pygame.error as e:
                print(f"Erreur lors du chargement de l'image de cœur {filename}: {e}")
                # Repli sur le cœur précédent si disponible
                if i > 1 and len(self.heart_images) > 0:
                    self.heart_images.append(self.heart_images[-1])
                else:
                    # Crée un cœur de remplacement (redimensionné de manière appropriée)
                    placeholder_size = 100  # Taille de base avant mise à l'échelle
                    placeholder = pygame.Surface((placeholder_size, placeholder_size))
                    placeholder.fill((255, 0, 0))  # Carré rouge comme placeholder
                    scaled_size = (
                        int(placeholder_size * settings.HEART_SCALE),
                        int(placeholder_size * settings.HEART_SCALE)
                    )
                    self.heart_images.append(pygame.transform.scale(placeholder, scaled_size))
            
        # Configure le cœur
        self.lives = settings.INITIAL_LIVES
        self.heart_image = self.heart_images[0]  # Commence avec la première image de cœur
        self.heart_rect = self.heart_image.get_rect(
            center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
        )
        
        # Configure les pixels de jeu
        self.pixels = []
        self.last_spawn_time = 0
        self.spawn_interval = settings.GAME_PIXEL_SPAWN_INTERVAL
        self.pixel_base_speed = settings.GAME_PIXEL_BASE_SPEED
        self.difficulty_timer = 0
        
        # État de la souris
        self.mouse_in_window = True
        
    def load_sounds(self):
        """Charge tous les effets sonores du jeu."""
        # Initialise les objets sonores à None
        self.explode_sound = None
        self.death_sound = None
        self.collect_sound = None
        self.game_over_sound = None
        
        try:
            # Charge le son d'explosion
            explode_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
            if os.path.exists(explode_path):
                self.explode_sound = pygame.mixer.Sound(explode_path)
                self.explode_sound.set_volume(settings.EXPLOSION_VOLUME)
            else:
                print(f"Avertissement: Fichier son '{explode_path}' non trouvé.")
            
            # Charge le son de mort
            death_path = os.path.join(settings.ASSETS_DIR, "death.mp3")
            if os.path.exists(death_path):
                self.death_sound = pygame.mixer.Sound(death_path)
                self.death_sound.set_volume(settings.DEATH_VOLUME)
            else:
                print(f"Avertissement: Fichier son '{death_path}' non trouvé.")
                
            # Charge le son de collecte
            collect_path = os.path.join(settings.ASSETS_DIR, "collect.mp3")
            if os.path.exists(collect_path):
                self.collect_sound = pygame.mixer.Sound(collect_path)
                self.collect_sound.set_volume(settings.COLLECT_VOLUME)
            else:
                print(f"Avertissement: Fichier son '{collect_path}' non trouvé.")
            
            # Charge le son de game-over
            game_over_path = os.path.join(settings.ASSETS_DIR, "game-over.mp3")
            if os.path.exists(game_over_path):
                self.game_over_sound = pygame.mixer.Sound(game_over_path)
                self.game_over_sound.set_volume(settings.GAME_OVER_VOLUME)  # Utilise le volume dédié au game over
            else:
                print(f"Avertissement: Fichier son '{game_over_path}' non trouvé.")
                
        except pygame.error as e:
            print(f"Erreur lors du chargement des effets sonores: {e}")
    
    def start_background_music(self):
        """Démarre la musique de fond pour le jeu."""
        # Ne joue la musique que si elle est activée
        if self.music_enabled:
            try:
                # Arrête toute musique existante
                pygame.mixer.music.stop()
                
                # Charge et joue la musique de fond du jeu
                bg_music_path = os.path.join(settings.ASSETS_DIR, "game-song.mp3")
                if os.path.exists(bg_music_path):
                    pygame.mixer.music.load(bg_music_path)
                    pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)  # Utilise la valeur du paramètre
                    pygame.mixer.music.play(-1)  # -1 signifie boucler indéfiniment
                else:
                    print(f"Avertissement: Fichier de musique de fond du jeu '{bg_music_path}' non trouvé.")
            except pygame.error as e:
                print(f"Erreur lors du chargement de la musique de fond du jeu: {e}")
    
    def spawn_pixel(self):
        """Fait apparaître un nouveau pixel au bord de l'écran mais à l'intérieur de la bordure."""
        # Calcule les limites de la bordure
        if hasattr(self, 'border_rect') and self.border_rect:
            border_left = self.border_rect.left + 20  # Ajoute un rembourrage
            border_right = self.border_rect.right - 20
            border_top = self.border_rect.top + 20
            border_bottom = self.border_rect.bottom - 20
        else:
            # Repli sur les limites de l'écran avec rembourrage
            border_left = 20
            border_right = settings.SCREEN_WIDTH - 20
            border_top = 20
            border_bottom = settings.SCREEN_HEIGHT - 20
        
        # Choisit aléatoirement de quel côté apparaître (0=haut, 1=droite, 2=bas, 3=gauche)
        side = random.randint(0, 3)
        
        # Calcule la position en fonction du côté choisi mais à l'intérieur de la bordure
        if side == 0:  # Haut
            x = random.randint(border_left, border_right)
            y = border_top
            angle = math.pi / 2  # Vers le bas
        elif side == 1:  # Droite
            x = border_right
            y = random.randint(border_top, border_bottom)
            angle = math.pi  # Vers la gauche
        elif side == 2:  # Bas
            x = random.randint(border_left, border_right)
            y = border_bottom
            angle = 3 * math.pi / 2  # Vers le haut
        else:  # Gauche
            x = border_left
            y = random.randint(border_top, border_bottom)
            angle = 0  # Vers la droite
            
        # Détermine aléatoirement le type de pixel en fonction des probabilités d'apparition
        roll = random.randint(1, 100)
        if roll <= settings.RED_PIXEL_ODDS:
            pixel_type = "red"
        elif roll <= settings.RED_PIXEL_ODDS + settings.GREEN_PIXEL_ODDS:
            pixel_type = "green"
        elif roll <= settings.RED_PIXEL_ODDS + settings.GREEN_PIXEL_ODDS + settings.ORANGE_PIXEL_ODDS:
            pixel_type = "orange"
        else:
            pixel_type = "white"
            
        # Détermine aléatoirement la taille du pixel
        size = random.randint(settings.GAME_PIXEL_MIN_SIZE, settings.GAME_PIXEL_MAX_SIZE)
        
        # Crée et ajoute le pixel
        pixel = GamePixel(x, y, angle, size, pixel_type)
        pixel.speed = self.pixel_base_speed  # Définit la vitesse de base actuelle
        self.pixels.append(pixel)
        
    def spawn_orange_splash(self, x, y):
        """
        Fait apparaître exactement deux pixels blancs s'éloignant du cœur lorsqu'un pixel orange est cliqué.
        
        Args:
            x (float): Position X du pixel orange
            y (float): Position Y du pixel orange
        """
        heart_x = settings.HEART_X_POSITION
        heart_y = settings.HEART_Y_POSITION
        
        # Calcule le vecteur de direction du cœur vers le pixel orange
        dx = x - heart_x
        dy = y - heart_y
        
        # Obtient la distance du cœur au pixel orange
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Ne procède que si nous avons une direction valide (pas au cœur)
        if distance > 0:
            # Normalise le vecteur de direction
            dx /= distance
            dy /= distance
            
            # Fait toujours apparaître exactement 2 pixels blancs
            for i in range(2):
                # Varie légèrement l'angle pour chaque pixel
                if i == 0:
                    angle_offset = random.uniform(-math.pi/6, 0)  # -30 à 0 degrés
                else:
                    angle_offset = random.uniform(0, math.pi/6)  # 0 à 30 degrés
                    
                angle = math.atan2(dy, dx) + angle_offset
                dir_x = math.cos(angle)
                dir_y = math.sin(angle)
                
                # Calcule la position d'apparition plus loin du cœur que le pixel orange
                additional_distance = settings.ORANGE_SPLASH_RADIUS * 1.5  # S'assure qu'ils sont loin
                spawn_x = x + dir_x * additional_distance
                spawn_y = y + dir_y * additional_distance
                
                # Limite aux limites de l'écran tout en s'assurant qu'ils sont à l'intérieur de la bordure
                if hasattr(self, 'border_rect') and self.border_rect:
                    border_left = self.border_rect.left + 20
                    border_right = self.border_rect.right - 20
                    border_top = self.border_rect.top + 20
                    border_bottom = self.border_rect.bottom - 20
                else:
                    border_left = 20
                    border_right = settings.SCREEN_WIDTH - 20
                    border_top = 20
                    border_bottom = settings.SCREEN_HEIGHT - 20
                    
                spawn_x = max(border_left, min(spawn_x, border_right))
                spawn_y = max(border_top, min(spawn_y, border_bottom))
                
                # Taille aléatoire
                size = random.randint(settings.GAME_PIXEL_MIN_SIZE, settings.GAME_PIXEL_MAX_SIZE)
                
                # Crée et ajoute un pixel blanc (pas orange)
                pixel = GamePixel(spawn_x, spawn_y, angle, size, "white")
                
                # Rend ces pixels blancs légèrement plus lents que la normale pour donner au joueur le temps de réagir
                pixel.speed = self.pixel_base_speed * 0.6
                self.pixels.append(pixel)
    
    def lose_life(self):
        """Réduit les vies du joueur de 1 et met à jour l'image du cœur."""
        self.lives -= 1
        
        # Joue le son de mort lors de la perte d'une vie
        self.play_sound(self.death_sound)
        
        # Crée une animation de pixels rouges sur le cœur lors de la perte d'une vie
        for _ in range(15):  # Crée 15 particules
            # Positions aléatoires autour du centre du cœur
            particle_x = settings.HEART_X_POSITION + random.uniform(-20, 20)
            particle_y = settings.HEART_Y_POSITION + random.uniform(-20, 20)
            self.pixel_animation.spawn_particles(particle_x, particle_y, color="red")
        
        # Vérifie la fin de partie
        if self.lives <= 0:
            self.lives = 0
            print("Game Over!")
            # Commence la transition de fin de jeu
            self.trigger_game_over(from_red_pixel=False)
            
        # Met à jour l'image du cœur (heart_1.png à heart_5.png en fonction des dégâts)
        damage_level = 5 - self.lives
        if damage_level >= 0 and damage_level < 5:
            self.heart_image = self.heart_images[damage_level]
        # Quand toutes les vies sont perdues, s'assure d'afficher le cœur le plus endommagé
        elif damage_level >= 5:
            self.heart_image = self.heart_images[4]  # Dernière image de cœur (la plus endommagée)
    
    def apply_powerup(self):
        """Applique un effet de power-up aléatoire."""
        # Pour l'instant, implémente simplement un powerup qui supprime quelques pixels
        powerup_type = random.choice(["clear_pixels", "slow_pixels", "extra_life"])
        
        if powerup_type == "clear_pixels":
            # Supprime la moitié des pixels blancs
            white_pixels = [p for p in self.pixels if p.type == "white"]
            if white_pixels:
                for _ in range(len(white_pixels) // 2):
                    pixel = random.choice(white_pixels)
                    if pixel in self.pixels:
                        pixel.mark_as_dead()
                        white_pixels.remove(pixel)
                        
        elif powerup_type == "slow_pixels":
            # Ralentit tous les pixels temporairement
            for pixel in self.pixels:
                pixel.speed *= 0.5
                
        elif powerup_type == "extra_life":
            # Ajoute une vie supplémentaire si pas au maximum
            if self.lives < 5:
                self.lives += 1
                damage_level = 5 - self.lives
                self.heart_image = self.heart_images[damage_level - 1]
    
    def trigger_game_over(self, from_red_pixel=False):
        """
        Déclenche la séquence de fin de jeu avec animation de transition vers le menu.
        
        Args:
            from_red_pixel (bool): Si la fin de jeu a été déclenchée en cliquant sur un pixel rouge
        """
        # Joue le son de game over
        self.play_sound(self.game_over_sound)
            
        # Crée des effets de particules à la position du cœur
        # Utilise plus de particules si déclenché par un pixel rouge pour un effet plus dramatique
        particle_count = 40 if from_red_pixel else 30
        particle_spread = 40 if from_red_pixel else 30
        
        for _ in range(particle_count):
            particle_x = settings.HEART_X_POSITION + random.uniform(-particle_spread, particle_spread)
            particle_y = settings.HEART_Y_POSITION + random.uniform(-particle_spread, particle_spread)
            self.pixel_animation.spawn_particles(particle_x, particle_y, color="red")
            
        # Commence la transition de sortie après un court délai pour laisser le joueur voir l'état de fin de jeu
        pygame.time.set_timer(pygame.USEREVENT, 1500)  # Délai de 1,5 seconde
        self.game_over_pending = True
    
    def add_score(self, points):
        """
        Ajoute des points au score actuel.
        
        Args:
            points (int): Nombre de points à ajouter
        """
        self.score += points
        # Vérifie si on a battu le meilleur score
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)
    
    def handle_events(self):
        """Gère les événements du jeu."""
        # Si dans l'état de sortie, ne traite aucun événement
        if self.exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
            return True
        
        # Gestion normale des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            # Vérifie la transition de fin de jeu différée
            elif event.type == pygame.USEREVENT:
                if hasattr(self, 'game_over_pending') and self.game_over_pending:
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # Annule le minuteur
                    self.game_over_pending = False
                    # Sauvegarde le high score avant de quitter
                    if self.score > self.highscore:
                        self.highscore = self.score
                        save_highscore(self.highscore)
                    self.start_exit_transition()
                
            elif event.type == pygame.MOUSEMOTION:
                # Vérifie si la souris est à l'intérieur de la fenêtre
                x, y = event.pos
                self.mouse_in_window = (0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT)
                
                # Vérifie si la souris survole le bouton de sortie
                if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                    self.exit_hovered = True
                    if not self.exit_clicked:
                        self.exit_image = self.exit_hover
                else:
                    self.exit_hovered = False
                    if not self.exit_clicked:
                        self.exit_image = self.exit_normal
            
            elif event.type == pygame.ACTIVEEVENT:
                # Gère les événements de focus/perte de focus de la fenêtre
                if event.gain == 0 and event.state == 1:  # La souris a quitté la fenêtre
                    self.mouse_in_window = False
                elif event.gain == 1 and event.state == 1:  # La souris est entrée dans la fenêtre
                    self.mouse_in_window = True
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Bouton gauche de la souris
                    # Vérifie si nous avons cliqué sur un élément interactif
                    clicked_on_interactive = False
                    clicked_pixel = None  # Initialise clicked_pixel pour éviter UnboundLocalError
                    
                    # Vérifie si le bouton de sortie a été cliqué
                    if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                        clicked_on_interactive = True
                        self.exit_clicked = True
                        self.exit_image = self.exit_click
                        # Ne retourne pas immédiatement, laisse le clic du bouton être visible
                    else:
                        # Vérifie les clics sur les pixels
                        for pixel in self.pixels:
                            if pixel.check_click(event.pos):
                                clicked_pixel = pixel
                                clicked_on_interactive = True
                                break
                                
                        if clicked_pixel:
                            # Joue le son d'explosion pour les clics de pixel
                            if hasattr(self, 'explode_sound') and self.explode_sound:
                                self.play_sound(self.explode_sound)
                                
                            if clicked_pixel.type == "white":
                                # Pixel blanc : détruit et crée une animation
                                clicked_pixel.mark_as_dead()
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="white")
                                # Ajoute 1 point pour un pixel blanc détruit
                                self.add_score(settings.WHITE_PIXEL_POINTS)
                                
                            elif clicked_pixel.type == "red":
                                # Pixel rouge : fin de jeu
                                print("Pixel rouge cliqué! Game Over!")
                                self.lives = 0  # Met les vies à 0
                                self.heart_image = self.heart_images[4]  # Cœur le plus endommagé
                                # Crée un effet d'explosion rouge plus grand
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="red", count=20)
                                # Supprime le pixel cliqué
                                clicked_pixel.mark_as_dead()
                                # Ajoute des points pour avoir cliqué sur un pixel rouge
                                self.add_score(settings.RED_PIXEL_BASE_POINTS)
                                # Déclenche la séquence de fin de jeu
                                self.trigger_game_over(from_red_pixel=True)
                                
                            elif clicked_pixel.type == "green":
                                # Pixel vert : power-up et fait éclater tous les pixels blancs et orange
                                clicked_pixel.mark_as_dead()
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="green")
                                
                                # Joue le son de collecte pour le pixel vert
                                if hasattr(self, 'collect_sound') and self.collect_sound:
                                    self.play_sound(self.collect_sound)
                                
                                self.apply_powerup()
                                
                                # Fait éclater tous les pixels blancs et orange
                                for other_pixel in list(self.pixels):  # Crée une copie de la liste pour itérer en toute sécurité
                                    if other_pixel.type in ["white", "orange"] and other_pixel != clicked_pixel:
                                        self.pixel_animation.spawn_particles(other_pixel.x, other_pixel.y, color=other_pixel.type)
                                        other_pixel.mark_as_dead()
                                        # Ajoute des points pour chaque pixel détruit
                                        if other_pixel.type == "white":
                                            self.add_score(settings.WHITE_PIXEL_POINTS)
                                        elif other_pixel.type == "orange":
                                            self.add_score(settings.ORANGE_PIXEL_POINTS)
                            
                            elif clicked_pixel.type == "orange":
                                # Pixel orange : détruit et fait apparaître des pixels blancs dans la direction opposée au cœur
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="orange")
                                self.spawn_orange_splash(clicked_pixel.x, clicked_pixel.y)
                                clicked_pixel.mark_as_dead()
                                # Ajoute 3 points pour un pixel orange détruit
                                self.add_score(settings.ORANGE_PIXEL_POINTS)
                    
                    # Si cliqué sur un élément interactif comme un bouton ou un pixel, joue le son d'explosion
                    if clicked_on_interactive and not clicked_pixel and hasattr(self, 'explode_sound') and self.explode_sound:
                        self.play_sound(self.explode_sound)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement du bouton gauche de la souris
                    # Vérifie si le bouton de sortie a été cliqué et relâché
                    if self.exit_clicked:
                        self.exit_clicked = False
                        if self.exit_hovered:
                            self.exit_image = self.exit_hover
                        else:
                            self.exit_image = self.exit_normal
                        
                        # Vérifie si la souris est toujours sur le bouton
                        if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                            print("Retour au menu principal")
                            # Sauvegarde le high score avant de quitter
                            if self.score > self.highscore:
                                self.highscore = self.score
                                save_highscore(self.highscore)
                            self.start_exit_transition()
        
        return True
    
    def start_exit_transition(self):
        """Démarre l'animation de transition lors de la sortie vers le menu."""
        self.exiting = True
        self.exit_timer = 0
        self.exit_fade_timer = 0
        
        # Arrêter complètement la musique du jeu au lieu de simplement la faire disparaître
        try:
            # Utiliser fadeout pour une transition douce, mais s'assurer que la musique est arrêtée
            pygame.mixer.music.fadeout(500)  # Fondu sortant sur 500ms
            # Ajout d'un arrêt complet après le fadeout pour être sûr
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Erreur lors du fondu sortant de la musique du jeu: {e}")
        
        # Collecte tous les éléments visibles pour la transition
        self.exit_elements = []
        
        # Ajoute la base (si elle existe)
        if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
            base_rect = self.scaled_base_img.get_rect(
                center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
            )
            self.exit_elements.append((self.scaled_base_img, base_rect))
        
        # Ajoute le cœur
        if hasattr(self, 'heart_image') and self.heart_image:
            self.exit_elements.append((self.heart_image, self.heart_rect))
        
        # Ajoute le bouton de sortie
        if hasattr(self, 'exit_image') and self.exit_image:
            self.exit_elements.append((self.exit_image, self.exit_rect))
        
        # Ajoute les pixels comme éléments
        for pixel in self.pixels:
            if hasattr(pixel, 'image') and pixel.image and hasattr(pixel, 'rect') and pixel.rect:
                self.exit_elements.append((pixel.image, pixel.rect))
        
        # Crée TransitionAnimation pour la sortie
        self.exit_transition = TransitionAnimation()
        self.exit_transition.start(self.exit_elements)
    
    def update(self, dt):
        """
        Met à jour l'état du jeu.
        
        Args:
            dt (float): Delta temps en secondes
        """
        # Gère la transition de sortie
        if self.exiting:
            self.exit_timer += dt
            
            # Première phase : les éléments tombent hors de l'écran
            if self.exit_timer < settings.TRANSITION_DURATION:
                # Met à jour l'animation de transition
                still_active = self.exit_transition.update(dt)
                
                # Si la transition est terminée, commence immédiatement le flash blanc
                if not still_active and self.exit_transition.all_elements_exited_screen():
                    # Passe à la phase de flash
                    self.exit_timer = settings.TRANSITION_DURATION
                    self.exit_fade_timer = 0
                
                # Met à jour le curseur
                mouse_pos = pygame.mouse.get_pos()
                self.cursor_manager.update(
                    mouse_pos, 
                    pygame.mouse.get_pressed(), 
                    hovering_button=False,
                    hovering_title=False,
                    mouse_in_window=self.mouse_in_window,
                    game_mode=True
                )
                
            # Deuxième phase : flash blanc
            elif self.exit_timer >= settings.TRANSITION_DURATION and self.exit_fade_timer < settings.FLASH_DURATION:
                self.exit_fade_timer += dt
                
                # Retourne au menu immédiatement lorsque le flash commence
                if self.exit_fade_timer < 0.05:  # Vient de commencer le flash
                    # S'assure que toute la musique est arrêtée avant de retourner au menu
                    try:
                        pygame.mixer.music.stop()
                    except pygame.error:
                        pass
                    self.return_to_menu = True
                    self.running = False
                
            return
        
        # Gère l'effet de fondu à l'entrée
        if self.fading_in:
            self.fade_timer += dt
            if self.fade_timer >= self.fade_duration:
                self.fading_in = False
        
        # Met à jour le curseur de la souris
        mouse_pos = pygame.mouse.get_pos()
        self.cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(mouse_pos),
            hovering_title=False,
            mouse_in_window=self.mouse_in_window,
            game_mode=True
        )
        
        # Ne met pas à jour l'état du jeu pendant le fondu à l'entrée
        if self.fading_in:
            # Met à jour uniquement les animations pendant le fondu à l'entrée
            self.pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            return
        
        # Met à jour l'animation des pixels
        self.pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Augmente la difficulté au fil du temps
        self.difficulty_timer += dt
        self.spawn_interval = max(
            settings.GAME_PIXEL_SPAWN_INTERVAL - (self.difficulty_timer * settings.GAME_PIXEL_SPAWN_DECREASE_RATE),
            settings.GAME_PIXEL_SPAWN_MIN_INTERVAL
        )
        self.pixel_base_speed = settings.GAME_PIXEL_BASE_SPEED + (self.difficulty_timer * settings.GAME_PIXEL_SPEED_INCREASE_RATE)
        
        # Vérifie si nous devons faire apparaître un nouveau pixel
        self.last_spawn_time += dt
        if self.last_spawn_time >= self.spawn_interval:
            self.spawn_pixel()
            self.last_spawn_time = 0
            
        # Met à jour tous les pixels
        heart_x = settings.HEART_X_POSITION
        heart_y = settings.HEART_Y_POSITION
        
        pixels_to_remove = []
        for i, pixel in enumerate(self.pixels):
            if not pixel.update(dt, heart_x, heart_y):
                pixels_to_remove.append(i)
                continue
                
            # Définit le rectangle de base pour la détection de collision
            if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
                base_rect = self.scaled_base_img.get_rect(
                    center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
                )
                collision_rect = base_rect
            else:
                collision_rect = self.heart_rect
            
            # Vérifie la collision avec le cœur/la base
            if pixel.check_collision(collision_rect) and not pixel.is_blinking:
                # Commence l'effet de clignotement au lieu de supprimer immédiatement
                if pixel.type == "green":
                    # Les pixels verts doivent éclater immédiatement sans son ni clignotement
                    self.apply_powerup()
                    pixels_to_remove.append(i)
                    # Crée un effet de particules sans son
                    self.pixel_animation.spawn_particles(pixel.x, pixel.y, color="green")
                else:
                    pixel.start_blinking()
                    
                    if pixel.type == "white" or pixel.type == "orange":
                        # Marque le pixel comme un pixel qui endommagera le cœur lorsqu'il aura fini de clignoter
                        pixel.will_damage_heart = True
                    elif pixel.type == "red":
                        # Les pixels rouges donnent des points quand ils touchent la base
                        # Mais ne causent pas de dégâts au cœur
                        self.add_score(settings.RED_PIXEL_BASE_POINTS)
            
        # Supprime les pixels morts (dans l'ordre inverse pour maintenir les indices corrects)
        for i in sorted(pixels_to_remove, reverse=True):
            if i < len(self.pixels):
                # Obtient le pixel avant de le supprimer
                pixel = self.pixels[i]
                
                # Vérifie si ce pixel clignote et vient de terminer son animation
                if pixel.is_blinking:
                    # Crée un effet de particules pour l'explosion
                    self.pixel_animation.spawn_particles(pixel.x, pixel.y, color=pixel.type)
                    
                    # Joue le son d'explosion pour l'éclatement du pixel
                    if hasattr(self, 'explode_sound') and self.explode_sound:
                        self.play_sound(self.explode_sound)
                    
                    # Applique les effets en fonction du type de pixel
                    if pixel.will_damage_heart:
                        # C'est maintenant que nous perdons une vie et montrons l'animation rouge
                        self.lose_life()
                    elif pixel.will_apply_powerup:
                        # Applique le powerup lorsque le pixel vert finit de clignoter
                        self.apply_powerup()
                        # Joue le son de collecte
                        if hasattr(self, 'collect_sound') and self.collect_sound:
                            self.play_sound(self.collect_sound)
                
                # Maintenant supprime le pixel
                del self.pixels[i]
    
    def draw(self):
        """Dessine l'état du jeu."""
        # Efface l'écran
        self.screen.fill(settings.BLACK)
        
        # Dessine toujours d'abord la bordure comme arrière-plan
        if hasattr(self, 'scaled_border_img') and self.scaled_border_img is not None:
            self.screen.blit(self.scaled_border_img, self.border_rect)
        
        if self.exiting:
            # Pendant la transition de sortie, première phase : éléments en chute
            if self.exit_timer < settings.TRANSITION_DURATION:
                # Dessine les éléments de transition
                self.exit_transition.draw(self.screen)
                
                # Dessine le curseur
                self.cursor_manager.draw(self.screen)
                
            # Deuxième phase : flash blanc
            elif self.exit_timer >= settings.TRANSITION_DURATION:
                # Calcule l'alpha du flash
                flash_progress = min(self.exit_fade_timer / settings.FLASH_DURATION, 1.0)
                alpha = int(255 * (1.0 - flash_progress))  # Commence à 255, diminue jusqu'à 0
                
                # Dessine le calque de flash blanc
                flash_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, alpha))
                self.screen.blit(flash_surface, (0, 0))
                
            # Met à jour l'affichage
            pygame.display.flip()
            return
        
        # Rendu normal du jeu
        # Dessine tous les éléments du jeu - ils seront visibles à travers le flash blanc
        # Dessine tous les pixels
        for pixel in self.pixels:
            pixel.draw(self.screen)
        
        # Dessine d'abord l'image de base sous le cœur
        if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
            base_rect = self.scaled_base_img.get_rect(
                center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
            )
            self.screen.blit(self.scaled_base_img, base_rect)
        
        # Dessine ensuite le cœur au-dessus de la base
        self.screen.blit(self.heart_image, self.heart_rect)
        
        # Dessine le bouton de sortie
        if hasattr(self, 'exit_image') and self.exit_image is not None:
            self.screen.blit(self.exit_image, self.exit_rect)
        
        # Dessine le score
        if self.font:
            score_text = self.font.render(f"{settings.SCORE_PREFIX}{self.score}", True, settings.SCORE_TEXT_COLOR)
            score_rect = score_text.get_rect(midtop=(settings.SCORE_X_POSITION, settings.SCORE_Y_POSITION))
            self.screen.blit(score_text, score_rect)
        
        # Dessine les effets d'animation de pixels
        self.pixel_animation.draw(self.screen)
        
        # Dessine le curseur
        self.cursor_manager.draw(self.screen)
        
        # Dessine l'effet de fondu à l'entrée
        if self.fading_in:
            fade_progress = 1.0 - min(self.fade_timer / self.fade_duration, 1.0)
            alpha = int(255 * fade_progress)
            fade_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((255, 255, 255, alpha))
            self.screen.blit(fade_surface, (0, 0))
        
        # Met à jour l'affichage
        pygame.display.flip()
    
    def run(self):
        """Exécute la boucle du jeu."""
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            # Calcule le delta temps
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # Gère les événements
            if not self.handle_events():
                break
                
            # Met à jour l'état du jeu
            self.update(dt)
            
            # Dessine
            self.draw()
            
            # Limite le taux de rafraîchissement
            clock.tick(settings.FPS)
            
        return self.running

    def play_sound(self, sound):
        """
        Joue un effet sonore si les effets sonores sont activés.
        
        Args:
            sound: L'objet Son pygame à jouer
        """
        if self.sound_effects_enabled:
            sound.play()

def start(screen, skip_entry_flash=False, music_enabled=True, sound_effects_enabled=True):
    """
    Démarre le jeu.
    
    Args:
        screen (Surface): Surface Pygame sur laquelle dessiner
        skip_entry_flash (bool): Si True, ignore l'effet de fondu initial
        music_enabled (bool): Si False, désactive la musique
        sound_effects_enabled (bool): Si False, désactive les effets sonores
        
    Returns:
        bool: True si le jeu doit retourner au menu, False s'il doit quitter
    """
    # Crée toujours une nouvelle instance de Game pour garantir des paramètres frais
    game = Game(screen, skip_entry_flash, music_enabled, sound_effects_enabled)
    result = game.run()
    
    # Si le jeu s'est terminé en raison du drapeau return_to_menu flag, renvoie toujours True
    # Cela garantit que nous retournons au menu principal plutôt que de quitter
    if game.return_to_menu:
        return True
        
    return result 