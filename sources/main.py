import pygame
import sys
import os
import math
import settings  # Importe les paramètres
from cursor_manager import CursorManager
from pixel_animation import PixelAnimation  # Importe notre système d'animation
from transition import TransitionAnimation  # Importe notre nouveau système d'animation de transition
from screen_flash import ScreenFlash  # Importe notre système d'animation de flash d'écran
import game  # Importe notre module de jeu

# Classe de bouton à bascule
class ToggleButton:
    """Classe de bouton à bascule pour les options marche/arrêt."""
    def __init__(self, x, y, on_img, off_img, initial_state=True, scale=1.0, shadow_offset=3, shadow_alpha=128):
        """
        Initialise un bouton à bascule.
        
        Args:
            x (int): Coordonnée X du centre du bouton
            y (int): Coordonnée Y du centre du bouton
            on_img (Surface): Image pour l'état activé
            off_img (Surface): Image pour l'état désactivé
            initial_state (bool): État initial du bouton (True = activé, False = désactivé)
            scale (float): Facteur d'échelle pour la taille du bouton (par défaut: 1.0)
            shadow_offset (int): Décalage de l'ombre en pixels
            shadow_alpha (int): Transparence de l'ombre (0-255)
        """
        # Redimensionne les images si nécessaire
        if scale != 1.0:
            orig_size = on_img.get_size()
            new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
            self.on_img = pygame.transform.scale(on_img, new_size)
            self.off_img = pygame.transform.scale(off_img, new_size)
        else:
            self.on_img = on_img
            self.off_img = off_img
            
        # Crée une version assombrie des images pour l'état de survol
        self.hover_on_img = self.on_img.copy()
        dark_surface = pygame.Surface(self.hover_on_img.get_size(), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Noir semi-transparent
        self.hover_on_img.blit(dark_surface, (0, 0))
        
        self.hover_off_img = self.off_img.copy()
        dark_surface = pygame.Surface(self.hover_off_img.get_size(), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Noir semi-transparent
        self.hover_off_img.blit(dark_surface, (0, 0))
        
        self.state = initial_state
        self.x = x
        self.y = y
        self.image = self.on_img if self.state else self.off_img
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        self.hovered = False
        self.shadow_offset = shadow_offset
        self.shadow_alpha = shadow_alpha
        
    def draw(self, surface):
        """
        Dessine le bouton à bascule sur la surface donnée.
        
        Args:
            surface (Surface): Surface sur laquelle dessiner le bouton
        """
        # Crée une ombre pour le bouton
        shadow_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, self.shadow_alpha))
        shadow_rect = shadow_surface.get_rect(
            center=(self.rect.centerx + self.shadow_offset, 
                    self.rect.centery + self.shadow_offset)
        )
        
        # Dessine l'ombre d'abord
        surface.blit(shadow_surface, shadow_rect)
        
        # Puis dessine le bouton
        if self.hovered:
            if self.state:
                surface.blit(self.hover_on_img, self.rect)
            else:
                surface.blit(self.hover_off_img, self.rect)
        else:
            if self.state:
                surface.blit(self.on_img, self.rect)
            else:
                surface.blit(self.off_img, self.rect)
    
    def check_click(self, pos):
        """
        Vérifie si le bouton est cliqué et bascule son état.
        
        Args:
            pos (tuple): Position (x, y) du clic de souris
            
        Returns:
            bool: True si le bouton est cliqué, False sinon
        """
        if self.rect.collidepoint(pos):
            self.clicked = True
            # Bascule l'état du bouton
            self.state = not self.state
            # Met à jour l'image en fonction du nouvel état
            self.image = self.on_img if self.state else self.off_img
            self.rect = self.image.get_rect(center=(self.x, self.y))
            return True
        return False
    
    def check_hover(self, pos):
        """
        Vérifie si la souris survole le bouton.
        
        Args:
            pos (tuple): Position (x, y) du curseur de la souris
            
        Returns:
            bool: True si le bouton est survolé, False sinon
        """
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)
        
        # Retourne True uniquement si l'état de survol a changé
        return was_hovered != self.hovered
    
    def get_state(self):
        """
        Retourne l'état actuel du bouton.
        
        Returns:
            bool: True si activé, False si désactivé
        """
        return self.state

# Fonction pour charger le meilleur score
def load_highscore():
    """
    Charge le meilleur score à partir du fichier.
    
    Returns:
        int: Le meilleur score enregistré, 0 si aucun score n'existe
    """
    # Vérifie si le dossier highscore existe
    if not os.path.exists(settings.HIGHSCORE_DIR):
        return 0

    highscore_path = os.path.join(settings.HIGHSCORE_DIR, settings.HIGHSCORE_FILE)
    try:
        if os.path.exists(highscore_path):
            with open(highscore_path, 'r') as f:
                return int(f.read().strip())
    except (IOError, ValueError) as e:
        print(f"Erreur lors du chargement du meilleur score: {e}")
    
    return 0

# Initialise pygame
pygame.init()
pygame.mixer.init()  # Initialise le mixer pour la lecture audio

# Crée l'écran en fonction des paramètres
if settings.BORDERLESS_WINDOW:
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.NOFRAME  # Supprime le cadre/bordure de la fenêtre, y compris la barre de titre
    )
else:
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    
pygame.display.set_caption("Pixel Perfect")  # Définit la légende pour la barre des tâches

# Charge les ressources
def load_image(filename):
    filepath = os.path.join(settings.ASSETS_DIR, filename)
    try:
        if not os.path.exists(filepath):
            print(f"Erreur : Fichier image '{filepath}' introuvable.")
            print(f"Veuillez vous assurer que '{filename}' est dans le dossier '{settings.ASSETS_DIR}'.")
            sys.exit()
        
        image = pygame.image.load(filepath)
        return image
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image {filepath}: {e}")
        sys.exit()

# Charge toutes les images requises
title_img = load_image("title.png")
play_btn = load_image("PlayBtn.png")
play_click = load_image("PlayClick.png")
opt_btn = load_image("OptBtn.png")
opt_click = load_image("OptClick.png")
exit_btn = load_image("ExitBtn.png")
exit_click = load_image("ExitClick.png")
border_img = load_image("fullborder.png")
name_img = load_image("name.png")  # Charge l'image du nom
crown_img = load_image("Crown.gif")  # Charge l'image de la couronne

# Classe de bouton
class Button:
    """Classe de bouton pour les boutons interactifs."""
    def __init__(self, x, y, normal_img, clicked_img, scale=1.0):
        """
        Initialise un bouton.
        
        Args:
            x (int): Coordonnée X du centre du bouton
            y (int): Coordonnée Y du centre du bouton
            normal_img (Surface): Image pour l'état normal
            clicked_img (Surface): Image pour l'état cliqué
            scale (float): Facteur d'échelle pour la taille du bouton (par défaut: 1.0)
        """
        # Redimensionne les images si nécessaire
        if scale != 1.0:
            orig_size = normal_img.get_size()
            new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
            self.normal_img = pygame.transform.scale(normal_img, new_size)
            self.clicked_img = pygame.transform.scale(clicked_img, new_size)
        else:
            self.normal_img = normal_img
            self.clicked_img = clicked_img
            
        # Crée une version assombrie de l'image normale pour l'état de survol
        self.hover_img = self.normal_img.copy()
        dark_surface = pygame.Surface(self.hover_img.get_size(), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Noir semi-transparent
        self.hover_img.blit(dark_surface, (0, 0))
        
        self.image = self.normal_img
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        self.hovered = False
        
    def draw(self, surface):
        """
        Dessine le bouton sur la surface donnée.
        
        Args:
            surface (Surface): Surface sur laquelle dessiner le bouton
        """
        surface.blit(self.image, self.rect)
        
    def check_click(self, pos):
        """
        Vérifie si le bouton est cliqué.
        
        Args:
            pos (tuple): Position de la souris (x, y)
            
        Returns:
            bool: True si le bouton est cliqué, False sinon
        """
        if self.rect.collidepoint(pos):
            self.clicked = True
            self.image = self.clicked_img
            return True
        return False
    
    def check_hover(self, pos):
        """
        Vérifie si le bouton est survolé.
        
        Args:
            pos (tuple): Position de la souris (x, y)
        """
        if self.rect.collidepoint(pos):
            self.hovered = True
            if not self.clicked:  # Affiche l'effet de survol uniquement si non cliqué
                self.image = self.hover_img
        else:
            self.hovered = False
            if not self.clicked:  # Réinitialise à la normale uniquement si non cliqué
                self.image = self.normal_img
    
    def release(self):
        """Relâche le bouton lorsque le bouton de la souris est relâché."""
        if self.clicked:
            self.clicked = False
            if self.hovered:
                self.image = self.hover_img
            else:
                self.image = self.normal_img

# Crée des boutons en utilisant les paramètres - toutes les positions sont maintenant absolues depuis l'origine (0,0)
play_button = Button(
    settings.PLAY_BUTTON_X_POSITION, 
    settings.PLAY_BUTTON_Y_POSITION, 
    play_btn, 
    play_click, 
    scale=settings.PLAY_BUTTON_SCALE
)

# Bouton d'options avec positionnement absolu
options_button = Button(
    settings.OPTIONS_BUTTON_X_POSITION, 
    settings.OPTIONS_BUTTON_Y_POSITION, 
    opt_btn, 
    opt_click, 
    scale=settings.OPTIONS_BUTTON_SCALE
)

# Bouton de sortie avec positionnement absolu
exit_button = Button(
    settings.EXIT_BUTTON_X_POSITION, 
    settings.EXIT_BUTTON_Y_POSITION, 
    exit_btn, 
    exit_click, 
    scale=settings.EXIT_BUTTON_SCALE
)

# Mise à l'échelle et positionnement de la bordure en utilisant les paramètres
original_border_size = border_img.get_size()
scaled_border_size = (
    int(original_border_size[0] * settings.BORDER_SCALE), 
    int(original_border_size[1] * settings.BORDER_SCALE)
)
scaled_border_img = pygame.transform.scale(border_img, scaled_border_size)
border_rect = scaled_border_img.get_rect(
    center=(settings.BORDER_X_POSITION, settings.BORDER_Y_POSITION)
)

# Mise à l'échelle et positionnement de l'image du nom en utilisant les paramètres
original_name_size = name_img.get_size()
scaled_name_size = (
    int(original_name_size[0] * settings.NAME_SCALE), 
    int(original_name_size[1] * settings.NAME_SCALE)
)
scaled_name_img = pygame.transform.scale(name_img, scaled_name_size)
name_rect = scaled_name_img.get_rect(
    midbottom=(settings.NAME_X_POSITION, settings.NAME_Y_POSITION)
)

# Mise à l'échelle de l'image de la couronne
original_crown_size = crown_img.get_size()
scaled_crown_size = (
    int(original_crown_size[0] * settings.CROWN_SCALE),
    int(original_crown_size[1] * settings.CROWN_SCALE)
)
scaled_crown_img = pygame.transform.scale(crown_img, scaled_crown_size)

# Variables globales pour les paramètres audio
music_enabled = True
sound_effects_enabled = True

def load_menu_music():
    """Load and play the menu background music."""
    global music_enabled
    
    # Don't load music if it's disabled
    if not music_enabled:
        pygame.mixer.music.stop()
        return
        
    try:
        # Load and play background music
        bg_music_path = os.path.join(settings.ASSETS_DIR, "pixel-song.mp3")
        if os.path.exists(bg_music_path):
            pygame.mixer.music.load(bg_music_path)
            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)  # Use the setting value
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        else:
            print(f"Warning: Background music file '{bg_music_path}' not found.")
    except pygame.error as e:
        print(f"Error loading background music: {e}")

def options_menu():
    """Affiche et gère le menu des options."""
    global music_enabled, sound_effects_enabled
    
    # Sauvegarde l'état actuel de la musique pour restauration à la sortie
    original_music_volume = settings.MUSIC_VOLUME
    original_sfx_volume = settings.SFX_VOLUME
    
    # Load sound effects for volume control
    try:
        explode_sound_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
        if os.path.exists(explode_sound_path):
            explode_sound = pygame.mixer.Sound(explode_sound_path)
            explode_sound.set_volume(settings.EXPLOSION_VOLUME)
        else:
            explode_sound = None
            
        # Load death sound
        death_path = os.path.join(settings.ASSETS_DIR, "death.mp3")
        if os.path.exists(death_path):
            death_sound = pygame.mixer.Sound(death_path)
            death_sound.set_volume(settings.DEATH_VOLUME)
        else:
            death_sound = None
            
        # Load collect sound
        collect_path = os.path.join(settings.ASSETS_DIR, "collect.mp3")
        if os.path.exists(collect_path):
            collect_sound = pygame.mixer.Sound(collect_path)
            collect_sound.set_volume(settings.COLLECT_VOLUME)
        else:
            collect_sound = None
        
        # Load game-over sound
        game_over_path = os.path.join(settings.ASSETS_DIR, "game-over.mp3")
        if os.path.exists(game_over_path):
            game_over_sound = pygame.mixer.Sound(game_over_path)
            game_over_sound.set_volume(settings.GAME_OVER_VOLUME)
        else:
            game_over_sound = None
    except pygame.error as e:
        print(f"Error loading sound effects: {e}")
        explode_sound = None
        death_sound = None
        collect_sound = None
        game_over_sound = None
    
    # Function to play sound effects when enabled
    def play_sound(sound):
        if sound_effects_enabled and sound:
            sound.play()
    
    # Charge les images nécessaires
    music_label = load_image("musique.png")
    sound_effects_label = load_image("effetssonnores.png")
    music_on = load_image("musique-oui.png")
    music_off = load_image("musique-non.png")
    sound_on = load_image("effets-oui.png")
    sound_off = load_image("effets-non.png")
    exit_btn = load_image("ExitBtn.png")
    exit_click = load_image("ExitClick.png")
    
    # Redimensionne les labels
    music_label = pygame.transform.scale(
        music_label, 
        (int(music_label.get_width() * settings.MUSIC_LABEL_SCALE), 
         int(music_label.get_height() * settings.MUSIC_LABEL_SCALE))
    )
    sound_effects_label = pygame.transform.scale(
        sound_effects_label, 
        (int(sound_effects_label.get_width() * settings.SOUND_EFFECTS_LABEL_SCALE), 
         int(sound_effects_label.get_height() * settings.SOUND_EFFECTS_LABEL_SCALE))
    )
    
    # Crée les rectangles pour les labels
    music_label_rect = music_label.get_rect(
        center=(settings.MUSIC_LABEL_X_POSITION, settings.MUSIC_LABEL_Y_POSITION)
    )
    sound_effects_label_rect = sound_effects_label.get_rect(
        center=(settings.SOUND_EFFECTS_LABEL_X_POSITION, settings.SOUND_EFFECTS_LABEL_Y_POSITION)
    )
    
    # Crée les boutons à bascule avec paramètres spécifiques pour chaque bouton
    music_toggle = ToggleButton(
        settings.MUSIC_LABEL_X_POSITION + settings.MUSIC_TOGGLE_OFFSET_X,
        settings.MUSIC_LABEL_Y_POSITION,
        music_on, music_off, 
        initial_state=music_enabled, 
        scale=settings.MUSIC_TOGGLE_SCALE,
        shadow_offset=settings.MUSIC_TOGGLE_SHADOW_OFFSET,
        shadow_alpha=settings.MUSIC_TOGGLE_SHADOW_ALPHA
    )
    
    sound_toggle = ToggleButton(
        settings.SOUND_EFFECTS_LABEL_X_POSITION + settings.SOUND_TOGGLE_OFFSET_X,
        settings.SOUND_EFFECTS_LABEL_Y_POSITION,
        sound_on, sound_off, 
        initial_state=sound_effects_enabled, 
        scale=settings.SOUND_TOGGLE_SCALE,
        shadow_offset=settings.SOUND_TOGGLE_SHADOW_OFFSET,
        shadow_alpha=settings.SOUND_TOGGLE_SHADOW_ALPHA
    )
    
    # Crée le bouton de retour
    exit_button = Button(
        settings.OPTIONS_EXIT_BUTTON_X_POSITION,
        settings.OPTIONS_EXIT_BUTTON_Y_POSITION,
        exit_btn, exit_click, scale=settings.OPTIONS_EXIT_BUTTON_SCALE
    )
    
    # Charge le titre
    title_img = load_image("title.png")
    
    # Title animation variables
    title_scale = settings.TITLE_SCALE
    title_hover = False
    
    # Charge et redimensionne la bordure
    border_img = load_image("fullborder.png")
    original_border_size = border_img.get_size()
    scaled_border_size = (
        int(original_border_size[0] * settings.BORDER_SCALE), 
        int(original_border_size[1] * settings.BORDER_SCALE)
    )
    scaled_border_img = pygame.transform.scale(border_img, scaled_border_size)
    border_rect = scaled_border_img.get_rect(
        center=(settings.BORDER_X_POSITION, settings.BORDER_Y_POSITION)
    )
    
    # Initialize title with current scale
    scaled_title_width = int(title_img.get_width() * title_scale)
    scaled_title_height = int(title_img.get_height() * title_scale)
    scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
    title_rect = scaled_title.get_rect(center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION))
    
    # Initialise le gestionnaire de curseur
    cursor_manager = CursorManager()
    
    # Initialise l'animation de pixels
    pixel_animation = PixelAnimation()
    
    # Initialise l'animation de transition
    transition_animation = TransitionAnimation()
    
    # Initialise l'animation de flash d'écran
    screen_flash = ScreenFlash()
    screen_flash.start()  # Commence avec un flash d'écran
    
    # Variables d'état
    running = True
    in_transition = False
    next_scene = None
    
    # Pour calculer le delta time
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks() / 1000.0
    
    # Boucle principale du menu des options
    while running:
        # Calcule le delta time
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        
        # Obtient la position de la souris
        mouse_pos = pygame.mouse.get_pos()
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not in_transition:  # Clic gauche et pas en transition
                    # Play click sound
                    play_sound(explode_sound)
                    
                    # Génère des particules à la position du clic
                    pixel_animation.spawn_particles(event.pos[0], event.pos[1])
                    
                    # Vérifie si les boutons sont cliqués
                    if music_toggle.check_click(event.pos):
                        # Met à jour l'état de la musique
                        music_enabled = music_toggle.get_state()
                        if music_enabled:
                            pygame.mixer.music.set_volume(original_music_volume)
                        else:
                            pygame.mixer.music.set_volume(0)
                            
                    elif sound_toggle.check_click(event.pos):
                        # Met à jour l'état des effets sonores
                        sound_effects_enabled = sound_toggle.get_state()
                        if sound_effects_enabled:
                            settings.SFX_VOLUME = original_sfx_volume
                            settings.EXPLOSION_VOLUME = original_sfx_volume * 0.8
                            settings.COLLECT_VOLUME = original_sfx_volume
                            settings.DEATH_VOLUME = original_sfx_volume * 1.2
                            settings.GAME_OVER_VOLUME = original_sfx_volume * 1.4
                            
                            # Re-enable sounds immediately
                            if explode_sound:
                                explode_sound.set_volume(settings.EXPLOSION_VOLUME)
                            if death_sound:
                                death_sound.set_volume(settings.DEATH_VOLUME)
                            if collect_sound:
                                collect_sound.set_volume(settings.COLLECT_VOLUME)
                            if game_over_sound:
                                game_over_sound.set_volume(settings.GAME_OVER_VOLUME)
                        else:
                            settings.SFX_VOLUME = 0
                            settings.EXPLOSION_VOLUME = 0
                            settings.COLLECT_VOLUME = 0
                            settings.DEATH_VOLUME = 0
                            settings.GAME_OVER_VOLUME = 0
                            
                            # Disable sounds immediately
                            if explode_sound:
                                explode_sound.set_volume(0)
                            if death_sound:
                                death_sound.set_volume(0)
                            if collect_sound:
                                collect_sound.set_volume(0)
                            if game_over_sound:
                                game_over_sound.set_volume(0)
                        
                    elif exit_button.check_click(event.pos):
                        # Démarre l'animation de transition pour revenir au menu principal
                        # Don't include the title in the transition elements so it stays visible
                        ui_elements = [
                            (music_label, music_label_rect),
                            (sound_effects_label, sound_effects_label_rect),
                            (music_toggle.image, music_toggle.rect),
                            (sound_toggle.image, sound_toggle.rect),
                            (exit_button.image, exit_button.rect)
                        ]
                        transition_animation.start(ui_elements, "exit")
                        in_transition = True
                        next_scene = "exit"
            
        # Vérifie le survol des boutons si pas en transition
        if not in_transition:
            music_toggle.check_hover(mouse_pos)
            sound_toggle.check_hover(mouse_pos)
            exit_button.check_hover(mouse_pos)
            
            # Vérifie le survol des boutons pour l'animation de pixels
            pixel_animation.check_button_hover([music_toggle, sound_toggle, exit_button])
        
        # Always calculate title hover effect, even during transition
        # Calculate title hover effect (moves up and down slightly)
        time = pygame.time.get_ticks() / 1000  # Convert to seconds
        title_y_offset = math.sin(time * settings.TITLE_HOVER_SPEED) * settings.TITLE_HOVER_AMPLITUDE
        
        # Calculate title rect for hover detection
        base_title_rect = title_img.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Only check hover interaction and scaling if not in transition
        if not in_transition:
            # Check if mouse is hovering over title
            if base_title_rect.collidepoint(mouse_pos):
                title_hover = True
                # Gradually increase scale up to max
                title_scale = min(title_scale + settings.TITLE_SCALE_SPEED, settings.TITLE_MAX_SCALE)
            else:
                title_hover = False
                # Gradually decrease scale back to normal
                title_scale = max(title_scale - settings.TITLE_SCALE_SPEED, settings.TITLE_SCALE)
        
        # Scale the title image based on hover state
        scaled_title_width = int(title_img.get_width() * title_scale)
        scaled_title_height = int(title_img.get_height() * title_scale)
        scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
        title_rect = scaled_title.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Met à jour le gestionnaire de curseur
        hovering_button = (
            music_toggle.hovered or 
            sound_toggle.hovered or 
            exit_button.hovered
        )
        cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hovering_button,
            hovering_title=title_hover,
            mouse_in_window=True
        )
        
        # Met à jour l'animation de pixels
        pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Met à jour l'animation de flash d'écran
        screen_flash.update(dt)
        
        # Met à jour l'animation de transition si en cours
        if in_transition:
            transition_active = transition_animation.update(dt)
            
            # Si l'animation de transition est terminée
            if not transition_active and transition_animation.all_elements_exited_screen():
                if next_scene == "exit":
                    # Démarre le flash d'écran puis retourne au menu principal
                    screen_flash.start()
                    running = False
        
        # Dessine l'écran
        screen.fill(settings.BLACK)
        
        # Dessine la bordure comme arrière-plan
        screen.blit(scaled_border_img, border_rect)
        
        # Dessine le titre
        screen.blit(scaled_title, title_rect)
        
        # Dessine les éléments de l'interface ou l'animation de transition
        if in_transition:
            transition_animation.draw(screen)
        else:
            # Dessine les labels et les boutons
            screen.blit(music_label, music_label_rect)
            screen.blit(sound_effects_label, sound_effects_label_rect)
            music_toggle.draw(screen)
            sound_toggle.draw(screen)
            exit_button.draw(screen)
        
        # Dessine l'animation de pixels
        pixel_animation.draw(screen)
        
        # Dessine le curseur personnalisé
        cursor_manager.draw(screen)
        
        # Dessine le flash d'écran (doit être la dernière chose à dessiner)
        screen_flash.draw(screen)
        
        # Met à jour l'affichage
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    return

# Main game loop
def main():
    """Main game function."""
    global music_enabled, sound_effects_enabled
    
    clock = pygame.time.Clock()
    running = True
    
    # Initialize background music
    load_menu_music()
    
    # Load sound effects for the main menu
    try:
        explode_sound_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
        if os.path.exists(explode_sound_path):
            explode_sound = pygame.mixer.Sound(explode_sound_path)
            # Set volume based on sound effects setting
            if sound_effects_enabled:
                explode_sound.set_volume(settings.EXPLOSION_VOLUME)
            else:
                explode_sound.set_volume(0)
        else:
            print(f"Warning: Sound file '{explode_sound_path}' not found.")
            explode_sound = None
    except pygame.error as e:
        print(f"Error loading explode sound: {e}")
        explode_sound = None

    # Title expansion variables
    title_scale = settings.TITLE_SCALE
    title_hover = False
    
    # Initialize cursor manager
    cursor_manager = CursorManager()
    
    # Initialize pixel animation system
    pixel_animation = PixelAnimation()
    
    # Initialize transition animation system
    transition_animation = TransitionAnimation()
    
    # Initialize screen flash animation system
    screen_flash = ScreenFlash()
    
    # State tracking
    in_transition = False
    next_scene = None
    waiting_for_elements_exit = False
    
    # Track if mouse is inside the window
    mouse_in_window = False
    
    # For calculating delta time
    last_time = pygame.time.get_ticks() / 1000.0
    
    # Initialize scaled_title and title_rect to ensure they're defined before event handling
    scaled_title_width = int(title_img.get_width() * title_scale)
    scaled_title_height = int(title_img.get_height() * title_scale)
    scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
    title_rect = scaled_title.get_rect(center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION))
    
    # Start with an initial screen flash when the game loads
    screen_flash.start()
    
    # Charger et initialiser la police pour le meilleur score
    try:
        highscore_font = pygame.font.SysFont("Arial", settings.HIGHSCORE_FONT_SIZE, bold=False)
    except pygame.error as e:
        print(f"Erreur lors du chargement de la police pour le meilleur score: {e}")
        highscore_font = None

    # Charger le meilleur score
    highscore = load_highscore()

    try:
        highscore_font = pygame.font.SysFont("Arial", settings.HIGHSCORE_FONT_SIZE, bold=False)
    except:
        print("Error loading fonts. Using fallback.")
        highscore_font = pygame.font.Font(None, settings.HIGHSCORE_FONT_SIZE)

    while running:
        # Calculate delta time
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is inside the window
                x, y = event.pos
                mouse_in_window = (0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT)
            
            
            elif event.type == pygame.ACTIVEEVENT:
                # Handle window focus/unfocus events
                if event.gain == 0 and event.state == 1:  # Mouse left the window
                    mouse_in_window = False
                elif event.gain == 1 and event.state == 1:  # Mouse entered the window
                    mouse_in_window = True
            
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Only check button clicks if not in transition
                    if not in_transition and not waiting_for_elements_exit:
                        # Play click sound for any click on the menu
                        if explode_sound and sound_effects_enabled:
                            explode_sound.play()
                        
                        # Spawn particles at click position - allow particles anywhere on menu screen
                        pixel_animation.spawn_particles(event.pos[0], event.pos[1])
                        
                        if play_button.check_click(event.pos):
                            # Start transition animation
                            ui_elements = [
                                (scaled_title, title_rect),
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "play")
                            in_transition = True
                            next_scene = "play"
                            
                            # Fade out music before transitioning to game
                            pygame.mixer.music.fadeout(500)  # Fade out over 500ms
                        
                        elif options_button.check_click(event.pos):
                            # Start transition animation - only include name_img for transition 
                            # (title and border will remain on screen)
                            ui_elements = [
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "options")
                            in_transition = True
                            next_scene = "options"
                        
                        elif exit_button.check_click(event.pos):
                            # Start transition animation
                            ui_elements = [
                                (scaled_title, title_rect),
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "exit")
                            in_transition = True
                            next_scene = "exit"
            
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    play_button.release()
                    options_button.release()
                    exit_button.release()
        
        # If in transition mode, update the transition animation
        if in_transition:
            still_active = transition_animation.update(dt)
            
            # If transition is no longer active
            if not still_active:
                # Check if all elements have exited the screen - immediately start the flash and scene change
                if transition_animation.all_elements_exited_screen():
                    # Start the screen flash immediately
                    screen_flash.start()
                    
                    # Handle scene change immediately during the flash
                    if next_scene == "play":
                        print("Transitioning to Play scene")
                        in_transition = False
                        # Launch the game immediately - we want game elements to appear during the white flash
                        # Pass music and sound effect settings to the game
                        game_result = game.start(screen, skip_entry_flash=True, 
                                               music_enabled=music_enabled, 
                                               sound_effects_enabled=sound_effects_enabled)
                        if not game_result:
                            running = False  # Exit the game if game returns False
                        else:
                            # Game returned to menu - reset menu state
                            title_scale = settings.TITLE_SCALE
                            
                            # Actualiser le meilleur score après avoir joué
                            highscore = load_highscore()
                            
                            # Restart music when returning from game
                            try:
                                # Recharger complètement la musique du menu au lieu de juste la remettre
                                if music_enabled:
                                    load_menu_music()
                                else:
                                    # Ensure music is stopped if disabled
                                    pygame.mixer.music.stop()
                            except pygame.error as e:
                                print(f"Error restarting music: {e}")
                        
                    elif next_scene == "options":
                        print("Transitioning to Options scene")
                        in_transition = False
                        # Call the options menu function
                        options_menu()
                        
                        # Restart music when returning from options menu
                        try:
                            # In case music state was changed
                            if music_enabled:
                                pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
                            else:
                                pygame.mixer.music.set_volume(0)
                        except pygame.error as e:
                            print(f"Error restarting music: {e}")
                        
                        # Apply sound effect changes to current sounds
                        if explode_sound:
                            explode_sound.set_volume(settings.EXPLOSION_VOLUME)
                        
                        # Make sure we reset the title scale
                        title_scale = settings.TITLE_SCALE
                        
                    elif next_scene == "exit":
                        print("Exiting game")
                        # End the game immediately when white flash starts on exit button press
                        running = False
                        
                    next_scene = None
                    in_transition = False
        
        # Only check button hover states if not in transition
        if not in_transition and not waiting_for_elements_exit:
            play_button.check_hover(mouse_pos)
            options_button.check_hover(mouse_pos)
            exit_button.check_hover(mouse_pos)
            
            # Check button hover for pixel animations
            if pixel_animation.check_button_hover([play_button, options_button, exit_button]):
                # Don't play sound on button hover - only show the particles
                pass
        
        # Always calculate title hover effect, even during transition to options
        # Calculate title hover effect (moves up and down slightly)
        time = pygame.time.get_ticks() / 1000  # Convert to seconds
        title_y_offset = math.sin(time * settings.TITLE_HOVER_SPEED) * settings.TITLE_HOVER_AMPLITUDE
        
        # Calculate title rect for hover detection
        base_title_rect = title_img.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Only check hover interaction and scaling if not in transition
        if not in_transition and not waiting_for_elements_exit:
            # Check if mouse is hovering over title
            if base_title_rect.collidepoint(mouse_pos):
                title_hover = True
                # Gradually increase scale up to max
                title_scale = min(title_scale + settings.TITLE_SCALE_SPEED, settings.TITLE_MAX_SCALE)
            else:
                title_hover = False
                # Gradually decrease scale back to normal
                title_scale = max(title_scale - settings.TITLE_SCALE_SPEED, settings.TITLE_SCALE)
        
        # Scale the title image based on hover state
        scaled_title_width = int(title_img.get_width() * title_scale)
        scaled_title_height = int(title_img.get_height() * title_scale)
        scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
        title_rect = scaled_title.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Check if mouse is hovering over any buttons (excluding title)
        hovering_button = (
            play_button.hovered or 
            options_button.hovered or 
            exit_button.hovered
        )
        
        # Update cursor state with separate title hover parameter
        cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hovering_button,
            hovering_title=title_hover,
            mouse_in_window=mouse_in_window
        )
        
        # Update pixel animation
        pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Update screen flash animation
        screen_flash.update(dt)
        
        # Draw
        screen.fill(settings.BLACK)
        
        # Draw border as background (first layer) - always draw the border
        screen.blit(scaled_border_img, border_rect)
        
        # Always draw the title if going to options menu
        if in_transition and next_scene == "options":
            # Draw title with hover effect
            screen.blit(scaled_title, title_rect)
        
        # Draw UI elements or transition animation
        if in_transition:
            # If in transition, draw the border and transition elements
            transition_animation.draw(screen)
        else:
            # Draw regular UI if not in transition and not waiting for elements exit
            if not waiting_for_elements_exit:
                # Draw title with hover effect
                screen.blit(scaled_title, title_rect)
                
                # Draw buttons
                play_button.draw(screen)
                options_button.draw(screen)
                exit_button.draw(screen)
                
                # Draw name image in foreground (last layer)
                screen.blit(scaled_name_img, name_rect)
                
                # Afficher le meilleur score
                if highscore_font:
                    highscore_text = highscore_font.render(f"HIGHSCORE LOCAL: {highscore}", True, settings.WHITE)
                    highscore_rect = highscore_text.get_rect(midtop=(settings.HIGHSCORE_X_POSITION, settings.HIGHSCORE_Y_POSITION))
                    
                    # Afficher la couronne à gauche du texte du meilleur score
                    crown_rect = scaled_crown_img.get_rect(
                        midright=(highscore_rect.left - settings.CROWN_SPACING,
                                 highscore_rect.centery + settings.CROWN_Y_OFFSET)
                    )
                    screen.blit(scaled_crown_img, crown_rect)
                    
                    # Afficher le texte du highscore après la couronne
                    screen.blit(highscore_text, highscore_rect)
        
        # Draw pixel animation (should be after UI elements but before cursor)
        pixel_animation.draw(screen)
        
        # Draw the custom cursor (should be last)
        cursor_manager.draw(screen)
        
        # Draw screen flash (should be the very last thing to draw)
        screen_flash.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    # Clean up before quitting
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 