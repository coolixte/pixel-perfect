import pygame
import os
from settings import (
    ASSETS_DIR, 
    CURSOR_NORMAL, CURSOR_HOVER, CURSOR_CLICK, CURSOR_ZOOM, CURSOR_VISIBLE,
    CURSOR_NORMAL_SCALE, CURSOR_HOVER_SCALE, CURSOR_CLICK_SCALE, CURSOR_ZOOM_SCALE
)

class CursorManager:
    """
    Gère les états du curseur personnalisé et le rendu dans pygame.
    
    Cette classe s'occupe du chargement des images de curseur et du changement entre
    différents états de curseur (normal, survol, clic, zoom) en fonction de l'interaction
    de l'utilisateur.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de curseur avec les images de curseur par défaut."""
        # Charge les images de curseur avec mise à l'échelle
        self.cursor_normal = self._load_cursor_image(CURSOR_NORMAL, CURSOR_NORMAL_SCALE)
        self.cursor_hover = self._load_cursor_image(CURSOR_HOVER, CURSOR_HOVER_SCALE)
        self.cursor_click = self._load_cursor_image(CURSOR_CLICK, CURSOR_CLICK_SCALE)
        self.cursor_zoom = self._load_cursor_image(CURSOR_ZOOM, CURSOR_ZOOM_SCALE)
        
        # Définit l'état initial du curseur
        self.current_cursor = self.cursor_normal
        self.is_hovering = False
        self.is_clicking = False
        self.is_zooming = False
        self.mouse_in_window = False  # Vérifie si la souris est dans la fenêtre
        
        # Masque le curseur système si spécifié dans les paramètres
        pygame.mouse.set_visible(CURSOR_VISIBLE)
    
    def _load_cursor_image(self, image_name, scale=1.0):
        """
        Charge une image de curseur depuis le répertoire des ressources et la redimensionne.
        
        Args:
            image_name: Le nom du fichier de l'image du curseur
            scale: Facteur d'échelle à appliquer à l'image
            
        Returns:
            Une surface pygame contenant l'image du curseur redimensionnée
        """
        image_path = os.path.join(ASSETS_DIR, image_name)
        try:
            image = pygame.image.load(image_path).convert_alpha()
            
            # Applique la mise à l'échelle si nécessaire
            if scale != 1.0:
                orig_size = image.get_size()
                new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
                image = pygame.transform.scale(image, new_size)
                
            return image
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image du curseur {image_name}: {e}")
            # Crée un curseur de secours (petit carré blanc)
            fallback = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (255, 255, 255, 180), (0, 0, 16, 16))
            return fallback
    
    def update(self, mouse_pos, mouse_pressed, hovering_button=False, hovering_title=False, mouse_in_window=False):
        """
        Met à jour l'état du curseur en fonction de la position de la souris et de l'état des boutons.
        
        Args:
            mouse_pos: Position actuelle de la souris (x, y)
            mouse_pressed: Booléen indiquant si le bouton de la souris est enfoncé
            hovering_button: Booléen indiquant si la souris survole un bouton
            hovering_title: Booléen indiquant si la souris survole le titre
            mouse_in_window: Booléen indiquant si la souris est dans la fenêtre
        """
        self.is_hovering = hovering_button
        self.is_clicking = mouse_pressed[0]  # Bouton gauche de la souris
        self.is_zooming = hovering_title
        self.mouse_in_window = mouse_in_window
        
        # Détermine quel curseur afficher
        if self.is_clicking:
            self.current_cursor = self.cursor_click
        elif self.is_zooming:
            self.current_cursor = self.cursor_zoom
        elif self.is_hovering:
            self.current_cursor = self.cursor_hover
        else:
            self.current_cursor = self.cursor_normal
    
    def draw(self, surface):
        """
        Dessine le curseur actuel à la position de la souris.
        
        Args:
            surface: La surface pygame sur laquelle dessiner le curseur
        """
        # Dessine le curseur uniquement si la souris est dans la fenêtre
        if self.mouse_in_window:
            mouse_pos = pygame.mouse.get_pos()
            surface.blit(self.current_cursor, mouse_pos) 