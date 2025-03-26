import pygame
import sys
import os
import math
import settings  # Import settings
from cursor_manager import CursorManager
from pixel_animation import PixelAnimation  # Import our animation system
from transition import TransitionAnimation  # Import our new transition animation system
from screen_flash import ScreenFlash  # Import our screen flash animation system
import game  # Import our game module

# Initialize pygame
pygame.init()

# Create the screen based on settings
if settings.BORDERLESS_WINDOW:
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.NOFRAME  # Remove window frame/border including title bar
    )
else:
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    
pygame.display.set_caption("Pixel Perfect")  # Set caption for taskbar

# Load assets
def load_image(filename):
    filepath = os.path.join(settings.ASSETS_DIR, filename)
    try:
        if not os.path.exists(filepath):
            print(f"Error: Image file '{filepath}' not found.")
            print(f"Please ensure '{filename}' is in the '{settings.ASSETS_DIR}' folder.")
            sys.exit()
        
        image = pygame.image.load(filepath)
        return image
    except pygame.error as e:
        print(f"Error loading image {filepath}: {e}")
        sys.exit()

# Load all required images
title_img = load_image("title.png")
play_btn = load_image("PlayBtn.png")
play_click = load_image("PlayClick.png")
opt_btn = load_image("OptBtn.png")
opt_click = load_image("OptClick.png")
exit_btn = load_image("ExitBtn.png")
exit_click = load_image("ExitClick.png")
border_img = load_image("fullborder.png")
name_img = load_image("name.png")  # Load the name image

# Button class
class Button:
    """Button class for interactive buttons."""
    def __init__(self, x, y, normal_img, clicked_img, scale=1.0):
        """
        Initialize a button.
        
        Args:
            x (int): X-coordinate of the button's center
            y (int): Y-coordinate of the button's center
            normal_img (Surface): Image for normal state
            clicked_img (Surface): Image for clicked state
            scale (float): Scale factor for the button size (default: 1.0)
        """
        # Scale images if needed
        if scale != 1.0:
            orig_size = normal_img.get_size()
            new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
            self.normal_img = pygame.transform.scale(normal_img, new_size)
            self.clicked_img = pygame.transform.scale(clicked_img, new_size)
        else:
            self.normal_img = normal_img
            self.clicked_img = clicked_img
            
        # Create a darkened version of the normal image for hover state
        self.hover_img = self.normal_img.copy()
        dark_surface = pygame.Surface(self.hover_img.get_size(), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, settings.HOVER_DARKNESS))  # Semi-transparent black
        self.hover_img.blit(dark_surface, (0, 0))
        
        self.image = self.normal_img
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        self.hovered = False
        
    def draw(self, surface):
        """
        Draw the button on the given surface.
        
        Args:
            surface (Surface): Surface to draw the button on
        """
        surface.blit(self.image, self.rect)
        
    def check_click(self, pos):
        """
        Check if the button is clicked.
        
        Args:
            pos (tuple): Mouse position (x, y)
            
        Returns:
            bool: True if button is clicked, False otherwise
        """
        if self.rect.collidepoint(pos):
            self.clicked = True
            self.image = self.clicked_img
            return True
        return False
    
    def check_hover(self, pos):
        """
        Check if the button is being hovered over.
        
        Args:
            pos (tuple): Mouse position (x, y)
        """
        if self.rect.collidepoint(pos):
            self.hovered = True
            if not self.clicked:  # Only show hover effect if not clicked
                self.image = self.hover_img
        else:
            self.hovered = False
            if not self.clicked:  # Only reset to normal if not clicked
                self.image = self.normal_img
    
    def release(self):
        """Release the button when mouse button is released."""
        if self.clicked:
            self.clicked = False
            if self.hovered:
                self.image = self.hover_img
            else:
                self.image = self.normal_img

# Create buttons using settings
# Center the buttons horizontally, position play button relative to the middle of the screen
play_button = Button(
    settings.SCREEN_WIDTH // 2, 
    settings.SCREEN_HEIGHT // 2 + settings.PLAY_BUTTON_Y_OFFSET, 
    play_btn, 
    play_click, 
    scale=settings.PLAY_BUTTON_SCALE
)

# Position options button below the play button with proper spacing
button_spacing = int(play_button.rect.height * settings.BUTTON_SPACING_MULTIPLIER)
options_button = Button(
    settings.SCREEN_WIDTH // 2, 
    settings.SCREEN_HEIGHT // 2 + settings.PLAY_BUTTON_Y_OFFSET + button_spacing, 
    opt_btn, 
    opt_click, 
    scale=settings.OPTIONS_BUTTON_SCALE
)

# Exit button positioning using settings (now relative to center like play button)
exit_button = Button(
    settings.SCREEN_WIDTH // 2 + settings.EXIT_BUTTON_X_OFFSET, 
    settings.SCREEN_HEIGHT // 2 + settings.EXIT_BUTTON_Y_OFFSET, 
    exit_btn, 
    exit_click, 
    scale=settings.EXIT_BUTTON_SCALE
)

# Border scaling and positioning using settings
original_border_size = border_img.get_size()
scaled_border_size = (
    int(original_border_size[0] * settings.BORDER_SCALE), 
    int(original_border_size[1] * settings.BORDER_SCALE)
)
scaled_border_img = pygame.transform.scale(border_img, scaled_border_size)
border_rect = scaled_border_img.get_rect(
    center=(settings.SCREEN_WIDTH // 2, (settings.SCREEN_HEIGHT // 2) + settings.BORDER_Y_OFFSET)
)

# Name image scaling and positioning using settings
original_name_size = name_img.get_size()
scaled_name_size = (
    int(original_name_size[0] * settings.NAME_SCALE), 
    int(original_name_size[1] * settings.NAME_SCALE)
)
scaled_name_img = pygame.transform.scale(name_img, scaled_name_size)
name_rect = scaled_name_img.get_rect(
    midbottom=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - settings.NAME_BOTTOM_PADDING)
)

# Main game loop
def main():
    """Main game function."""
    clock = pygame.time.Clock()
    running = True
    
    # Title expansion variables
    title_scale = settings.TITLE_SCALE
    title_hover = False
    
    # Initialize cursor manager
    cursor_manager = CursorManager()
    
    # Initialize pixel animation system
    pixel_animation = PixelAnimation()
    
    # Initialize transition animation system
    transition_animation = TransitionAnimation()
    
    # Initialize screen flash animation system
    screen_flash = ScreenFlash()
    
    # State tracking
    in_transition = False
    next_scene = None
    waiting_for_elements_exit = False
    
    # Track if mouse is inside the window
    mouse_in_window = False
    
    # For calculating delta time
    last_time = pygame.time.get_ticks() / 1000.0
    
    # Start with an initial screen flash when the game loads
    screen_flash.start()
    
    while running:
        # Calculate delta time
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is inside the window
                x, y = event.pos
                mouse_in_window = (0 <= x < settings.SCREEN_WIDTH and 0 <= y < settings.SCREEN_HEIGHT)
            
            
            elif event.type == pygame.ACTIVEEVENT:
                # Handle window focus/unfocus events
                if event.gain == 0 and event.state == 1:  # Mouse left the window
                    mouse_in_window = False
                elif event.gain == 1 and event.state == 1:  # Mouse entered the window
                    mouse_in_window = True
            
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Only check button clicks if not in transition
                    if not in_transition and not waiting_for_elements_exit:
                        # Spawn particles at click position
                        pixel_animation.spawn_particles(event.pos[0], event.pos[1])
                        
                        if play_button.check_click(event.pos):
                            # Start transition animation
                            ui_elements = [
                                (scaled_title, title_rect),
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "play")
                            in_transition = True
                            next_scene = "play"
                            
                        elif options_button.check_click(event.pos):
                            # Start transition animation
                            ui_elements = [
                                (scaled_title, title_rect),
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "options")
                            in_transition = True
                            next_scene = "options"
                            
                        elif exit_button.check_click(event.pos):
                            # Start transition animation
                            ui_elements = [
                                (scaled_title, title_rect),
                                (play_button.image, play_button.rect),
                                (options_button.image, options_button.rect),
                                (exit_button.image, exit_button.rect),
                                (scaled_name_img, name_rect)
                            ]
                            transition_animation.start(ui_elements, "exit")
                            in_transition = True
                            next_scene = "exit"
            
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    play_button.release()
                    options_button.release()
                    exit_button.release()
        
        # If in transition mode, update the transition animation
        if in_transition:
            still_active = transition_animation.update(dt)
            
            # If transition is no longer active
            if not still_active:
                # Check if all elements have exited the screen - immediately start the flash and scene change
                if transition_animation.all_elements_exited_screen():
                    # Start the screen flash immediately
                    screen_flash.start()
                    
                    # Handle scene change immediately during the flash
                    if next_scene == "play":
                        print("Transitioning to Play scene")
                        in_transition = False
                        # Launch the game immediately - we want game elements to appear during the white flash
                        game_result = game.start(screen, skip_entry_flash=True)  # Tell game to skip its own entry flash
                        if not game_result:
                            running = False  # Exit the game if game returns False
                        else:
                            # Game returned to menu - reset menu state
                            title_scale = settings.TITLE_SCALE
                            
                    elif next_scene == "options":
                        print("Transitioning to Options scene")
                        in_transition = False
                        # You would launch your options menu here
                        # import options
                        # options.start(skip_entry_flash=True)
                        
                    elif next_scene == "exit":
                        print("Exiting game")
                        # End the game immediately when white flash starts on exit button press
                        running = False
                        
                    next_scene = None
                    in_transition = False
        
        # Only check button hover states if not in transition
        if not in_transition and not waiting_for_elements_exit:
            play_button.check_hover(mouse_pos)
            options_button.check_hover(mouse_pos)
            exit_button.check_hover(mouse_pos)
            
            # Check button hover for pixel animations
            pixel_animation.check_button_hover([play_button, options_button, exit_button])
            
            # Calculate title hover effect (moves up and down slightly)
            time = pygame.time.get_ticks() / 1000  # Convert to seconds
            title_y_offset = math.sin(time * settings.TITLE_HOVER_SPEED) * settings.TITLE_HOVER_AMPLITUDE
            
            # Calculate title rect for hover detection
            base_title_rect = title_img.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.TITLE_Y_POSITION + title_y_offset)
            )
            
            # Check if mouse is hovering over title
            if base_title_rect.collidepoint(mouse_pos):
                title_hover = True
                # Gradually increase scale up to max
                title_scale = min(title_scale + settings.TITLE_SCALE_SPEED, settings.TITLE_MAX_SCALE)
            else:
                title_hover = False
                # Gradually decrease scale back to normal
                title_scale = max(title_scale - settings.TITLE_SCALE_SPEED, settings.TITLE_SCALE)
            
            # Scale the title image based on hover state
            scaled_title_width = int(title_img.get_width() * title_scale)
            scaled_title_height = int(title_img.get_height() * title_scale)
            scaled_title = pygame.transform.scale(title_img, (scaled_title_width, scaled_title_height))
            title_rect = scaled_title.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.TITLE_Y_POSITION + title_y_offset)
            )
        
        # Check if mouse is hovering over any buttons (excluding title)
        hovering_button = (
            play_button.hovered or 
            options_button.hovered or 
            exit_button.hovered
        )
        
        # Update cursor state with separate title hover parameter
        cursor_manager.update(
            mouse_pos, 
            pygame.mouse.get_pressed(), 
            hovering_button=hovering_button,
            hovering_title=title_hover,
            mouse_in_window=mouse_in_window
        )
        
        # Update pixel animation
        pixel_animation.update(dt, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        # Update screen flash animation
        screen_flash.update(dt)
        
        # Draw
        screen.fill(settings.BLACK)
        
        # Draw border as background (first layer) - always draw the border
        screen.blit(scaled_border_img, border_rect)
        
        # Draw UI elements or transition animation
        if in_transition:
            # If in transition, draw the border and transition elements
            transition_animation.draw(screen)
        else:
            # Draw regular UI if not in transition and not waiting for elements exit
            if not waiting_for_elements_exit:
                # Draw title with hover effect
                screen.blit(scaled_title, title_rect)
                
                # Draw buttons
                play_button.draw(screen)
                options_button.draw(screen)
                exit_button.draw(screen)
                
                # Draw name image in foreground (last layer)
                screen.blit(scaled_name_img, name_rect)
        
        # Draw pixel animation (should be after UI elements but before cursor)
        pixel_animation.draw(screen)
        
        # Draw the custom cursor (should be last)
        cursor_manager.draw(screen)
        
        # Draw screen flash (should be the very last thing to draw)
        screen_flash.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 