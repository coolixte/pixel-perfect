import pygame
import random
import math
import settings

# Transitions —————————————————————————————————————————————————————————————————————————————————————————
# —————————————————————————————————————————————————————————————————————————————————————————————————————

class TransitionElement:
    """Représente un élément d'interface utilisateur avec physique pendant l'animation de transition."""
    def __init__(self, image, rect, reverse=False):
        """
        Initialise un élément de transition avec des propriétés physiques.
        
        Args:
            image (Surface): L'image de l'élément d'interface
            rect (Rect): Le rectangle définissant la position et la taille de l'élément
            reverse (bool): Si True, l'élément entrera dans l'écran au lieu d'en sortir
        """
        self.image = image.copy()  # Crée une copie de l'image pour éviter de modifier l'original
        self.original_image = image.copy()  # Conserve l'original pour la rotation
        self.rect = rect.copy()
        self.reverse = reverse
        
        if reverse:
            # Pour les transitions inversées, commence hors de l'écran
            self.x = random.randint(-100, settings.SCREEN_WIDTH + 100)
            self.y = settings.SCREEN_HEIGHT + 100  # Commence sous l'écran
            
            # La destination finale sera le centre du rectangle original
            self.dest_x = rect.centerx
            self.dest_y = rect.centery
        else:
            # Transition normale (les éléments tombent hors de l'écran)
            self.x = rect.centerx
            self.y = rect.centery
        
        # Génère un angle aléatoire entre les paramètres min et max
        angle_rad = math.radians(random.uniform(
            settings.TRANSITION_MIN_ANGLE, 
            settings.TRANSITION_MAX_ANGLE
        ))
        
        # Génère une vitesse aléatoire
        speed = random.uniform(
            settings.TRANSITION_MIN_SPEED,
            settings.TRANSITION_MAX_SPEED
        )
        
        # Calcule la vitesse initiale en fonction de l'angle et de la vitesse
        if reverse:
            # Pour l'inverse, la vitesse pointe vers la destination finale
            self.velocity_x = 0  # Sera défini dans update
            self.velocity_y = 0  # Sera défini dans update
        else:
            # Transition normale
            self.velocity_x = math.sin(angle_rad) * speed
            self.velocity_y = math.cos(angle_rad) * speed  # Commence avec une vitesse vers le bas
        
        # Rotation
        self.angle = 0  # Angle de rotation actuel
        self.rotation_speed = random.uniform(-1, 1) * settings.TRANSITION_ROTATION_SPEED
        
        # Progression de l'animation
        self.elapsed_time = 0
    
    def update(self, dt):
        """
        Met à jour la position et la rotation de l'élément en fonction de la physique.
        
        Args:
            dt (float): Delta temps en secondes
            
        Returns:
            bool: True si l'animation doit continuer, False si terminée
        """
        self.elapsed_time += dt
        
        if self.reverse:
            # Transition inversée - déplacement de l'élément sur l'écran
            # Utilise une fonction d'assouplissement pour déplacer les éléments vers leurs destinations
            progress = min(self.elapsed_time / 1.0, 1.0)  # Durée de 1.0 seconde
            
            # Fonction d'assouplissement
            ease = 1 - (1 - progress) * (1 - progress)
            
            # Se déplace vers la destination
            self.x = self.x + (self.dest_x - self.x) * ease * 5 * dt
            self.y = self.y + (self.dest_y - self.y) * ease * 5 * dt
            
            # Réduit la rotation en approchant de la destination
            self.rotation_speed *= 0.95
            
            # Vérifie si nous avons atteint la destination
            distance = math.sqrt((self.x - self.dest_x)**2 + (self.y - self.dest_y)**2)
            if distance < 5 and self.elapsed_time > 1.0:
                return False  # Animation terminée
                
        else:
            # Transition normale - les éléments tombent hors de l'écran
            # Met à jour la position en fonction de la vitesse
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # Applique la gravité
            self.velocity_y += settings.TRANSITION_GRAVITY * dt * 60  # Mise à l'échelle par dt et cible 60fps
            
            # Vérifie si l'élément est tombé hors du bas de l'écran
            if self.y - self.rect.height > settings.SCREEN_HEIGHT:
                return False
        
        # Met à jour la rotation
        self.angle += self.rotation_speed * dt * 60
        
        # Fait pivoter l'image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Met à jour la position du rectangle tout en gardant le centre
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        return True
    
    def draw(self, surface):
        """
        Dessine l'élément sur la surface donnée.
        
        Args:
            surface (Surface): Surface Pygame sur laquelle dessiner
        """
        surface.blit(self.image, self.rect)


class TransitionAnimation:
    """Gère l'animation de transition pour les éléments d'interface utilisateur."""
    def __init__(self):
        """Initialise le système d'animation de transition."""
        self.elements = []
        self.is_active = False
        self.start_time = 0
        self.duration = settings.TRANSITION_DURATION
        self.target_scene = None
        self.all_elements_exited = False
        self.initial_element_count = 0
        self.reverse = False
        
    def start(self, ui_elements, target_scene=None, reverse=False):
        """
        Démarre l'animation de transition avec les éléments d'interface fournis.
        
        Args:
            ui_elements (list): Liste de tuples (image, rect) pour les éléments d'interface
            target_scene (str, optional): La scène vers laquelle transitionner après l'animation
            reverse (bool): Si True, les éléments entrent dans l'écran au lieu d'en sortir
        """
        self.elements = []
        self.reverse = reverse
        self.target_scene = target_scene
        
        # Crée les éléments de transition
        for image, rect in ui_elements:
            # Ignore les éléments None ou les rectangles vides
            if image is None or rect is None:
                continue
            self.elements.append(TransitionElement(image, rect, reverse))
        
        self.is_active = True
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.all_elements_exited = False
        self.initial_element_count = len(self.elements)
        
    def update(self, dt):
        """
        Met à jour tous les éléments de transition.
        
        Args:
            dt (float): Delta temps en secondes
            
        Returns:
            bool: True si l'animation est toujours active, False si terminée
        """
        if not self.is_active:
            return False
            
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - self.start_time
        
        # Vérifie si la durée de l'animation est passée (délai de sécurité)
        if elapsed_time >= self.duration:
            self.is_active = False
            self.elements = []
            return False
        
        # Met à jour chaque élément et supprime ceux qui sont tombés hors de l'écran
        self.elements = [elem for elem in self.elements if elem.update(dt)]
        
        # Si tous les éléments ont disparu, termine l'animation plus tôt et définit le drapeau
        if not self.elements and self.initial_element_count > 0:
            self.all_elements_exited = True
            self.is_active = False
            return False
            
        return True
        
    def draw(self, surface):
        """
        Dessine tous les éléments de transition sur la surface donnée.
        
        Args:
            surface (Surface): Surface Pygame sur laquelle dessiner
        """
        if self.is_active:
            for element in self.elements:
                element.draw(surface)
                
    def is_finished(self):
        """
        Vérifie si l'animation de transition est terminée.
        
        Returns:
            bool: True si l'animation est terminée, False sinon
        """
        return not self.is_active
        
    def all_elements_exited_screen(self):
        """
        Vérifie si tous les éléments d'interface ont quitté l'écran.
        
        Returns:
            bool: True si tous les éléments ont quitté l'écran, False sinon
        """
        return self.all_elements_exited 