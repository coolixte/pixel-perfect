import pygame
import sys
import os
import math
import settings  # Import settings

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
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if play_button.check_click(event.pos):
                        print("Play button clicked!")
                        # Add game start logic here
                    elif options_button.check_click(event.pos):
                        print("Options button clicked!")
                        # Add options menu logic here
                    elif exit_button.check_click(event.pos):
                        print("Exit button clicked!")
                        running = False  # Exit the game
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    play_button.release()
                    options_button.release()
                    exit_button.release()
        
        # Check button hover states
        play_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        
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
        
        # Draw
        screen.fill(settings.BLACK)
        
        # Draw border as background (first layer)
        screen.blit(scaled_border_img, border_rect)
        
        # Draw title with hover effect
        screen.blit(scaled_title, title_rect)
        
        # Draw buttons
        play_button.draw(screen)
        options_button.draw(screen)
        exit_button.draw(screen)
        
        # Draw name image in foreground (last layer)
        screen.blit(scaled_name_img, name_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 