import pygame
import random
import math
import settings

class TransitionElement:
    """Represents a UI element with physics during transition animation."""
    def __init__(self, image, rect, reverse=False):
        """
        Initialize a transition element with physics properties.
        
        Args:
            image (Surface): The image of the UI element
            rect (Rect): The rectangle defining the element's position and size
            reverse (bool): If True, element will enter the screen rather than exit
        """
        self.image = image.copy()  # Create a copy of the image to avoid modifying the original
        self.original_image = image.copy()  # Keep the original for rotation
        self.rect = rect.copy()
        self.reverse = reverse
        
        if reverse:
            # For reverse transitions, start off-screen
            self.x = random.randint(-100, settings.SCREEN_WIDTH + 100)
            self.y = settings.SCREEN_HEIGHT + 100  # Start below the screen
            
            # Final destination will be the original rect center
            self.dest_x = rect.centerx
            self.dest_y = rect.centery
        else:
            # Normal transition (elements fall off screen)
            self.x = rect.centerx
            self.y = rect.centery
        
        # Generate random angle between min and max settings
        angle_rad = math.radians(random.uniform(
            settings.TRANSITION_MIN_ANGLE, 
            settings.TRANSITION_MAX_ANGLE
        ))
        
        # Generate random speed
        speed = random.uniform(
            settings.TRANSITION_MIN_SPEED,
            settings.TRANSITION_MAX_SPEED
        )
        
        # Calculate initial velocity based on angle and speed
        if reverse:
            # For reverse, velocity points toward final destination
            self.velocity_x = 0  # Will be set in update
            self.velocity_y = 0  # Will be set in update
        else:
            # Normal transition
            self.velocity_x = math.sin(angle_rad) * speed
            self.velocity_y = math.cos(angle_rad) * speed  # Start with downward velocity
        
        # Rotation
        self.angle = 0  # Current rotation angle
        self.rotation_speed = random.uniform(-1, 1) * settings.TRANSITION_ROTATION_SPEED
        
        # Animation progress
        self.elapsed_time = 0
    
    def update(self, dt):
        """
        Update the element's position and rotation based on physics.
        
        Args:
            dt (float): Time delta in seconds
            
        Returns:
            bool: True if the animation should continue, False if complete
        """
        self.elapsed_time += dt
        
        if self.reverse:
            # Reverse transition - moving element onto screen
            # Use a easing function to move elements to their destinations
            progress = min(self.elapsed_time / 1.0, 1.0)  # 1.0 second duration
            
            # Ease-out function
            ease = 1 - (1 - progress) * (1 - progress)
            
            # Move toward destination
            self.x = self.x + (self.dest_x - self.x) * ease * 5 * dt
            self.y = self.y + (self.dest_y - self.y) * ease * 5 * dt
            
            # Reduce rotation as we approach destination
            self.rotation_speed *= 0.95
            
            # Check if we've reached the destination
            distance = math.sqrt((self.x - self.dest_x)**2 + (self.y - self.dest_y)**2)
            if distance < 5 and self.elapsed_time > 1.0:
                return False  # Animation complete
                
        else:
            # Normal transition - elements fall off screen
            # Update position based on velocity
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # Apply gravity
            self.velocity_y += settings.TRANSITION_GRAVITY * dt * 60  # Scale by dt and target 60fps
            
            # Check if element has fallen off the bottom of the screen
            if self.y - self.rect.height > settings.SCREEN_HEIGHT:
                return False
        
        # Update rotation
        self.angle += self.rotation_speed * dt * 60
        
        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Update rect position while keeping the center
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        return True
    
    def draw(self, surface):
        """
        Draw the element on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        surface.blit(self.image, self.rect)


class TransitionAnimation:
    """Manages the transition animation for UI elements."""
    def __init__(self):
        """Initialize the transition animation system."""
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
        Start the transition animation with the provided UI elements.
        
        Args:
            ui_elements (list): List of (image, rect) tuples for UI elements
            target_scene (str, optional): The scene to transition to after animation
            reverse (bool): If True, elements enter screen rather than exit
        """
        self.elements = []
        self.reverse = reverse
        self.target_scene = target_scene
        
        # Create the transition elements
        for image, rect in ui_elements:
            # Skip None elements or empty rects
            if image is None or rect is None:
                continue
            self.elements.append(TransitionElement(image, rect, reverse))
        
        self.is_active = True
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.all_elements_exited = False
        self.initial_element_count = len(self.elements)
        
    def update(self, dt):
        """
        Update all transition elements.
        
        Args:
            dt (float): Time delta in seconds
            
        Returns:
            bool: True if animation is still active, False if completed
        """
        if not self.is_active:
            return False
            
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - self.start_time
        
        # Check if animation duration has passed (safety timeout)
        if elapsed_time >= self.duration:
            self.is_active = False
            self.elements = []
            return False
        
        # Update each element and remove those that have fallen off screen
        self.elements = [elem for elem in self.elements if elem.update(dt)]
        
        # If all elements are gone, end animation early and set the flag
        if not self.elements and self.initial_element_count > 0:
            self.all_elements_exited = True
            self.is_active = False
            return False
            
        return True
        
    def draw(self, surface):
        """
        Draw all transition elements on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        if self.is_active:
            for element in self.elements:
                element.draw(surface)
                
    def is_finished(self):
        """
        Check if the transition animation has finished.
        
        Returns:
            bool: True if animation is finished, False otherwise
        """
        return not self.is_active
        
    def all_elements_exited_screen(self):
        """
        Check if all UI elements have exited the screen.
        
        Returns:
            bool: True if all elements have exited the screen, False otherwise
        """
        return self.all_elements_exited 