import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS
from cursor_manager import CursorManager

def example_integration():
    """
    Example showing how to integrate the custom cursor manager into a pygame application.
    
    This demonstrates:
    1. Initializing the cursor manager
    2. Updating cursor state based on game events
    3. Drawing the custom cursor
    """
    # Initialize pygame
    pygame.init()
    
    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Custom Cursor Example")
    
    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Initialize cursor manager
    cursor_manager = CursorManager()
    
    # Example button for demonstration
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30, 200, 60)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        # Get mouse state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        # Check if mouse is hovering over the button
        hovering_button = button_rect.collidepoint(mouse_pos)
        
        # Update cursor state
        cursor_manager.update(mouse_pos, mouse_pressed, hovering_button)
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw example button
        button_color = (100, 100, 255) if hovering_button else (50, 50, 200)
        pygame.draw.rect(screen, button_color, button_rect)
        
        # Draw custom cursor (should be the last thing drawn)
        cursor_manager.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    example_integration() 