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
        self.size = size  # Size is now just used for scaling
        self.type = pixel_type
        self.speed = settings.GAME_PIXEL_BASE_SPEED
        self.dead = False
        self.alpha = 0  # Start completely transparent
        self.fade_in_duration = 1.0  # Time in seconds to fade in completely
        self.fade_in_timer = 0.0  # Timer for fade-in effect
        
        # Add blinking state variables
        self.is_blinking = False
        self.blink_timer = 0.0
        self.blink_interval = 0.5  # Start with slower blinking
        self.blink_count = 0
        self.max_blinks = 4  # Number of blinks before popping
        self.is_visible = True  # Control visibility during blinking
        
        # Add a flag to track if this pixel will cause damage
        self.will_damage_heart = False
        self.will_apply_powerup = False
        
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
                base_size = 10  # Base size before applying the scaling factor
                scaled_size = int(base_size * (self.size / 10.0))  # Scale relative to base size
                self.image = pygame.Surface((scaled_size, scaled_size))
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
                # Get original size of the image
                original_size = self.image.get_size()
                # Calculate scale factor based on requested size
                scale_factor = self.size / max(original_size)
                # Scale the image
                scaled_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                self.image = pygame.transform.scale(self.image, scaled_size)
        except pygame.error as e:
            print(f"Error loading pixel image {filename}: {e}")
            # Create a fallback colored square with consistent sizing
            base_size = 10  # Base size before applying the scaling factor
            scaled_size = int(base_size * (self.size / 10.0))  # Scale relative to base size
            self.image = pygame.Surface((scaled_size, scaled_size))
            if self.type == "white":
                self.image.fill((255, 255, 255))
            elif self.type == "red":
                self.image.fill((255, 0, 0))
            elif self.type == "green":
                self.image.fill((0, 255, 0))
            elif self.type == "orange":
                self.image.fill((255, 165, 0))
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # After image is loaded and rect is set, create a copy for alpha manipulation
        if hasattr(self, 'image') and self.image:
            self.original_image = self.image.copy()
            # Create a transparent version for initial display
            self.image = self.original_image.copy()
            self.image.set_alpha(0)
        
    def start_blinking(self):
        """Start the blinking effect when colliding with heart base"""
        self.is_blinking = True
        self.blink_timer = 0.0
        self.blink_count = 0
        self.blink_interval = 0.5  # Start with slower blinking
        self.is_visible = True
        
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
        
        # Handle blinking state
        if self.is_blinking:
            self.blink_timer += dt
            
            if self.blink_timer >= self.blink_interval:
                # Toggle visibility
                self.is_visible = not self.is_visible
                
                # Apply alpha based on visibility
                if self.is_visible:
                    self.image = self.original_image.copy()
                    self.image.set_alpha(255)
                else:
                    self.image = self.original_image.copy()
                    self.image.set_alpha(0)
                
                # Reset timer and increase blink speed
                self.blink_timer = 0
                self.blink_count += 0.5  # Count half for each toggle
                
                # Make blinking faster as it progresses
                self.blink_interval = max(0.05, 0.5 - (0.1 * self.blink_count))
                
                # Check if we've blinked enough times
                if self.blink_count >= self.max_blinks:
                    self.dead = True
                    return False
            
            # Don't move while blinking
            return True
            
        # Update fade-in effect
        if self.fade_in_timer < self.fade_in_duration:
            self.fade_in_timer += dt
            # Calculate new alpha
            self.alpha = int(255 * min(self.fade_in_timer / self.fade_in_duration, 1.0))
            # Apply alpha to image
            self.image = self.original_image.copy()
            self.image.set_alpha(self.alpha)
        
        # Calculate direction vector to heart
        dx = heart_x - self.x
        dy = heart_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Exponential speed increase as pixel gets closer to heart
        # Use an exponential formula based on distance
        if distance < settings.GAME_PIXEL_PROXIMITY_THRESHOLD:
            # Calculate progress (0 = far away, 1 = at the heart)
            progress = 1.0 - distance / settings.GAME_PIXEL_PROXIMITY_THRESHOLD
            # Exponential acceleration (power of 2 for moderate effect, increase for stronger effect)
            acceleration_factor = 1.0 + (progress * progress * settings.GAME_PIXEL_ACCELERATION)
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
        # Only draw the pixel if it has some visibility
        if (not self.is_blinking) or (self.is_blinking and self.is_visible):
            if self.alpha > 0:
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
    def __init__(self, screen, skip_entry_flash=False):
        """
        Initialize the game.
        
        Args:
            screen (Surface): Pygame surface to draw on
            skip_entry_flash (bool): If True, skip the initial fade in effect
        """
        self.screen = screen
        self.running = True
        self.return_to_menu = False  # Flag to indicate whether to return to menu
        
        # Fade in state
        self.fading_in = skip_entry_flash
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
        
        # Load sounds
        self.load_sounds()
        
        # Start game background music
        self.start_background_music()
        
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
            
            # Create hover version with darkening effect
            self.exit_hover = self.exit_normal.copy()
            dark_surface = pygame.Surface(self.exit_hover.get_size(), pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Semi-transparent black
            self.exit_hover.blit(dark_surface, (0, 0))
            
            # Position the button using the absolute position settings
            self.exit_rect = self.exit_normal.get_rect(
                midbottom=(settings.GAME_EXIT_ICON_X_POSITION, settings.GAME_EXIT_ICON_Y_POSITION)
            )
            self.exit_image = self.exit_normal
            self.exit_clicked = False
            self.exit_hovered = False
        except pygame.error as e:
            print(f"Error loading exit button images: {e}")
            self.exit_normal = None
            self.exit_click = None
            self.exit_hover = None
        
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
                center=(settings.BORDER_X_POSITION, settings.BORDER_Y_POSITION)
            )
        except pygame.error as e:
            print(f"Error loading border image: {e}")
            self.scaled_border_img = None
        
        # Load heart base image
        try:
            self.base_img = pygame.image.load(os.path.join(settings.ASSETS_DIR, "base.png"))
            original_base_size = self.base_img.get_size()
            scaled_base_size = (
                int(original_base_size[0] * settings.HEART_BASE_SCALE), 
                int(original_base_size[1] * settings.HEART_BASE_SCALE)
            )
            self.scaled_base_img = pygame.transform.scale(self.base_img, scaled_base_size)
        except pygame.error as e:
            print(f"Error loading base image: {e}")
            self.scaled_base_img = None
        
        # Load heart images
        self.heart_images = []
        for i in range(1, 6):  # heart_1.png to heart_5.png - now all with consistent naming
            filename = f"heart_{i}.png"
            try:
                image = pygame.image.load(os.path.join(settings.ASSETS_DIR, filename))
                # Scale the image using the HEART_SCALE setting
                original_size = image.get_size()
                scaled_size = (
                    int(original_size[0] * settings.HEART_SCALE),
                    int(original_size[1] * settings.HEART_SCALE)
                )
                self.heart_images.append(pygame.transform.scale(image, scaled_size))
            except pygame.error as e:
                print(f"Error loading heart image {filename}: {e}")
                # Fallback to previous heart if available
                if i > 1 and len(self.heart_images) > 0:
                    self.heart_images.append(self.heart_images[-1])
                else:
                    # Create a placeholder heart (scaled appropriately)
                    placeholder_size = 100  # Base size before scaling
                    placeholder = pygame.Surface((placeholder_size, placeholder_size))
                    placeholder.fill((255, 0, 0))  # Red square as placeholder
                    scaled_size = (
                        int(placeholder_size * settings.HEART_SCALE),
                        int(placeholder_size * settings.HEART_SCALE)
                    )
                    self.heart_images.append(pygame.transform.scale(placeholder, scaled_size))
            
        # Set up heart
        self.lives = settings.INITIAL_LIVES
        self.heart_image = self.heart_images[0]  # Start with the first heart image
        self.heart_rect = self.heart_image.get_rect(
            center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
        )
        
        # Set up game pixels
        self.pixels = []
        self.last_spawn_time = 0
        self.spawn_interval = settings.GAME_PIXEL_SPAWN_INTERVAL
        self.pixel_base_speed = settings.GAME_PIXEL_BASE_SPEED
        self.difficulty_timer = 0
        
        # Mouse state
        self.mouse_in_window = True
        
    def load_sounds(self):
        """Load all game sound effects."""
        # Initialize sound objects to None
        self.explode_sound = None
        self.death_sound = None
        self.collect_sound = None
        
        try:
            # Load explode sound
            explode_path = os.path.join(settings.ASSETS_DIR, "explode.mp3")
            if os.path.exists(explode_path):
                self.explode_sound = pygame.mixer.Sound(explode_path)
                self.explode_sound.set_volume(0.4)
            else:
                print(f"Warning: Sound file '{explode_path}' not found.")
            
            # Load death sound
            death_path = os.path.join(settings.ASSETS_DIR, "death.mp3")
            if os.path.exists(death_path):
                self.death_sound = pygame.mixer.Sound(death_path)
                self.death_sound.set_volume(0.5)
            else:
                print(f"Warning: Sound file '{death_path}' not found.")
                
            # Load collect sound
            collect_path = os.path.join(settings.ASSETS_DIR, "collect.mp3")
            if os.path.exists(collect_path):
                self.collect_sound = pygame.mixer.Sound(collect_path)
                self.collect_sound.set_volume(0.4)
            else:
                print(f"Warning: Sound file '{collect_path}' not found.")
                
        except pygame.error as e:
            print(f"Error loading sound effects: {e}")
    
    def start_background_music(self):
        """Start the background music for the game."""
        try:
            # Stop any existing music
            pygame.mixer.music.stop()
            
            # Load and play game background music
            bg_music_path = os.path.join(settings.ASSETS_DIR, "game-song.mp3")
            if os.path.exists(bg_music_path):
                pygame.mixer.music.load(bg_music_path)
                pygame.mixer.music.set_volume(0.4)  # Set volume to 40%
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            else:
                print(f"Warning: Game background music file '{bg_music_path}' not found.")
        except pygame.error as e:
            print(f"Error loading game background music: {e}")
    
    def spawn_pixel(self):
        """Spawn a new pixel at the edge of the screen but inside the border."""
        # Calculate border boundaries
        if hasattr(self, 'border_rect') and self.border_rect:
            border_left = self.border_rect.left + 20  # Add padding
            border_right = self.border_rect.right - 20
            border_top = self.border_rect.top + 20
            border_bottom = self.border_rect.bottom - 20
        else:
            # Fallback to screen boundaries with padding
            border_left = 20
            border_right = settings.SCREEN_WIDTH - 20
            border_top = 20
            border_bottom = settings.SCREEN_HEIGHT - 20
        
        # Randomly choose which side to spawn from (0=top, 1=right, 2=bottom, 3=left)
        side = random.randint(0, 3)
        
        # Calculate position based on the chosen side but within border
        if side == 0:  # Top
            x = random.randint(border_left, border_right)
            y = border_top
            angle = math.pi / 2  # Downward
        elif side == 1:  # Right
            x = border_right
            y = random.randint(border_top, border_bottom)
            angle = math.pi  # Leftward
        elif side == 2:  # Bottom
            x = random.randint(border_left, border_right)
            y = border_bottom
            angle = 3 * math.pi / 2  # Upward
        else:  # Left
            x = border_left
            y = random.randint(border_top, border_bottom)
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
        Spawn exactly two white pixels away from heart when an orange pixel is clicked.
        
        Args:
            x (float): X position of the orange pixel
            y (float): Y position of the orange pixel
        """
        heart_x = settings.HEART_X_POSITION
        heart_y = settings.HEART_Y_POSITION
        
        # Calculate direction vector from heart to the orange pixel
        dx = x - heart_x
        dy = y - heart_y
        
        # Get the distance from heart to the orange pixel
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Only proceed if we have a valid direction (not at the heart)
        if distance > 0:
            # Normalize the direction vector
            dx /= distance
            dy /= distance
            
            # Always spawn exactly 2 white pixels
            for i in range(2):
                # Vary the angle slightly for each pixel
                if i == 0:
                    angle_offset = random.uniform(-math.pi/6, 0)  # -30 to 0 degrees
                else:
                    angle_offset = random.uniform(0, math.pi/6)  # 0 to 30 degrees
                    
                angle = math.atan2(dy, dx) + angle_offset
                dir_x = math.cos(angle)
                dir_y = math.sin(angle)
                
                # Calculate spawn position farther away from the heart than orange pixel
                additional_distance = settings.ORANGE_SPLASH_RADIUS * 1.5  # Make sure they're far away
                spawn_x = x + dir_x * additional_distance
                spawn_y = y + dir_y * additional_distance
                
                # Clamp to screen boundaries while ensuring they're inside the border
                if hasattr(self, 'border_rect') and self.border_rect:
                    border_left = self.border_rect.left + 20
                    border_right = self.border_rect.right - 20
                    border_top = self.border_rect.top + 20
                    border_bottom = self.border_rect.bottom - 20
                else:
                    border_left = 20
                    border_right = settings.SCREEN_WIDTH - 20
                    border_top = 20
                    border_bottom = settings.SCREEN_HEIGHT - 20
                    
                spawn_x = max(border_left, min(spawn_x, border_right))
                spawn_y = max(border_top, min(spawn_y, border_bottom))
                
                # Random size
                size = random.randint(settings.GAME_PIXEL_MIN_SIZE, settings.GAME_PIXEL_MAX_SIZE)
                
                # Create and add white pixel (not orange)
                pixel = GamePixel(spawn_x, spawn_y, angle, size, "white")
                
                # Make these white pixels slightly slower than normal to give player time to react
                pixel.speed = self.pixel_base_speed * 0.6
                self.pixels.append(pixel)
    
    def lose_life(self):
        """Reduce player's lives by 1 and update heart image."""
        self.lives -= 1
        
        # Play death sound when losing a life
        if hasattr(self, 'death_sound') and self.death_sound:
            self.death_sound.play()
        
        # Create red pixel animation on the heart when losing a life
        for _ in range(15):  # Create 15 particles
            # Random positions around the heart center
            particle_x = settings.HEART_X_POSITION + random.uniform(-20, 20)
            particle_y = settings.HEART_Y_POSITION + random.uniform(-20, 20)
            self.pixel_animation.spawn_particles(particle_x, particle_y, color="red")
        
        # Check for game over
        if self.lives <= 0:
            self.lives = 0
            print("Game Over!")
            # For now, we'll keep the game running
            
        # Update heart image (heart_1.png to heart_5.png based on damage)
        damage_level = 5 - self.lives
        if damage_level >= 0 and damage_level < 5:
            self.heart_image = self.heart_images[damage_level]
        # When all lives are lost, ensure we show the most damaged heart
        elif damage_level >= 5:
            self.heart_image = self.heart_images[4]  # Last heart image (most damaged)
    
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
                    self.exit_hovered = True
                    if not self.exit_clicked:
                        self.exit_image = self.exit_hover
                else:
                    self.exit_hovered = False
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
                    # Play explode sound for any click
                    if hasattr(self, 'explode_sound') and self.explode_sound:
                        self.explode_sound.play()
                    
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
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="white")
                                
                            elif clicked_pixel.type == "red":
                                # Red pixel: game over
                                print("Red pixel clicked! Game Over!")
                                self.lives = 0
                                self.heart_image = self.heart_images[4]  # Most damaged heart
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="red")
                                
                            elif clicked_pixel.type == "green":
                                # Green pixel: power-up and pop all white and orange pixels
                                clicked_pixel.mark_as_dead()
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="green")
                                
                                # Play collect sound for green pixel
                                if hasattr(self, 'collect_sound') and self.collect_sound:
                                    self.collect_sound.play()
                                
                                self.apply_powerup()
                                
                                # Pop all white and orange pixels
                                for other_pixel in list(self.pixels):  # Make a copy of the list to iterate safely
                                    if other_pixel.type in ["white", "orange"] and other_pixel != clicked_pixel:
                                        self.pixel_animation.spawn_particles(other_pixel.x, other_pixel.y, color=other_pixel.type)
                                        other_pixel.mark_as_dead()
                            
                            elif clicked_pixel.type == "orange":
                                # Orange pixel: destroy and spawn white pixels in opposite direction from heart
                                self.pixel_animation.spawn_particles(clicked_pixel.x, clicked_pixel.y, color="orange")
                                self.spawn_orange_splash(clicked_pixel.x, clicked_pixel.y)
                                clicked_pixel.mark_as_dead()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button release
                    # Check if exit button was clicked and released
                    if self.exit_clicked:
                        self.exit_clicked = False
                        if self.exit_hovered:
                            self.exit_image = self.exit_hover
                        else:
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
        
        # Fade out game music
        try:
            pygame.mixer.music.fadeout(500)  # Fade out over 500ms
        except pygame.error as e:
            print(f"Error fading out game music: {e}")
        
        # Collect all visible elements for the transition
        self.exit_elements = []
        
        # Add base (if it exists)
        if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
            base_rect = self.scaled_base_img.get_rect(
                center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
            )
            self.exit_elements.append((self.scaled_base_img, base_rect))
        
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
                still_active = self.exit_transition.update(dt)
                
                # If transition is complete, immediately start the white flash
                if not still_active and self.exit_transition.all_elements_exited_screen():
                    # Skip to the flash phase
                    self.exit_timer = settings.TRANSITION_DURATION
                    self.exit_fade_timer = 0
                
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
                
                # Return to menu immediately when the flash starts
                if self.exit_fade_timer < 0.05:  # Just started the flash
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
        heart_x = settings.HEART_X_POSITION
        heart_y = settings.HEART_Y_POSITION
        
        pixels_to_remove = []
        for i, pixel in enumerate(self.pixels):
            if not pixel.update(dt, heart_x, heart_y):
                pixels_to_remove.append(i)
                continue
                
            # Define base rect for collision detection
            if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
                base_rect = self.scaled_base_img.get_rect(
                    center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
                )
                collision_rect = base_rect
            else:
                collision_rect = self.heart_rect
            
            # Check for collision with heart/base
            if pixel.check_collision(collision_rect) and not pixel.is_blinking:
                # Start blinking effect instead of removing immediately
                pixel.start_blinking()
                
                if pixel.type == "white" or pixel.type == "orange":
                    # Mark pixel as one that will damage the heart when it finishes blinking
                    pixel.will_damage_heart = True
                elif pixel.type == "green":
                    # Mark pixel as one that will apply a powerup when it finishes blinking
                    pixel.will_apply_powerup = True
                    
        # Remove dead pixels (in reverse order to maintain correct indices)
        for i in sorted(pixels_to_remove, reverse=True):
            if i < len(self.pixels):
                # Get the pixel before removing it
                pixel = self.pixels[i]
                
                # Check if this pixel is blinking and just finished its animation
                if pixel.is_blinking:
                    # Create particle effect for the explosion
                    self.pixel_animation.spawn_particles(pixel.x, pixel.y, color=pixel.type)
                    
                    # Play explode sound for pixel popping
                    if hasattr(self, 'explode_sound') and self.explode_sound:
                        self.explode_sound.play()
                    
                    # Apply effects based on pixel type
                    if pixel.will_damage_heart:
                        # Now is when we lose a life and show the red animation
                        self.lose_life()
                    elif pixel.will_apply_powerup:
                        # Apply powerup when green pixel finishes blinking
                        self.apply_powerup()
                        # Play collect sound
                        if hasattr(self, 'collect_sound') and self.collect_sound:
                            self.collect_sound.play()
                
                # Now remove the pixel
                del self.pixels[i]
    
    def draw(self):
        """Draw the game state."""
        # Clear the screen
        self.screen.fill(settings.BLACK)
        
        # Always draw the border as background first
        if hasattr(self, 'scaled_border_img') and self.scaled_border_img is not None:
            self.screen.blit(self.scaled_border_img, self.border_rect)
        
        if self.exiting:
            # During exit transition, first phase: elements falling
            if self.exit_timer < settings.TRANSITION_DURATION:
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
        # Draw all game elements - they will be visible through the white flash
        # Draw all pixels
        for pixel in self.pixels:
            pixel.draw(self.screen)
        
        # First draw the base image under the heart
        if hasattr(self, 'scaled_base_img') and self.scaled_base_img is not None:
            base_rect = self.scaled_base_img.get_rect(
                center=(settings.HEART_X_POSITION, settings.HEART_Y_POSITION)
            )
            self.screen.blit(self.scaled_base_img, base_rect)
        
        # Then draw the heart on top of the base
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

def start(screen, skip_entry_flash=False):
    """
    Start the game.
    
    Args:
        screen (Surface): Pygame surface to draw on
        skip_entry_flash (bool): If True, skip the initial fade in effect
        
    Returns:
        bool: True if game should return to menu, False if should exit
    """
    # Always create a new Game instance to ensure fresh settings
    game = Game(screen, skip_entry_flash)
    result = game.run()
    
    # If game ended due to return_to_menu flag, always return True
    # This ensures we go back to the main menu rather than exiting
    if game.return_to_menu:
        return True
        
    return result 