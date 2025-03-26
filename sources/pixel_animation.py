import pygame
import random
import math
import settings

class PixelParticle:
    """Représente une particule de pixel unique dans l'animation."""
    def __init__(self, x, y, angle, speed, size=3, color=(255, 255, 255)):
        """
        Initialise une particule de pixel.
        
        Args:
            x (float): Position x initiale
            y (float): Position y initiale
            angle (float): Angle de mouvement initial
            speed (float): Vitesse initiale
            size (int): Taille du pixel en pixels
            color (tuple): Tuple de couleur RGB
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.size = size
        self.color = color
        self.gravity = random.uniform(0.5, 1.5) * settings.PIXEL_GRAVITY
        self.life = 1.0  # Vie complète
        self.fade_speed = random.uniform(0.5, 1.5)  # Vitesse de fondu aléatoire
        
    def update(self, dt, screen_height):
        """
        Met à jour la position et les propriétés de la particule.
        
        Args:
            dt (float): Delta temps en secondes
            screen_height (int): Hauteur de l'écran pour la vérification des limites
        
        Returns:
            bool: True si la particule est toujours à l'écran, False si elle doit être supprimée
        """
        # Met à jour la position en fonction de la vitesse
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Applique la gravité
        self.velocity_y += self.gravity * dt * 60  # Mise à l'échelle par dt et cible 60fps
        
        # Ajoute une légère traînée/résistance à l'air
        self.velocity_x *= 0.99
        
        # Met à jour la vie (fondu)
        self.life -= self.fade_speed * dt
        
        # Vérifie si la particule est tombée en bas de l'écran ou s'est estompée
        if self.y > screen_height or self.life <= 0:
            return False
            
        return True
        
    def draw(self, surface):
        """
        Dessine la particule sur la surface donnée.
        
        Args:
            surface (Surface): Surface Pygame sur laquelle dessiner
        """
        # Calcule l'alpha en fonction de la vie
        alpha = int(255 * self.life)
        
        # Dessine uniquement si encore visible
        if alpha > 0:
            # Crée une surface pour la particule avec canal alpha
            particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Obtient la couleur avec alpha
            color_with_alpha = (*self.color, alpha)
            
            # Remplit avec la couleur
            particle_surface.fill(color_with_alpha)
            
            # Dessine la particule
            surface.blit(particle_surface, (self.x - self.size // 2, self.y - self.size // 2))


class PixelAnimation:
    """Gère plusieurs particules de pixels pour les animations."""
    def __init__(self, auto_spawn=True):
        """
        Initialise le système d'animation de pixels.
        
        Args:
            auto_spawn (bool): Indique s'il faut générer automatiquement des particules à intervalles aléatoires
        """
        self.particles = []
        self.last_random_spawn = 0
        self.random_spawn_interval = random.uniform(
            settings.PIXEL_MIN_INTERVAL, 
            settings.PIXEL_MAX_INTERVAL
        )
        self.button_hover_states = {}  # Suit les états de survol des boutons
        self.auto_spawn = auto_spawn  # Indique s'il faut générer des particules automatiquement
        
        # Crée un dictionnaire de couleurs de particules
        self.particle_colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "orange": (255, 165, 0)
        }
        
    def spawn_particles(self, x, y, count=None, color="white"):
        """
        Génère un groupe de particules à la position donnée avec des comportements spécifiques à la couleur.
        
        Args:
            x (int): Coordonnée X pour générer les particules
            y (int): Coordonnée Y pour générer les particules
            count (int, optional): Nombre de particules à générer. Si None, utilise PIXEL_CLICK_COUNT.
            color (str, optional): Couleur des particules. Par défaut, c'est "white".
        """
        if count is None:
            count = settings.PIXEL_CLICK_COUNT
            
        # Obtient la couleur du dictionnaire ou utilise le blanc par défaut
        particle_color = self.particle_colors.get(color, (255, 255, 255))
        
        for _ in range(count):
            # Paramètres de base qui seront modifiés en fonction de la couleur
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            gravity = random.uniform(0.5, 1.5) * settings.PIXEL_GRAVITY
            fade_speed = random.uniform(0.5, 1.5)
            
            # Personnalise le comportement en fonction de la couleur
            if color == "red":
                # Particules rouges : plus rapides, plus grandes, fondu rapide
                speed *= 1.5
                size *= 1.5
                fade_speed *= 2.0
                
            elif color == "green":
                # Particules vertes : flottent vers le haut (gravité négative), fondu plus lent
                gravity *= -0.5  # Flotte vers le haut
                fade_speed *= 0.7  # Fondu plus lent
                
            elif color == "orange":
                # Particules orange : explosion vers l'extérieur, nombre de particules plus élevé
                speed *= 1.3
                # Pas besoin d'ajuster le nombre ici car il est géré par les paramètres ORANGE_SPLASH
                
            # Crée une particule avec des comportements spécifiques à la couleur
            particle = PixelParticle(x, y, angle, speed, size, particle_color)
            particle.gravity = gravity
            particle.fade_speed = fade_speed
            self.particles.append(particle)
    
    def spawn_button_hover_particles(self, button):
        """
        Génère des particules à des positions aléatoires le long du bord du bouton lors du survol.
        
        Args:
            button: L'objet bouton survolé
        """
        # Obtient le rectangle du bouton
        rect = button.rect
        
        # Génère le nombre spécifié de particules
        for _ in range(settings.PIXEL_BUTTON_HOVER_COUNT):
            # Choisit un bord aléatoire du bouton (0=haut, 1=droite, 2=bas, 3=gauche)
            edge = random.randint(0, 3)
            
            if edge == 0:  # Bord supérieur
                x = random.randint(rect.left, rect.right)
                y = rect.top
            elif edge == 1:  # Bord droit
                x = rect.right
                y = random.randint(rect.top, rect.bottom)
            elif edge == 2:  # Bord inférieur
                x = random.randint(rect.left, rect.right)
                y = rect.bottom
            else:  # Bord gauche
                x = rect.left
                y = random.randint(rect.top, rect.bottom)
            
            # Crée des particules avec des paramètres légèrement différents pour le survol du bouton
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)  # Légèrement plus lent que les particules de clic
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            color = (255, 255, 255)  # Blanc pour le survol du bouton
            
            particle = PixelParticle(x, y, angle, speed, size, color)
            self.particles.append(particle)
    
    def check_button_hover(self, buttons):
        """
        Vérifie si les boutons sont survolés et génère des particules si nécessaire.
        
        Args:
            buttons (list): Liste des objets bouton à vérifier
            
        Returns:
            bool: True si des particules ont été générées, False sinon
        """
        particles_spawned = False
        
        for button in buttons:
            button_id = id(button)  # Utilise l'ID de l'objet comme identifiant unique
            
            # Si le bouton est survolé maintenant mais ne l'était pas avant, génère des particules
            if button.hovered and not self.button_hover_states.get(button_id, False):
                self.spawn_button_hover_particles(button)
                particles_spawned = True
            
            # Met à jour l'état de survol
            self.button_hover_states[button_id] = button.hovered
            
        return particles_spawned
    
    def spawn_random_particles(self, screen_width, screen_height):
        """
        Génère des particules à un emplacement aléatoire sur l'écran.
        
        Args:
            screen_width (int): Largeur de l'écran
            screen_height (int): Hauteur de l'écran
        """
        # Choisit une position aléatoire qui n'est pas trop proche des bords
        margin = 100
        x = random.randint(margin, screen_width - margin)
        y = random.randint(margin, screen_height - margin)
        
        # Génère moins de particules pour les événements aléatoires
        count = random.randint(settings.PIXEL_MIN_COUNT, settings.PIXEL_MAX_COUNT)
        self.spawn_particles(x, y, count=count)
    
    def update(self, dt, screen_width, screen_height):
        """
        Met à jour toutes les particules et vérifie les événements de génération aléatoire.
        
        Args:
            dt (float): Delta temps en secondes
            screen_width (int): Largeur de l'écran
            screen_height (int): Hauteur de l'écran
        """
        # Met à jour les particules existantes et supprime celles qui sortent de l'écran
        self.particles = [p for p in self.particles if p.update(dt, screen_height)]
        
        # Vérifie s'il est temps de générer des particules aléatoires
        if self.auto_spawn:
            self.last_random_spawn += dt
            if self.last_random_spawn >= self.random_spawn_interval:
                self.spawn_random_particles(screen_width, screen_height)
                self.last_random_spawn = 0
                self.random_spawn_interval = random.uniform(
                    settings.PIXEL_MIN_INTERVAL, 
                    settings.PIXEL_MAX_INTERVAL
                )
    
    def draw(self, surface):
        """
        Dessine toutes les particules sur la surface donnée.
        
        Args:
            surface (Surface): Surface Pygame sur laquelle dessiner
        """
        for particle in self.particles:
            particle.draw(surface)