import pygame
import settings

class ScreenFlash:
    """Handles screen flash animation effect for transitions between scenes."""
    
    def __init__(self):
        """Initialize the screen flash animation system."""
        self.active = False
        self.alpha = 0  # 0 = fully transparent, 255 = fully opaque
        self.flash_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.flash_surface.fill(settings.WHITE)
        self.timer = 0
        self.callback = None
    
    def start(self, callback=None):
        """
        Start the screen flash animation.
        
        Args:
            callback (function, optional): Function to call when the flash is complete
        """
        self.active = True
        self.alpha = 255  # Start fully opaque
        self.timer = 0
        self.callback = callback
    
    def update(self, dt):
        """
        Update the screen flash animation.
        
        Args:
            dt (float): Delta time in seconds
            
        Returns:
            bool: True if the flash is still active, False otherwise
        """
        if not self.active:
            return False
            
        # Update timer
        self.timer += dt
        
        # Calculate alpha based on timer and fade speed
        fade_progress = min(self.timer / settings.FLASH_DURATION, 1.0)
        self.alpha = max(0, 255 - int(255 * fade_progress * settings.FLASH_FADE_SPEED))
        
        # Check if flash is complete
        if self.timer >= settings.FLASH_DURATION or self.alpha <= 0:
            self.active = False
            self.alpha = 0
            
            # Call the callback if provided
            if self.callback:
                self.callback()
            
            return False
            
        return True
    
    def draw(self, surface):
        """
        Draw the screen flash on the given surface.
        
        Args:
            surface (Surface): Surface to draw the flash on
        """
        if self.active and self.alpha > 0:
            self.flash_surface.set_alpha(self.alpha)
            surface.blit(self.flash_surface, (0, 0)) 