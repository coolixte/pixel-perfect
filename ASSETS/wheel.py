import pygame
import os

def create_wheel():
    """
    Creates a white wheel image and saves it to the assets directory.
    The wheel is a simple white circle with a transparent background.
    """
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()
    
    # Set dimensions for the wheel
    size = 300
    
    # Create a transparent surface
    wheel = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw a white circle with a black outline
    pygame.draw.circle(wheel, (255, 255, 255, 220), (size//2, size//2), size//2 - 5)
    pygame.draw.circle(wheel, (0, 0, 0), (size//2, size//2), size//2 - 5, 2)
    
    # Make sure the assets directory exists
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Save the wheel image
    pygame.image.save(wheel, os.path.join("assets", "wheel.png"))
    print("Wheel image created successfully!")

if __name__ == "__main__":
    create_wheel() 