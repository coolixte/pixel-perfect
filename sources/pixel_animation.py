import pygame
import random
import math
import settings

class PixelParticle:
    """Represents a single pixel particle in the animation."""
    def __init__(self, x, y, velocity_x, velocity_y, size=3, color=(255, 255, 255)):
        """
        Initialize a pixel particle.
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            velocity_x (float): Initial x velocity
            velocity_y (float): Initial y velocity
            size (int): Size of the pixel in pixels
            color (tuple): RGB color tuple
        """
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.color = color
        # No longer using lifetime or alpha for fading
        
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
        
        # Apply gravity from settings
        self.velocity_y += settings.PIXEL_GRAVITY * dt * 60  # Scale by dt and target 60fps
        
        # Add slight drag/air resistance
        self.velocity_x *= 0.99
        
        # Check if particle has fallen off the bottom of the screen
        if self.y > screen_height:
            return False
            
        return True
        
    def draw(self, surface):
        """
        Draw the particle on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        # Draw a fully opaque pixel
        pygame.draw.rect(
            surface, 
            self.color, 
            pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        )


class PixelAnimation:
    """Manages multiple pixel particles for animations."""
    def __init__(self):
        """Initialize the pixel animation system."""
        self.particles = []
        self.last_random_spawn = 0
        self.random_spawn_interval = random.uniform(
            settings.PIXEL_MIN_INTERVAL, 
            settings.PIXEL_MAX_INTERVAL
        )
        self.button_hover_states = {}  # Track button hover states
        
    def spawn_particles(self, x, y, count=None):
        """
        Spawn a group of particles at the given position.
        
        Args:
            x (int): X-coordinate to spawn particles
            y (int): Y-coordinate to spawn particles
            count (int, optional): Number of particles to spawn. If None, uses PIXEL_CLICK_COUNT.
        """
        if count is None:
            count = settings.PIXEL_CLICK_COUNT
            
        for _ in range(count):
            # Random initial velocity in all directions
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 200)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Random size variation
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            
            # Pure white pixels
            color = (255, 255, 255)
            
            # Create and add the particle
            particle = PixelParticle(x, y, velocity_x, velocity_y, size, color)
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
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            size = random.randint(settings.PIXEL_MIN_SIZE, settings.PIXEL_MAX_SIZE)
            color = (255, 255, 255)
            
            particle = PixelParticle(x, y, velocity_x, velocity_y, size, color)
            self.particles.append(particle)
    
    def check_button_hover(self, buttons):
        """
        Check if buttons are being hovered and spawn particles if needed.
        
        Args:
            buttons (list): List of button objects to check
        """
        for button in buttons:
            button_id = id(button)  # Use object ID as unique identifier
            
            # If button is hovered now but wasn't before, spawn particles
            if button.hovered and not self.button_hover_states.get(button_id, False):
                self.spawn_button_hover_particles(button)
            
            # Update hover state
            self.button_hover_states[button_id] = button.hovered
    
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