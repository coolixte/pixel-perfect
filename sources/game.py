import pygame
import sys
import os
import math
import random
import settings
from cursor_manager import CursorManager
from pixel_animation import PixelAnimation
from transition import TransitionAnimation

class GamePixel:
    """Represents a game pixel that moves towards the heart."""
    def __init__(self, x, y, angle, size, pixel_type="white"):
        """
        Initialize a game pixel.
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            angle (float): Movement angle in radians
            size (int): Size of the pixel
            pixel_type (str): Type of pixel - "white", "red", "green", or "orange"
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.type = pixel_type
        self.speed = settings.GAME_PIXEL_BASE_SPEED
        self.dead = False
        
        # Load the appropriate image based on type
        self.load_image()
        
    def load_image(self):
        """Load the appropriate image for this pixel type."""
        filename = ""
        if self.type == "white":
            filename = "whitepx.png"
        elif self.type == "red":
            filename = "redpx.png"
        elif self.type == "green":
            filename = "greenpx.png"
        elif self.type == "orange":
            filename = "orangepx.png"
        
        try:
            filepath = os.path.join(settings.ASSETS_DIR, filename)
            if not os.path.exists(filepath):
                print(f"Error: Pixel image '{filepath}' not found.")
                # Create a fallback colored square
                self.image = pygame.Surface((self.size, self.size))
                if self.type == "white":
                    self.image.fill((255, 255, 255))
                elif self.type == "red":
                    self.image.fill((255, 0, 0))
                elif self.type == "green":
                    self.image.fill((0, 255, 0))
                elif self.type == "orange":
                    self.image.fill((255, 165, 0))
            else:
                self.image = pygame.image.load(filepath)
                # Scale the image to the pixel size
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except pygame.error as e:
            print(f"Error loading pixel image {filename}: {e}")
            # Create a fallback colored square
            self.image = pygame.Surface((self.size, self.size))
            if self.type == "white":
                self.image.fill((255, 255, 255))
            elif self.type == "red":
                self.image.fill((255, 0, 0))
            elif self.type == "green":
                self.image.fill((0, 255, 0))
            elif self.type == "orange":
                self.image.fill((255, 165, 0))
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def update(self, dt, heart_x, heart_y):
        """
        Update the pixel position and check for heart proximity.
        
        Args:
            dt (float): Time delta in seconds
            heart_x (float): Heart x position
            heart_y (float): Heart y position
            
        Returns:
            bool: True if the pixel is still active, False if it should be removed
        """
        if self.dead:
            return False
            
        # Calculate direction vector to heart
        dx = heart_x - self.x
        dy = heart_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Increase speed if getting closer to heart
        if distance < settings.GAME_PIXEL_PROXIMITY_THRESHOLD:
            acceleration_factor = 1 + (settings.GAME_PIXEL_PROXIMITY_THRESHOLD - distance) / settings.GAME_PIXEL_PROXIMITY_THRESHOLD * settings.GAME_PIXEL_ACCELERATION
            current_speed = self.speed * acceleration_factor
        else:
            current_speed = self.speed
            
        # Move pixel towards heart
        self.x += dx * current_speed * dt
        self.y += dy * current_speed * dt
        
        # Update rectangle position
        self.rect.center = (self.x, self.y)
        
        return True
        
    def draw(self, surface):
        """
        Draw the pixel on the given surface.
        
        Args:
            surface (Surface): Pygame surface to draw on
        """
        surface.blit(self.image, self.rect)
        
    def check_collision(self, heart_rect):
        """
        Check if the pixel is colliding with the heart.
        
        Args:
            heart_rect (Rect): Pygame rectangle for the heart
            
        Returns:
            bool: True if collision, False otherwise
        """
        return self.rect.colliderect(heart_rect)
        
    def check_click(self, pos):
        """
        Check if the pixel was clicked.
        
        Args:
            pos (tuple): Mouse position (x, y)
            
        Returns:
            bool: True if clicked, False otherwise
        """
        return self.rect.collidepoint(pos)
        
    def mark_as_dead(self):
        """Mark the pixel as dead so it will be removed in the next update."""
        self.dead = True

class Game:
    """Main game class that manages the game state and logic."""
    def __init__(self, screen):
        """
        Initialize the game.
        
        Args:
            screen (Surface): Pygame surface to draw on
        """
        self.screen = screen
        self.running = True
        self.return_to_menu = False  # Flag to indicate whether to return to menu
        
        # Fade in state
        self.fading_in = True
        self.fade_timer = 0
        self.fade_duration = settings.FLASH_DURATION  # Reuse flash duration
        
        # Exit transition state
        self.exiting = False
        self.exit_timer = 0
        self.exit_fade_timer = 0
        self.exit_elements = []  # Elements to animate when exiting
        
        # Initialize pixel animation (for effects)
        self.pixel_animation = PixelAnimation(auto_spawn=False)  # Disable auto spawning for game scene
        
        # Initialize cursor manager
        self.cursor_manager = CursorManager()
        
        # Load exit button images
        try:
            self.exit_normal = pygame.image.load(os.path.join(settings.ASSETS_DIR, "ExitIcon.png"))
            self.exit_click = pygame.image.load(os.path.join(settings.ASSETS_DIR, "ExitIconClick.png"))
            
            # Scale button using settings
            scale = settings.GAME_EXIT_ICON_SCALE
            orig_size = self.exit_normal.get_size()
            new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
            self.exit_normal = pygame.transform.scale(self.exit_normal, new_size)
            self.exit_click = pygame.transform.scale(self.exit_click, new_size)
            
            # Position the button in the top-right corner using settings
            self.exit_rect = self.exit_normal.get_rect(
                topright=(settings.SCREEN_WIDTH - settings.GAME_EXIT_ICON_PADDING, 
                          settings.GAME_EXIT_ICON_PADDING)
            )
            self.exit_image = self.exit_normal
            self.exit_clicked = False
        except pygame.error as e:
            print(f"Error loading exit button images: {e}")
            self.exit_normal = None
            self.exit_click = None
        
        # Load border image from main menu
        try:
            self.border_img = pygame.image.load(os.path.join(settings.ASSETS_DIR, "fullborder.png"))
            original_border_size = self.border_img.get_size()
            scaled_border_size = (
                int(original_border_size[0] * settings.BORDER_SCALE), 
                int(original_border_size[1] * settings.BORDER_SCALE)
            )
            self.scaled_border_img = pygame.transform.scale(self.border_img, scaled_border_size)
            self.border_rect = self.scaled_border_img.get_rect(
                center=(settings.SCREEN_WIDTH // 2, (settings.SCREEN_HEIGHT // 2) + settings.BORDER_Y_OFFSET)
            )
        except pygame.error as e:
            print(f"Error loading border image: {e}")
            self.scaled_border_img = None
        
        # Load heart images
        self.heart_images = []
        for i in range(1, 6):  # heart_1.png to heart_5.png - now all with consistent naming
            filename = f"heart_{i}.png"
            try:
                image = pygame.image.load(os.path.join(settings.ASSETS_DIR, filename))
                # Using explicit heart size settings instead of just scaling
                scaled_size = (settings.HEART_WIDTH, settings.HEART_HEIGHT)
                self.heart_images.append(pygame.transform.scale(image, scaled_size))
            except pygame.error as e:
                print(f"Error loading heart image {filename}: {e}")
                # Fallback to previous heart if available
                if i > 1 and len(self.heart_images) > 0:
                    self.heart_images.append(self.heart_images[-1])
                else:
                    # Create a placeholder heart
                    placeholder = pygame.Surface((settings.HEART_WIDTH, settings.HEART_HEIGHT))
                    placeholder.fill((255, 0, 0))  # Red square as placeholder
                    self.heart_images.append(placeholder)
            
        # Set up heart
        self.lives = settings.INITIAL_LIVES
        self.heart_image = self.heart_images[0]  # Start with the first heart image
        self.heart_rect = self.heart_image.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        
        # Set up game pixels
        self.pixels = []
        self.last_spawn_time = 0
        self.spawn_interval = settings.GAME_PIXEL_SPAWN_INTERVAL
        self.pixel_base_speed = settings.GAME_PIXEL_BASE_SPEED
        self.difficulty_timer = 0
        
        # Mouse state
        self.mouse_in_window = True
        
    def spawn_pixel(self):
        """Spawn a new pixel at the edge of the screen."""
        # Randomly choose which side to spawn from (0=top, 1=right, 2=bottom, 3=left)
        side = random.randint(0, 3)
        
        # Calculate position based on the chosen side
        if side == 0:  # Top
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = 0
            angle = math.pi / 2  # Downward
        elif side == 1:  # Right
            x = settings.SCREEN_WIDTH
            y = random.randint(0, settings.SCREEN_HEIGHT)
            angle = math.pi  # Leftward
        elif side == 2:  # Bottom
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = settings.SCREEN_HEIGHT
            angle = 3 * math.pi / 2  # Upward
        else:  # Left
            x = 0
            y = random.randint(0, settings.SCREEN_HEIGHT)
            angle = 0  # Rightward
            
        # Randomly determine pixel type based on spawn odds
        roll = random.randint(1, 100)
        if roll <= settings.RED_PIXEL_ODDS:
            pixel_type = "red"
        elif roll <= settings.RED_PIXEL_ODDS + settings.GREEN_PIXEL_ODDS:
            pixel_type = "green"
        elif roll <= settings.RED_PIXEL_ODDS + settings.GREEN_PIXEL_ODDS + settings.ORANGE_PIXEL_ODDS:
            pixel_type = "orange"
        else:
            pixel_type = "white"
            
        # Randomly determine pixel size
        size = random.randint(settings.GAME_PIXEL_MIN_SIZE, settings.GAME_PIXEL_MAX_SIZE)
        
        # Create and add the pixel
        pixel = GamePixel(x, y, angle, size, pixel_type)
        pixel.speed = self.pixel_base_speed  # Set the current base speed
        self.pixels.append(pixel)
        
    def spawn_orange_splash(self, x, y):
        """
        Spawn white pixels when an orange pixel is clicked.
        
        Args:
            x (float): X position of the orange pixel
            y (float): Y position of the orange pixel
        """
        for _ in range(settings.ORANGE_SPLASH_COUNT):
            # Generate random angle
            angle = random.uniform(0, 2 * math.pi)
            
            # Calculate position at a random distance within splash radius
            distance = random.uniform(0, settings.ORANGE_SPLASH_RADIUS)
            spawn_x = x + math.cos(angle) * distance
            spawn_y = y + math.sin(angle) * distance
            
            # Clamp to screen boundaries
            spawn_x = max(0, min(spawn_x, settings.SCREEN_WIDTH))
            spawn_y = max(0, min(spawn_y, settings.SCREEN_HEIGHT))
            
            # Random size
            size = random.randint(settings.GAME_PIXEL_MIN_SIZE, settings.GAME_PIXEL_MAX_SIZE)
            
            # Create and add the white pixel
            pixel = GamePixel(spawn_x, spawn_y, angle, size, "white")
            pixel.speed = self.pixel_base_speed * 1.5  # Slightly faster than normal
            self.pixels.append(pixel)
    
    def lose_life(self):
        """Reduce player's lives by 1 and update heart image."""
        self.lives -= 1
        
        # Check for game over
        if self.lives <= 0:
            self.lives = 0
            print("Game Over!")
            # For now, we'll keep the game running
            
        # Update heart image (heart_1.png to heart_5.png based on damage)
        damage_level = 5 - self.lives
        if damage_level > 0 and damage_level <= 5:
            self.heart_image = self.heart_images[damage_level - 1]
            
    def apply_powerup(self):
        """Apply a random power-up effect."""
        # For now, just implement a simple powerup that removes some pixels
        powerup_type = random.choice(["clear_pixels", "slow_pixels", "extra_life"])
        
        if powerup_type == "clear_pixels":
            # Remove half of the white pixels
            white_pixels = [p for p in self.pixels if p.type == "white"]
            if white_pixels:
                for _ in range(len(white_pixels) // 2):
                    pixel = random.choice(white_pixels)
                    if pixel in self.pixels:
                        pixel.mark_as_dead()
                        white_pixels.remove(pixel)
                        
        elif powerup_type == "slow_pixels":
            # Slow down all pixels temporarily
            for pixel in self.pixels:
                pixel.speed *= 0.5
                
        elif powerup_type == "extra_life":
            # Add an extra life if not at max
            if self.lives < 5:
                self.lives += 1
                damage_level = 5 - self.lives
                self.heart_image = self.heart_images[damage_level - 1]
    
    def handle_events(self):
        """Handle game events."""
        # If in exiting state, don't process any events
        if self.exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
            return True
        
        # Normal event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is inside the window
                x, y = event.pos
                self.mouse_in_window = (0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT)
                
                # Check if mouse is hovering over exit button
                if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                    if not self.exit_clicked:
                        self.exit_image = self.exit_normal  # You can create a hover state if desired
                else:
                    if not self.exit_clicked:
                        self.exit_image = self.exit_normal
            
            elif event.type == pygame.ACTIVEEVENT:
                # Handle window focus/unfocus events
                if event.gain == 0 and event.state == 1:  # Mouse left the window
                    self.mouse_in_window = False
                elif event.gain == 1 and event.state == 1:  # Mouse entered the window
                    self.mouse_in_window = True
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if exit button was clicked
                    if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                        self.exit_clicked = True
                        self.exit_image = self.exit_click
                        # Don't return immediately, let the button click be visible
                    else:
                        # Check for pixel clicks
                        clicked_pixel = None
                        for pixel in self.pixels:
                            if pixel.check_click(event.pos):
                                clicked_pixel = pixel
                                break
                                
                        if clicked_pixel:
                            if clicked_pixel.type == "white":
                                # White pixel: destroy and create animation
                                clicked_pixel.mark_as_dead()
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y)
                                
                            elif clicked_pixel.type == "red":
                                # Red pixel: game over
                                print("Red pixel clicked! Game Over!")
                                self.lives = 0
                                self.heart_image = self.heart_images[4]  # Most damaged heart
                                
                            elif clicked_pixel.type == "green":
                                # Green pixel: power-up
                                clicked_pixel.mark_as_dead()
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y)
                                self.apply_powerup()
                                
                            elif clicked_pixel.type == "orange":
                                # Orange pixel: destroy and spawn white pixels
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y)
                                self.spawn_orange_splash(clicked_pixel.x, clicked_pixel.y)
                                clicked_pixel.mark_as_dead()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button release
                    # Check if exit button was clicked and released
                    if self.exit_clicked:
                        self.exit_clicked = False
                        self.exit_image = self.exit_normal
                        
                        # Check if mouse is still over the button
                        if hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(event.pos):
                            print("Returning to main menu")
                            self.start_exit_transition()
        
        return True
    
    def start_exit_transition(self):
        """Start the transition animation when exiting to the menu."""
        self.exiting = True
        self.exit_timer = 0
        self.exit_fade_timer = 0
        
        # Collect all visible elements for the transition
        self.exit_elements = []
        
        # Add heart
        if hasattr(self, 'heart_image') and self.heart_image:
            self.exit_elements.append((self.heart_image, self.heart_rect))
        
        # Add exit button
        if hasattr(self, 'exit_image') and self.exit_image:
            self.exit_elements.append((self.exit_image, self.exit_rect))
        
        # Add pixels as elements
        for pixel in self.pixels:
            if hasattr(pixel, 'image') and pixel.image and hasattr(pixel, 'rect') and pixel.rect:
                self.exit_elements.append((pixel.image, pixel.rect))
        
        # Create TransitionAnimation for the exit
        self.exit_transition = TransitionAnimation()
        self.exit_transition.start(self.exit_elements)
    
    def update(self, dt):
        """
        Update game state.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Handle exit transition
        if self.exiting:
            self.exit_timer += dt
            
            # First phase: elements fall off screen
            if self.exit_timer < settings.TRANSITION_DURATION:
                # Update transition animation
                self.exit_transition.update(dt)
                
                # Update cursor
                mouse_pos = pygame.mouse.get_pos()
                self.cursor_manager.update(
                    mouse_pos, 
                    pygame.mouse.get_pressed(), 
                    hovering_button=False,
                    hovering_title=False,
                    mouse_in_window=self.mouse_in_window
                )
                
            # Second phase: white flash
            elif self.exit_timer >= settings.TRANSITION_DURATION and self.exit_fade_timer < settings.FLASH_DURATION:
                self.exit_fade_timer += dt
                
                # After flash is done, return to menu
                if self.exit_fade_timer >= settings.FLASH_DURATION:
                    self.return_to_menu = True
                    self.running = False
                
            return
        
        # Handle fade-in effect
        if self.fading_in:
            self.fade_timer += dt
            if self.fade_timer >= self.fade_duration:
                self.fading_in = False
        
        # Update mouse cursor
        mouse_pos = pygame.mouse.get_pos()
        self.cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hasattr(self, 'exit_rect') and self.exit_rect and self.exit_rect.collidepoint(mouse_pos),
            hovering_title=False,
            mouse_in_window=self.mouse_in_window
        )
        
        # Don't update game state during fade-in
        if self.fading_in:
            # Only update animations during fade-in
            self.pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            return
        
        # Update pixel animation
        self.pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Increase difficulty over time
        self.difficulty_timer += dt
        self.spawn_interval = max(
            settings.GAME_PIXEL_SPAWN_INTERVAL - (self.difficulty_timer * settings.GAME_PIXEL_SPAWN_DECREASE_RATE),
            settings.GAME_PIXEL_SPAWN_MIN_INTERVAL
        )
        self.pixel_base_speed = settings.GAME_PIXEL_BASE_SPEED + (self.difficulty_timer * settings.GAME_PIXEL_SPEED_INCREASE_RATE)
        
        # Check if we should spawn a new pixel
        self.last_spawn_time += dt
        if self.last_spawn_time >= self.spawn_interval:
            self.spawn_pixel()
            self.last_spawn_time = 0
            
        # Update all pixels
        heart_x = self.heart_rect.centerx
        heart_y = self.heart_rect.centery
        
        pixels_to_remove = []
        for i, pixel in enumerate(self.pixels):
            if not pixel.update(dt, heart_x, heart_y):
                pixels_to_remove.append(i)
                continue
                
            # Check for collision with heart
            if pixel.check_collision(self.heart_rect):
                pixels_to_remove.append(i)
                
                if pixel.type == "white" or pixel.type == "orange":
                    # White or orange pixels damage the heart
                    self.lose_life()
                    self.pixel_animation.spawn_particles(pixel.x, pixel.y)
                elif pixel.type == "green":
                    # Green pixels give power-ups
                    self.apply_powerup()
                    self.pixel_animation.spawn_particles(pixel.x, pixel.y)
                    
        # Remove dead pixels (in reverse order to maintain correct indices)
        for i in sorted(pixels_to_remove, reverse=True):
            if i < len(self.pixels):
                del self.pixels[i]
    
    def draw(self):
        """Draw the game state."""
        # Clear the screen
        self.screen.fill(settings.BLACK)
        
        if self.exiting:
            # During exit transition, first phase: elements falling
            if self.exit_timer < settings.TRANSITION_DURATION:
                # Draw border as background
                if hasattr(self, 'scaled_border_img') and self.scaled_border_img is not None:
                    self.screen.blit(self.scaled_border_img, self.border_rect)
                    
                # Draw transition elements
                self.exit_transition.draw(self.screen)
                
                # Draw cursor
                self.cursor_manager.draw(self.screen)
                
            # Second phase: white flash
            elif self.exit_timer >= settings.TRANSITION_DURATION:
                # Calculate flash alpha
                flash_progress = min(self.exit_fade_timer / settings.FLASH_DURATION, 1.0)
                alpha = int(255 * (1.0 - flash_progress))  # Start at 255, fade to 0
                
                # Draw white flash overlay
                flash_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, alpha))
                self.screen.blit(flash_surface, (0, 0))
                
            # Update display
            pygame.display.flip()
            return
        
        # Normal game rendering
        # Draw border as background (first layer)
        if hasattr(self, 'scaled_border_img') and self.scaled_border_img is not None:
            self.screen.blit(self.scaled_border_img, self.border_rect)
        
        # Draw all game elements - they will be visible through the white flash
        # Draw all pixels
        for pixel in self.pixels:
            pixel.draw(self.screen)
            
        # Draw the heart
        self.screen.blit(self.heart_image, self.heart_rect)
        
        # Draw exit button
        if hasattr(self, 'exit_image') and self.exit_image is not None:
            self.screen.blit(self.exit_image, self.exit_rect)
        
        # Draw pixel animation effects
        self.pixel_animation.draw(self.screen)
        
        # Draw the cursor
        self.cursor_manager.draw(self.screen)
        
        # Draw fade-in effect
        if self.fading_in:
            fade_progress = 1.0 - min(self.fade_timer / self.fade_duration, 1.0)
            alpha = int(255 * fade_progress)
            fade_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((255, 255, 255, alpha))
            self.screen.blit(fade_surface, (0, 0))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Run the game loop."""
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            if not self.handle_events():
                break
                
            # Update game state
            self.update(dt)
            
            # Draw
            self.draw()
            
            # Cap frame rate
            clock.tick(settings.FPS)
            
        return self.running

def start(screen):
    """
    Start the game.
    
    Args:
        screen (Surface): Pygame surface to draw on
        
    Returns:
        bool: True if game should return to menu, False if should exit
    """
    game = Game(screen)
    result = game.run()
    
    # If game ended due to return_to_menu flag, always return True
    # This ensures we go back to the main menu rather than exiting
    if game.return_to_menu:
        return True
        
    return result 