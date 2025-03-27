import pygame
import settings

# Screen Flash ———————————————————————————————————————————————————————————————————————————————————————
# ————————————————————————————————————————————————————————————————————————————————————————————————————

class ScreenFlash:
    """Gère l'effet d'animation de flash d'écran pour les transitions entre les scènes."""
    
    def __init__(self):
        """Initialise le système d'animation de flash d'écran."""
        self.active = False
        self.alpha = 0  # 0 = complètement transparent, 255 = complètement opaque
        self.flash_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.flash_surface.fill(settings.WHITE)
        self.timer = 0
        self.callback = None
    
    def start(self, callback=None):
        """
        Démarre l'animation de flash d'écran.
        
        Args:
            callback (function, optional): Fonction à appeler lorsque le flash est terminé
        """
        self.active = True
        self.alpha = 255  # Commence complètement opaque
        self.timer = 0
        self.callback = callback
    
    def update(self, dt):
        """
        Met à jour l'animation de flash d'écran.
        
        Args:
            dt (float): Delta temps en secondes
            
        Returns:
            bool: True si le flash est toujours actif, False sinon
        """
        if not self.active:
            return False
            
        # Met à jour le timer
        self.timer += dt
        
        # Calcule l'alpha en fonction du timer et de la vitesse de fondu
        fade_progress = min(self.timer / settings.FLASH_DURATION, 1.0)
        self.alpha = max(0, 255 - int(255 * fade_progress * settings.FLASH_FADE_SPEED))
        
        # Vérifie si le flash est terminé
        if self.timer >= settings.FLASH_DURATION or self.alpha <= 0:
            self.active = False
            self.alpha = 0
            
            # Appelle le callback s'il est fourni
            if self.callback:
                self.callback()
            
            return False
            
        return True
    
    def draw(self, surface):
        """
        Dessine le flash d'écran sur la surface donnée.
        
        Args:
            surface (Surface): Surface sur laquelle dessiner le flash
        """
        if self.active and self.alpha > 0:
            self.flash_surface.set_alpha(self.alpha)
            surface.blit(self.flash_surface, (0, 0)) 