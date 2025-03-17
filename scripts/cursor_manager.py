import pygame
import os
from settings import (
    ASSETS_DIR, 
    CURSOR_NORMAL, CURSOR_HOVER, CURSOR_CLICK, CURSOR_ZOOM, CURSOR_VISIBLE,
    CURSOR_NORMAL_SCALE, CURSOR_HOVER_SCALE, CURSOR_CLICK_SCALE, CURSOR_ZOOM_SCALE
)

class CursorManager:
    """
    Manages custom cursor states and rendering in pygame.
    
    This class handles loading cursor images and switching between different
    cursor states (normal, hover, click, zoom) based on user interaction.
    """
    
    def __init__(self):
        """Initialize the cursor manager with default cursor images."""
        # Load cursor images with scaling
        self.cursor_normal = self._load_cursor_image(CURSOR_NORMAL, CURSOR_NORMAL_SCALE)
        self.cursor_hover = self._load_cursor_image(CURSOR_HOVER, CURSOR_HOVER_SCALE)
        self.cursor_click = self._load_cursor_image(CURSOR_CLICK, CURSOR_CLICK_SCALE)
        self.cursor_zoom = self._load_cursor_image(CURSOR_ZOOM, CURSOR_ZOOM_SCALE)
        
        # Set initial cursor state
        self.current_cursor = self.cursor_normal
        self.is_hovering = False
        self.is_clicking = False
        self.is_zooming = False
        self.mouse_in_window = False  # Track if mouse is inside the window
        
        # Hide the system cursor if specified in settings
        pygame.mouse.set_visible(CURSOR_VISIBLE)
    
    def _load_cursor_image(self, image_name, scale=1.0):
        """
        Load a cursor image from the assets directory and scale it.
        
        Args:
            image_name: The filename of the cursor image
            scale: Scale factor to apply to the image
            
        Returns:
            A pygame Surface containing the scaled cursor image
        """
        image_path = os.path.join(ASSETS_DIR, image_name)
        try:
            image = pygame.image.load(image_path).convert_alpha()
            
            # Apply scaling if needed
            if scale != 1.0:
                orig_size = image.get_size()
                new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
                image = pygame.transform.scale(image, new_size)
                
            return image
        except pygame.error as e:
            print(f"Error loading cursor image {image_name}: {e}")
            # Create a fallback cursor (small white square)
            fallback = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (255, 255, 255, 180), (0, 0, 16, 16))
            return fallback
    
    def update(self, mouse_pos, mouse_pressed, hovering_button=False, hovering_title=False, mouse_in_window=False):
        """
        Update the cursor state based on mouse position and button state.
        
        Args:
            mouse_pos: Current mouse position (x, y)
            mouse_pressed: Boolean indicating if mouse button is pressed
            hovering_button: Boolean indicating if mouse is over a button
            hovering_title: Boolean indicating if mouse is over the title
            mouse_in_window: Boolean indicating if mouse is inside the window
        """
        self.is_hovering = hovering_button
        self.is_clicking = mouse_pressed[0]  # Left mouse button
        self.is_zooming = hovering_title
        self.mouse_in_window = mouse_in_window
        
        # Determine which cursor to display
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
        Draw the current cursor at the mouse position.
        
        Args:
            surface: The pygame surface to draw the cursor on
        """
        # Only draw the cursor if the mouse is inside the window
        if self.mouse_in_window:
            mouse_pos = pygame.mouse.get_pos()
            surface.blit(self.current_cursor, mouse_pos) 