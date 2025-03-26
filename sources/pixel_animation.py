import pygame
import random
import math
import settings

class PixelParticle:
    """Represents a single pixel particle in the animation."""
    def __init__(self, x, y, angle, speed, size=3, color=(255, 255, 255)):
        """
        Initialize a pixel particle.
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            angle (float): Initial movement angle
            speed (float): Initial speed
            size (int): Size of the pixel in pixels
            color (tuple): RGB color tuple
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
        self.life = 1.0  # Full life
        self.fade_speed = random.uniform(0.5, 1.5)  # Random fade speed
        
    def update(self, dt, screen_height):
        """
        Update the particle position and properties.
        
        Args:
            dt (float): Time delta in seconds
            screen_height (int): Height of the screen for boundary checking
        
        Returns:
            bool: True if the particle is still on screen, False if it should be removed
        """
        # Update position based on velocity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Apply gravity
        self.velocity_y += self.gravity * dt * 60  # Scale by dt and target 60fps
        
        # Add slight drag/air resistance
        self.velocity_x *= 0.99
        
        # Update life (fade)
        self.life -= self.fade_speed * dt
        
        # Check if particle has fallen off the bottom of the screen or faded out
        if self.y > screen_height or self.life <= 0:
            return False
            
        return True
        
    def draw(self, surface):
        """
        Draw the particle on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        # Calculate alpha based on life
        alpha = int(255 * self.life)
        
        # Only draw if still visible
        if alpha > 0:
            # Create a surface for the particle with alpha channel
            particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Get the color with alpha
            color_with_alpha = (*self.color, alpha)
            
            # Fill with the color
            particle_surface.fill(color_with_alpha)
            
            # Draw the particle
            surface.blit(particle_surface, (self.x - self.size // 2, self.y - self.size // 2))


class PixelAnimation:
    """Manages multiple pixel particles for animations."""
    def __init__(self, auto_spawn=True):
        """
        Initialize the pixel animation system.
        
        Args:
            auto_spawn (bool): Whether to automatically spawn particles at random intervals
        """
        self.particles = []
        self.last_random_spawn = 0
        self.random_spawn_interval = random.uniform(
            settings.PIXEL_MIN_INTERVAL, 
            settings.PIXEL_MAX_INTERVAL
        )
        self.button_hover_states = {}  # Track button hover states
        self.auto_spawn = auto_spawn  # Whether to spawn particles automatically
        
        # Create particle colors dictionary
        self.particle_colors = {
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "orange": (255, 165, 0)
        }
        
    def spawn_particles(self, x, y, count=None, color="white"):
        """
        Spawn a group of particles at the given position with color-specific behaviors.
        
        Args:
            x (int): X-coordinate to spawn particles
            y (int): Y-coordinate to spawn particles
            count (int, optional): Number of particles to spawn. If None, uses PIXEL_CLICK_COUNT.
            color (str, optional): Color of the particles. Default is "white".
        """
        if count is None:
            count = settings.PIXEL_CLICK_COUNT
            
        # Get color from dictionary or use white as default
        particle_color = self.particle_colors.get(color, (255, 255, 255))
        
        for _ in range(count):
            # Base parameters that will be modified based on color
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            gravity = random.uniform(0.5, 1.5) * settings.PIXEL_GRAVITY
            fade_speed = random.uniform(0.5, 1.5)
            
            # Customize behavior based on color
            if color == "red":
                # Red particles: faster, larger, quick fade
                speed *= 1.5
                size *= 1.5
                fade_speed *= 2.0
                
            elif color == "green":
                # Green particles: float upward (negative gravity), slower fade
                gravity *= -0.5  # Float upward
                fade_speed *= 0.7  # Slower fade
                
            elif color == "orange":
                # Orange particles: outward explosion, higher particle count
                speed *= 1.3
                # No need to adjust count here as it's handled by ORANGE_SPLASH settings
                
            # Create particle with color-specific behaviors
            particle = PixelParticle(x, y, angle, speed, size, particle_color)
            particle.gravity = gravity
            particle.fade_speed = fade_speed
            self.particles.append(particle)
    
    def spawn_button_hover_particles(self, button):
        """
        Spawn particles at random positions along the button's edge when hovered.
        
        Args:
            button: The button object being hovered
        """
        # Get button rect
        rect = button.rect
        
        # Spawn the specified number of particles
        for _ in range(settings.PIXEL_BUTTON_HOVER_COUNT):
            # Choose a random edge of the button (0=top, 1=right, 2=bottom, 3=left)
            edge = random.randint(0, 3)
            
            if edge == 0:  # Top edge
                x = random.randint(rect.left, rect.right)
                y = rect.top
            elif edge == 1:  # Right edge
                x = rect.right
                y = random.randint(rect.top, rect.bottom)
            elif edge == 2:  # Bottom edge
                x = random.randint(rect.left, rect.right)
                y = rect.bottom
            else:  # Left edge
                x = rect.left
                y = random.randint(rect.top, rect.bottom)
            
            # Create particles with slightly different parameters for button hover
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)  # Slightly slower than click particles
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            color = (255, 255, 255)  # White for button hover
            
            particle = PixelParticle(x, y, angle, speed, size, color)
            self.particles.append(particle)
    
    def check_button_hover(self, buttons):
        """
        Check if buttons are being hovered and spawn particles if needed.
        
        Args:
            buttons (list): List of button objects to check
            
        Returns:
            bool: True if particles were spawned, False otherwise
        """
        particles_spawned = False
        
        for button in buttons:
            button_id = id(button)  # Use object ID as unique identifier
            
            # If button is hovered now but wasn't before, spawn particles
            if button.hovered and not self.button_hover_states.get(button_id, False):
                self.spawn_button_hover_particles(button)
                particles_spawned = True
            
            # Update hover state
            self.button_hover_states[button_id] = button.hovered
            
        return particles_spawned
    
    def spawn_random_particles(self, screen_width, screen_height):
        """
        Spawn particles at a random location on the screen.
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        # Choose a random position that's not too close to the edges
        margin = 100
        x = random.randint(margin, screen_width - margin)
        y = random.randint(margin, screen_height - margin)
        
        # Spawn fewer particles for random events
        count = random.randint(settings.PIXEL_MIN_COUNT, settings.PIXEL_MAX_COUNT)
        self.spawn_particles(x, y, count=count)
    
    def update(self, dt, screen_width, screen_height):
        """
        Update all particles and check for random spawn events.
        
        Args:
            dt (float): Time delta in seconds
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        # Update existing particles and remove those that fall off the screen
        self.particles = [p for p in self.particles if p.update(dt, screen_height)]
        
        # Check if auto-spawning is enabled
        if self.auto_spawn:
            # Check if it's time for a random spawn
            self.last_random_spawn += dt
            if self.last_random_spawn >= self.random_spawn_interval:
                self.spawn_random_particles(screen_width, screen_height)
                self.last_random_spawn = 0
                # Set a new random interval
                self.random_spawn_interval = random.uniform(
                    settings.PIXEL_MIN_INTERVAL, 
                    settings.PIXEL_MAX_INTERVAL
                )
    
    def draw(self, surface):
        """
        Draw all particles on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        for particle in self.particles:
            particle.draw(surface)