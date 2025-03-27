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

# Main ———————————————————————————————————————————————————————————————————————————————————————————————
# ————————————————————————————————————————————————————————————————————————————————————————————————————

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
    """Charge et joue la musique de fond du menu."""
    global music_enabled
    
    # Ne charge pas la musique si elle est désactivée
    if not music_enabled:
        pygame.mixer.music.stop()
        return
        
    try:
        # Charge et joue la musique de fond
        bg_music_path = os.path.join(settings.ASSETS_DIR, "pixel-song.mp3")
        if os.path.exists(bg_music_path):
            pygame.mixer.music.load(bg_music_path)
            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)  # Utilise la valeur du paramètre
            pygame.mixer.music.play(-1)  # -1 signifie boucler indéfiniment
        else:
            print(f"Avertissement: Fichier de musique de fond '{bg_music_path}' introuvable.")
    except pygame.error as e:
        print(f"Erreur lors du chargement de la musique de fond: {e}")

def options_menu():
    """Affiche et gère le menu des options."""
    global music_enabled, sound_effects_enabled
    
    # Sauvegarde l'état actuel de la musique pour restauration à la sortie
    original_music_volume = settings.MUSIC_VOLUME
    original_sfx_volume = settings.SFX_VOLUME
    
    # Charge les effets sonores pour le contrôle du volume
    try:
        explode_sound_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
        if os.path.exists(explode_sound_path):
            explode_sound = pygame.mixer.Sound(explode_sound_path)
            explode_sound.set_volume(settings.EXPLOSION_VOLUME)
        else:
            explode_sound = None
            
        # Charge le son de mort
        death_path = os.path.join(settings.ASSETS_DIR, "death.mp3")
        if os.path.exists(death_path):
            death_sound = pygame.mixer.Sound(death_path)
            death_sound.set_volume(settings.DEATH_VOLUME)
        else:
            death_sound = None
            
        # Charge le son de collecte
        collect_path = os.path.join(settings.ASSETS_DIR, "collect.mp3")
        if os.path.exists(collect_path):
            collect_sound = pygame.mixer.Sound(collect_path)
            collect_sound.set_volume(settings.COLLECT_VOLUME)
        else:
            collect_sound = None
        
        # Charge le son de game-over
        game_over_path = os.path.join(settings.ASSETS_DIR, "game-over.mp3")
        if os.path.exists(game_over_path):
            game_over_sound = pygame.mixer.Sound(game_over_path)
            game_over_sound.set_volume(settings.GAME_OVER_VOLUME)
        else:
            game_over_sound = None
    except pygame.error as e:
        print(f"Erreur lors du chargement des effets sonores: {e}")
        explode_sound = None
        death_sound = None
        collect_sound = None
        game_over_sound = None
    
    # Fonction pour jouer les effets sonores lorsqu'ils sont activés
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
    
    # Variables d'animation du titre
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
    
    # Initialise le titre avec l'échelle actuelle
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
    waiting_for_elements_exit = False
    
    # Pour calculer le delta time
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks() / 1000.0
    
    # Charger le meilleur score
    highscore = load_highscore()
    
    # Charger et initialiser la police pour le meilleur score
    try:
        highscore_font = pygame.font.SysFont("Arial", settings.HIGHSCORE_FONT_SIZE, bold=False)
    except pygame.error as e:
        print(f"Erreur lors du chargement de la police pour le meilleur score: {e}")
        highscore_font = None
    
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
                            # Restart music immediately when toggled on
                            try:
                                # Reset the volume in settings first
                                settings.MUSIC_VOLUME = original_music_volume
                                # Stop any currently playing music
                                pygame.mixer.music.stop()
                                # Reload music and play
                                bg_music_path = os.path.join(settings.ASSETS_DIR, "pixel-song.mp3")
                                if os.path.exists(bg_music_path):
                                    pygame.mixer.music.load(bg_music_path)
                                    pygame.mixer.music.set_volume(original_music_volume)
                                    pygame.mixer.music.play(-1)
                            except pygame.error as e:
                                print(f"Error restarting music: {e}")
                        else:
                            # Just stop the music entirely when disabled
                            pygame.mixer.music.stop()
                            # Also set volume to 0
                            settings.MUSIC_VOLUME = 0
                            
                    elif sound_toggle.check_click(event.pos):
                        # Met à jour l'état des effets sonores
                        sound_effects_enabled = sound_toggle.get_state()
                        if sound_effects_enabled:
                            # Reset all volume settings to original values
                            settings.SFX_VOLUME = original_sfx_volume
                            settings.EXPLOSION_VOLUME = original_sfx_volume * 0.8
                            settings.COLLECT_VOLUME = original_sfx_volume
                            settings.DEATH_VOLUME = original_sfx_volume * 1.2
                            settings.GAME_OVER_VOLUME = original_sfx_volume * 1.4
                            
                            # Re-enable sounds immediately
                            if explode_sound:
                                explode_sound.set_volume(settings.EXPLOSION_VOLUME)
                                # Play sound immediately to demonstrate sound is working
                                explode_sound.play()
                            if death_sound:
                                death_sound.set_volume(settings.DEATH_VOLUME)
                            if collect_sound:
                                collect_sound.set_volume(settings.COLLECT_VOLUME)
                            if game_over_sound:
                                game_over_sound.set_volume(settings.GAME_OVER_VOLUME)
                        else:
                            # Zero out all volume settings
                            settings.SFX_VOLUME = 0
                            settings.EXPLOSION_VOLUME = 0
                            settings.COLLECT_VOLUME = 0
                            settings.DEATH_VOLUME = 0
                            settings.GAME_OVER_VOLUME = 0
                            
                            # Disable sounds immediately
                            if explode_sound:
                                explode_sound.set_volume(0)
                                explode_sound.stop()  # Stop any currently playing sounds
                            if death_sound:
                                death_sound.set_volume(0)
                                death_sound.stop()
                            if collect_sound:
                                collect_sound.set_volume(0)
                                collect_sound.stop()
                            if game_over_sound:
                                game_over_sound.set_volume(0)
                                game_over_sound.stop()
                        
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
        
        # Toujours calculer l'effet de survol du titre, même pendant la transition vers les options
        # Calcule l'effet de survol du titre (se déplace légèrement vers le haut et le bas)
        time = pygame.time.get_ticks() / 1000  # Convertit en secondes
        title_y_offset = math.sin(time * settings.TITLE_HOVER_SPEED) * settings.TITLE_HOVER_AMPLITUDE
        
        # Calcule le rectangle du titre pour la détection de survol
        base_title_rect = title_img.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Vérifie l'interaction de survol et la mise à l'échelle uniquement si pas en transition
        if not in_transition:
            # Vérifie si la souris survole le titre
            if base_title_rect.collidepoint(mouse_pos):
                title_hover = True
                # Augmente progressivement l'échelle jusqu'au maximum
                title_scale = min(title_scale + settings.TITLE_SCALE_SPEED, settings.TITLE_MAX_SCALE)
            else:
                title_hover = False
                # Diminue progressivement l'échelle pour revenir à la normale
                title_scale = max(title_scale - settings.TITLE_SCALE_SPEED, settings.TITLE_SCALE)
        
        # Met à l'échelle l'image du titre en fonction de l'état de survol
        scaled_title_width = int(title_img.get_width() * title_scale)
        scaled_title_height = int(title_img.get_height() * title_scale)
        scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
        title_rect = scaled_title.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Vérifie si la souris survole un bouton quelconque (à l'exclusion du titre)
        hovering_button = (
            music_toggle.hovered or 
            sound_toggle.hovered or 
            exit_button.hovered
        )
        
        # Met à jour l'état du curseur avec un paramètre de survol du titre distinct
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
        
        # Dessine
        screen.fill(settings.BLACK)
        
        # Dessine la bordure comme arrière-plan (première couche) - dessine toujours la bordure
        screen.blit(scaled_border_img, border_rect)
        
        # Dessine le titre
        screen.blit(scaled_title, title_rect)
        
        # Dessine les éléments de l'interface ou l'animation de transition
        if in_transition:
            # Si en transition, dessine la bordure et les éléments de transition
            transition_animation.draw(screen)
        else:
            # Dessine les labels et les boutons
            screen.blit(music_label, music_label_rect)
            screen.blit(sound_effects_label, sound_effects_label_rect)
            music_toggle.draw(screen)
            sound_toggle.draw(screen)
            exit_button.draw(screen)
        
        # Dessine l'animation de pixels (doit être après les éléments de l'interface mais avant le curseur)
        pixel_animation.draw(screen)
        
        # Dessine le curseur personnalisé (doit être en dernier)
        cursor_manager.draw(screen)
        
        # Dessine le flash d'écran (doit être la toute dernière chose à dessiner)
        screen_flash.draw(screen)
        
        # Met à jour l'affichage
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    return

# Main game loop
def main():
    """Fonction principale du jeu."""
    global music_enabled, sound_effects_enabled
    
    clock = pygame.time.Clock()
    running = True
    
    # Stocke les paramètres de volume originaux au démarrage
    ORIGINAL_MUSIC_VOLUME = settings.MUSIC_VOLUME
    ORIGINAL_SFX_VOLUME = settings.SFX_VOLUME
    ORIGINAL_EXPLOSION_VOLUME = settings.EXPLOSION_VOLUME
    ORIGINAL_COLLECT_VOLUME = settings.COLLECT_VOLUME
    ORIGINAL_DEATH_VOLUME = settings.DEATH_VOLUME
    ORIGINAL_GAME_OVER_VOLUME = settings.GAME_OVER_VOLUME
    
    # Fonction pour initialiser ou mettre à jour correctement les paramètres sonores
    def update_sound_settings():
        nonlocal explode_sound
        
        # Initialise ou met à jour la musique de fond
        if music_enabled:
            # Restaure le volume de musique original
            settings.MUSIC_VOLUME = ORIGINAL_MUSIC_VOLUME
            # Force explicitement le rechargement et la lecture de la musique
            try:
                pygame.mixer.music.stop()  # Arrête d'abord toute musique existante
                bg_music_path = os.path.join(settings.ASSETS_DIR, "pixel-song.mp3")
                if os.path.exists(bg_music_path):
                    pygame.mixer.music.load(bg_music_path)
                    pygame.mixer.music.set_volume(ORIGINAL_MUSIC_VOLUME)
                    pygame.mixer.music.play(-1)
                else:
                    print(f"Avertissement: Fichier de musique de fond '{bg_music_path}' introuvable.")
            except pygame.error as e:
                print(f"Erreur lors du rechargement de la musique: {e}")
        else:
            # S'assure que le volume de la musique est à 0 dans les paramètres
            settings.MUSIC_VOLUME = 0
            pygame.mixer.music.stop()
        
        # Initialise ou met à jour les paramètres des effets sonores
        if sound_effects_enabled:
            # Restaure tous les volumes d'effets sonores originaux
            settings.SFX_VOLUME = ORIGINAL_SFX_VOLUME
            settings.EXPLOSION_VOLUME = ORIGINAL_EXPLOSION_VOLUME
            settings.COLLECT_VOLUME = ORIGINAL_COLLECT_VOLUME
            settings.DEATH_VOLUME = ORIGINAL_DEATH_VOLUME
            settings.GAME_OVER_VOLUME = ORIGINAL_GAME_OVER_VOLUME
        else:
            # Met tous les volumes d'effets sonores à 0
            settings.SFX_VOLUME = 0
            settings.EXPLOSION_VOLUME = 0
            settings.COLLECT_VOLUME = 0
            settings.DEATH_VOLUME = 0
            settings.GAME_OVER_VOLUME = 0
        
        # Recharge toujours le son d'explosion
        try:
            explode_sound_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
            if os.path.exists(explode_sound_path):
                # Recharge toujours le son pour assurer une nouvelle instance
                explode_sound = pygame.mixer.Sound(explode_sound_path)
                # Règle le volume en fonction du paramètre des effets sonores
                if sound_effects_enabled:
                    explode_sound.set_volume(ORIGINAL_EXPLOSION_VOLUME)
                else:
                    explode_sound.set_volume(0)
            else:
                print(f"Avertissement: Fichier son '{explode_sound_path}' introuvable.")
                explode_sound = None
        except pygame.error as e:
            print(f"Erreur lors du chargement du son d'explosion: {e}")
            explode_sound = None
    
    # Initialise les effets sonores pour le menu principal
    explode_sound = None
    update_sound_settings()
    
    # Variables d'expansion du titre
    title_scale = settings.TITLE_SCALE
    title_hover = False
    
    # Initialise le gestionnaire de curseur
    cursor_manager = CursorManager()
    
    # Initialise le système d'animation de pixels
    pixel_animation = PixelAnimation()
    
    # Initialise le système d'animation de transition
    transition_animation = TransitionAnimation()
    
    # Initialise le système d'animation de flash d'écran
    screen_flash = ScreenFlash()
    
    # Suivi d'état
    in_transition = False
    next_scene = None
    waiting_for_elements_exit = False
    
    # Suivi si la souris est à l'intérieur de la fenêtre
    mouse_in_window = False
    
    # Pour calculer le delta time
    last_time = pygame.time.get_ticks() / 1000.0
    
    # Initialise scaled_title et title_rect pour s'assurer qu'ils sont définis avant le traitement des événements
    scaled_title_width = int(title_img.get_width() * title_scale)
    scaled_title_height = int(title_img.get_height() * title_scale)
    scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
    title_rect = scaled_title.get_rect(center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION))
    
    # Commence avec un flash d'écran initial lorsque le jeu se charge
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
        # Calcule le delta time
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Traite les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                # Vérifie si la souris est à l'intérieur de la fenêtre
                x, y = event.pos
                mouse_in_window = (0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT)
            
            
            elif event.type == pygame.ACTIVEEVENT:
                # Gère les événements de focus/perte de focus de la fenêtre
                if event.gain == 0 and event.state == 1:  # La souris a quitté la fenêtre
                    mouse_in_window = False
                elif event.gain == 1 and event.state == 1:  # La souris est entrée dans la fenêtre
                    mouse_in_window = True
            
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Bouton gauche de la souris
                    # Vérifie les clics de bouton uniquement si pas en transition
                    if not in_transition and not waiting_for_elements_exit:
                        # Joue le son de clic pour tout clic sur le menu
                        if explode_sound and sound_effects_enabled:
                            explode_sound.play()
                        
                        # Génère des particules à la position du clic - permet les particules partout sur l'écran du menu
                        pixel_animation.spawn_particles(event.pos[0], event.pos[1])
                        
                        if play_button.check_click(event.pos):
                            # Démarre l'animation de transition
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
                            
                            # Fait disparaître la musique avant de passer au jeu
                            pygame.mixer.music.fadeout(500)  # Fondu sortant sur 500ms
                        
                        elif options_button.check_click(event.pos):
                            # Démarre l'animation de transition - inclut seulement name_img pour la transition
                            # (le titre et la bordure resteront à l'écran)
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
                            # Démarre l'animation de transition
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
                if event.button == 1:  # Bouton gauche de la souris relâché
                    play_button.release()
                    options_button.release()
                    exit_button.release()
        
        # Si en mode transition, met à jour l'animation de transition
        if in_transition:
            still_active = transition_animation.update(dt)
            
            # Si la transition n'est plus active
            if not still_active:
                # Vérifie si tous les éléments ont quitté l'écran - démarre immédiatement le flash et le changement de scène
                if transition_animation.all_elements_exited_screen():
                    # Démarre le flash d'écran immédiatement
                    screen_flash.start()
                    
                    # Gère le changement de scène immédiatement pendant le flash
                    if next_scene == "play":
                        print("Transition vers la scène de jeu")
                        in_transition = False
                        # Lance le jeu immédiatement - nous voulons que les éléments du jeu apparaissent pendant le flash blanc
                        # Passe les paramètres de musique et d'effets sonores au jeu
                        game_result = game.start(screen, skip_entry_flash=True, 
                                               music_enabled=music_enabled, 
                                               sound_effects_enabled=sound_effects_enabled)
                        if not game_result:
                            running = False  # Quitte le jeu si le jeu renvoie False
                        else:
                            # Le jeu est retourné au menu - réinitialise l'état du menu
                            title_scale = settings.TITLE_SCALE
                            
                            # Actualise le meilleur score après avoir joué
                            highscore = load_highscore()
                            
                            # Met à jour correctement tous les paramètres sonores lors du retour du jeu
                            update_sound_settings()
                        
                    elif next_scene == "options":
                        print("Transition vers la scène d'options")
                        in_transition = False
                        waiting_for_elements_exit = False
                        # Appelle la fonction du menu des options
                        options_menu()
                        
                        # Recharge le score après retour du menu options
                        highscore = load_highscore()
                        
                        # Met à jour correctement tous les paramètres sonores lors du retour des options
                        update_sound_settings()
                        
                        # S'assure de réinitialiser l'échelle du titre
                        title_scale = settings.TITLE_SCALE
                        
                    elif next_scene == "exit":
                        print("Quitter le jeu")
                        # Termine le jeu immédiatement quand le flash blanc commence sur l'appui du bouton de sortie
                        running = False
                        
                    next_scene = None
                    in_transition = False
        
        # Vérifie uniquement les états de survol des boutons si pas en transition
        if not in_transition and not waiting_for_elements_exit:
            play_button.check_hover(mouse_pos)
            options_button.check_hover(mouse_pos)
            exit_button.check_hover(mouse_pos)
            
            # Vérifie le survol des boutons pour les animations de pixels
            if pixel_animation.check_button_hover([play_button, options_button, exit_button]):
                # Ne joue pas de son au survol des boutons - montre uniquement les particules
                pass
        
        # Toujours calculer l'effet de survol du titre, même pendant la transition vers les options
        # Calcule l'effet de survol du titre (se déplace légèrement vers le haut et le bas)
        time = pygame.time.get_ticks() / 1000  # Convertit en secondes
        title_y_offset = math.sin(time * settings.TITLE_HOVER_SPEED) * settings.TITLE_HOVER_AMPLITUDE
        
        # Calcule le rectangle du titre pour la détection de survol
        base_title_rect = title_img.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Vérifie l'interaction de survol et la mise à l'échelle uniquement si pas en transition
        if not in_transition and not waiting_for_elements_exit:
            # Vérifie si la souris survole le titre
            if base_title_rect.collidepoint(mouse_pos):
                title_hover = True
                # Augmente progressivement l'échelle jusqu'au maximum
                title_scale = min(title_scale + settings.TITLE_SCALE_SPEED, settings.TITLE_MAX_SCALE)
            else:
                title_hover = False
                # Diminue progressivement l'échelle pour revenir à la normale
                title_scale = max(title_scale - settings.TITLE_SCALE_SPEED, settings.TITLE_SCALE)
        
        # Met à l'échelle l'image du titre en fonction de l'état de survol
        scaled_title_width = int(title_img.get_width() * title_scale)
        scaled_title_height = int(title_img.get_height() * title_scale)
        scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
        title_rect = scaled_title.get_rect(
            center=(settings.TITLE_X_POSITION, settings.TITLE_Y_POSITION + title_y_offset)
        )
        
        # Vérifie si la souris survole un bouton quelconque (à l'exclusion du titre)
        hovering_button = (
            play_button.hovered or 
            options_button.hovered or 
            exit_button.hovered
        )
        
        # Met à jour l'état du curseur avec un paramètre de survol du titre distinct
        cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hovering_button,
            hovering_title=title_hover,
            mouse_in_window=mouse_in_window
        )
        
        # Met à jour l'animation de pixels
        pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Met à jour l'animation de flash d'écran
        screen_flash.update(dt)
        
        # Dessine
        screen.fill(settings.BLACK)
        
        # Dessine la bordure comme arrière-plan (première couche) - dessine toujours la bordure
        screen.blit(scaled_border_img, border_rect)
        
        # Dessine toujours le titre si on va vers le menu des options
        if in_transition and next_scene == "options":
            # Dessine le titre avec l'effet de survol
            screen.blit(scaled_title, title_rect)
        
        # Dessine les éléments de l'interface ou l'animation de transition
        if in_transition:
            # Si en transition, dessine la bordure et les éléments de transition
            transition_animation.draw(screen)
        else:
            # Dessine l'interface normale si pas en transition et pas en attente de sortie des éléments
            if not waiting_for_elements_exit:
                # Dessine le titre avec l'effet de survol
                screen.blit(scaled_title, title_rect)
                
                # Dessine les boutons
                play_button.draw(screen)
                options_button.draw(screen)
                exit_button.draw(screen)
                
                # Dessine l'image du nom au premier plan (dernière couche)
                screen.blit(scaled_name_img, name_rect)
                
                # Affiche le meilleur score
                if highscore_font:
                    highscore_text = highscore_font.render(f"HIGHSCORE LOCAL: {highscore}", True, settings.WHITE)
                    highscore_rect = highscore_text.get_rect(midtop=(settings.HIGHSCORE_X_POSITION, settings.HIGHSCORE_Y_POSITION))
                    
                    # Affiche la couronne à gauche du texte du meilleur score
                    crown_rect = scaled_crown_img.get_rect(
                        midright=(highscore_rect.left - settings.CROWN_SPACING,
                                 highscore_rect.centery + settings.CROWN_Y_OFFSET)
                    )
                    screen.blit(scaled_crown_img, crown_rect)
                    
                    # Affiche le texte du highscore après la couronne
                    screen.blit(highscore_text, highscore_rect)
        
        # Dessine l'animation de pixels (doit être après les éléments de l'interface mais avant le curseur)
        pixel_animation.draw(screen)
        
        # Dessine le curseur personnalisé (doit être en dernier)
        cursor_manager.draw(screen)
        
        # Dessine le flash d'écran (doit être la toute dernière chose à dessiner)
        screen_flash.draw(screen)
        
        # Met à jour l'affichage
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    # Nettoie avant de quitter
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 