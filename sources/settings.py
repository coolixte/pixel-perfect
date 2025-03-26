# Game Settings

# Screen dimensions
SCREEN_WIDTH = 940
SCREEN_HEIGHT = 605

# Window settings
BORDERLESS_WINDOW = True  # Set to True for borderless window, False for normal window

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Assets directory (supports running from both root and sources directory)
import os
ASSETS_DIR = "../assets" if os.path.basename(os.getcwd()) == "sources" else "assets"

# Position settings - all positions are now x,y offsets from origin (0,0)
# Title settings
TITLE_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
TITLE_Y_POSITION = 140
TITLE_HOVER_SPEED = 3  # Speed of the hover animation
TITLE_HOVER_AMPLITUDE = 10  # How far the title moves up and down
TITLE_SCALE = 1.0  # Default scale
TITLE_MAX_SCALE = 1.15  # Maximum scale when hovered
TITLE_SCALE_SPEED = 0.01  # How fast the title scales up/down

# Play button settings
PLAY_BUTTON_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
PLAY_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 - 20  # Slightly above center
PLAY_BUTTON_SCALE = 0.40

# Options button settings
OPTIONS_BUTTON_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
OPTIONS_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 + 90  # Below play button
OPTIONS_BUTTON_SCALE = 0.40
BUTTON_SPACING_MULTIPLIER = 1.2  # Spacing between buttons as a multiplier of button height

# Exit button settings
EXIT_BUTTON_X_POSITION = SCREEN_WIDTH // 2 - 3  # Slightly left of center
EXIT_BUTTON_Y_POSITION = SCREEN_HEIGHT // 2 + 200  # Far below center
EXIT_BUTTON_SCALE = 0.18

# Border settings
BORDER_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
BORDER_Y_POSITION = SCREEN_HEIGHT // 2  # Centered vertically
BORDER_SCALE = 2.9

# Name image settings
NAME_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
NAME_Y_POSITION = SCREEN_HEIGHT - 30  # Bottom of the screen with padding
NAME_SCALE = 0.5

# Game exit button settings
GAME_EXIT_ICON_X_POSITION = SCREEN_WIDTH // 2  # Centered horizontally
GAME_EXIT_ICON_Y_POSITION = SCREEN_HEIGHT - 30  # Bottom with padding
GAME_EXIT_ICON_SCALE = 0.125

# Heart settings
HEART_X_POSITION = SCREEN_WIDTH // 2  # Center of screen horizontally
HEART_Y_POSITION = SCREEN_HEIGHT // 2  # Center of screen vertically
HEART_SCALE = 0.1  # Scale for heart image
HEART_BASE_SCALE = 1.3  # Scale for the base under the heart
INITIAL_LIVES = 5  # Player starts with 5 lives

# Cursor settings
CURSOR_NORMAL = "cursor_normal.png"
CURSOR_HOVER = "cursor_hovering_selectable_item.png"
CURSOR_CLICK = "cursor_click.png"
CURSOR_ZOOM = "cursor_zoom.png"  # New zoom cursor for title hover
CURSOR_VISIBLE = False  # Hide the default system cursor

# Cursor scaling settings
CURSOR_NORMAL_SCALE = 0.7
CURSOR_HOVER_SCALE = 0.7
CURSOR_CLICK_SCALE = 0.7
CURSOR_ZOOM_SCALE = 0.7

# Button hover effect
HOVER_DARKNESS = 50  # 0-255, higher is darker

# Animation settings
FPS = 60  # Frames per second

# Pixel animation settings
PIXEL_MIN_SIZE = 2
PIXEL_MAX_SIZE = 4
PIXEL_MIN_COUNT = 5
PIXEL_MAX_COUNT = 15
PIXEL_MIN_INTERVAL = 1.0  # Minimum seconds between random animations
PIXEL_MAX_INTERVAL = 5.0  # Maximum seconds between random animations
PIXEL_CLICK_COUNT = 10
PIXEL_BUTTON_HOVER_COUNT = 5  # Number of particles to spawn when hovering over buttons
PIXEL_GRAVITY = 2.0      # Gravity strength (0 = no gravity, higher values = stronger gravity)

# Transition animation settings
TRANSITION_GRAVITY = 8.0       # Gravity strength for transition animation (increased for faster falling)
TRANSITION_MIN_ANGLE = -45     # Minimum angle in degrees for transition elements (wider angle range)
TRANSITION_MAX_ANGLE = 45      # Maximum angle in degrees for transition elements (wider angle range)
TRANSITION_MIN_SPEED = 100     # Minimum initial speed for transition elements (increased)
TRANSITION_MAX_SPEED = 250     # Maximum initial speed for transition elements (increased)
TRANSITION_ROTATION_SPEED = 3.0  # Rotation speed factor for transition elements (increased)
TRANSITION_DURATION = 3.0      # Maximum duration of transition animation in seconds (safety timeout)

# Screen flash animation settings
FLASH_DURATION = 1          # Duration of screen flash animation in seconds
FLASH_FADE_SPEED = 1.5

# Game Pixel settings
GAME_PIXEL_MIN_SIZE = 10   # Minimum size of game pixels
GAME_PIXEL_MAX_SIZE = 35  # Maximum size of game pixels
GAME_PIXEL_BASE_SPEED = 15  # Base speed of pixels
GAME_PIXEL_ACCELERATION = 3.0  # Exponential acceleration factor (increased for more dramatic effect)
GAME_PIXEL_PROXIMITY_THRESHOLD = 400  # Distance at which pixels start accelerating

# Spawn settings
GAME_PIXEL_SPAWN_INTERVAL = 3.0  # Initial seconds between spawns
GAME_PIXEL_SPAWN_DECREASE_RATE = 0.015  # How much spawn interval decreases per second
GAME_PIXEL_SPAWN_MIN_INTERVAL = 0.5  # Minimum spawn interval
GAME_PIXEL_SPEED_INCREASE_RATE = 0.025  # How much base speed increases per second

# Special pixel spawn odds (percentage)
RED_PIXEL_ODDS = 10  # 10% chance for a red pixel
GREEN_PIXEL_ODDS = 2.5  # 15% chance for a green pixel
ORANGE_PIXEL_ODDS = 10  # 20% chance for an orange pixel

# Orange pixel settings
ORANGE_SPLASH_RADIUS = 150  # Radius in which orange pixel spawns white pixels
ORANGE_SPLASH_COUNT = 3  # Number of white pixels spawned by orange pixel

# Sound settings
MUSIC_VOLUME = 0.4  # Volume for background music (0.0 to 1.0)
SFX_VOLUME = 0.5    # Volume for sound effects (0.0 to 1.0)
EXPLOSION_VOLUME = 0.4  # Volume for explosion sounds
COLLECT_VOLUME = 0.5    # Volume for collect sounds
DEATH_VOLUME = 0.6      # Volume for death sounds
GAME_OVER_VOLUME = 0.7  # Volume for game over sound (slightly louder than death sound)
