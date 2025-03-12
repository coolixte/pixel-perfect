import pygame
import sys
import os
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Perfect")

# Define assets directory
assets_dir = "assets"

# Load assets
def load_image(filename):
    filepath = os.path.join(assets_dir, filename)
    try:
        if not os.path.exists(filepath):
            print(f"Error: Image file '{filepath}' not found.")
            print(f"Please ensure '{filename}' is in the '{assets_dir}' folder.")
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
            
        self.image = self.normal_img
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        self.action_time = 0
        
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
            self.action_time = pygame.time.get_ticks()
            return True
        return False
    
    def update(self):
        """Update button state."""
        # Reset button after 200ms
        if self.clicked and pygame.time.get_ticks() - self.action_time > 200:
            self.clicked = False
            self.image = self.normal_img

# Create buttons with scaling (0.7 = 70% of original size)
button_scale = 0.40
# Center the buttons horizontally, position play button lower than the middle of the screen
play_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, play_btn, play_click, scale=button_scale)
# Position options button below the play button with proper spacing
button_spacing = int(play_button.rect.height * 1.2)  # 20% spacing between buttons
options_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + button_spacing, opt_btn, opt_click, scale=button_scale)

# Main game loop
def main():
    """Main game function."""
    clock = pygame.time.Clock()
    running = True
    
    while running:
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
        
        # Update
        play_button.update()
        options_button.update()
        
        # Calculate title hover effect (moves up and down slightly)
        time = pygame.time.get_ticks() / 1000  # Convert to seconds
        title_y_offset = math.sin(time * 3) * 10  # Sine wave for smooth up/down motion
        
        # Draw
        screen.fill(BLACK)
        
        # Draw title with hover effect
        title_rect = title_img.get_rect(center=(SCREEN_WIDTH // 2, 150 + title_y_offset))
        screen.blit(title_img, title_rect)
        
        # Draw buttons
        play_button.draw(screen)
        options_button.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 