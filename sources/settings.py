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

# Title settings
TITLE_Y_POSITION = 140
TITLE_HOVER_SPEED = 3  # Speed of the hover animation
TITLE_HOVER_AMPLITUDE = 10  # How far the title moves up and down
TITLE_SCALE = 1.0  # Default scale
TITLE_MAX_SCALE = 1.15  # Maximum scale when hovered
TITLE_SCALE_SPEED = 0.01  # How fast the title scales up/down

# Play button settings
PLAY_BUTTON_SCALE = 0.40
PLAY_BUTTON_Y_OFFSET = -20  # Offset from center of screen

# Options button settings
OPTIONS_BUTTON_SCALE = 0.40
BUTTON_SPACING_MULTIPLIER = 1.2  # Spacing between buttons as a multiplier of button height

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

# Exit button settings
EXIT_BUTTON_SCALE = 0.18
EXIT_BUTTON_X_OFFSET = -3  # X offset from center of screen (positive = right)
EXIT_BUTTON_Y_OFFSET = 200  # Y offset from center of screen (negative = up)

# Border settings
BORDER_SCALE = 2.9
BORDER_Y_OFFSET = 0  # Vertical offset from center

# Name image settings
NAME_SCALE = 0.5
NAME_BOTTOM_PADDING = 30  # Padding from the bottom of the screen

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

# Game settings
# Heart settings
HEART_SCALE = 0.5
HEART_WIDTH = 80  # Width of the heart in pixels
HEART_HEIGHT = 80  # Height of the heart in pixels
INITIAL_LIVES = 5  # Player starts with 5 lives

# Game Pixel settings
GAME_PIXEL_MIN_SIZE = 5   # Minimum size of game pixels
GAME_PIXEL_MAX_SIZE = 15  # Maximum size of game pixels
GAME_PIXEL_BASE_SPEED = 50  # Base speed of pixels
GAME_PIXEL_ACCELERATION = 1.2  # How much pixels accelerate as they get closer to heart
GAME_PIXEL_PROXIMITY_THRESHOLD = 200  # Distance at which pixels start accelerating

# Spawn settings
GAME_PIXEL_SPAWN_INTERVAL = 2.0  # Initial seconds between spawns
GAME_PIXEL_SPAWN_DECREASE_RATE = 0.05  # How much spawn interval decreases per second
GAME_PIXEL_SPAWN_MIN_INTERVAL = 0.5  # Minimum spawn interval
GAME_PIXEL_SPEED_INCREASE_RATE = 0.5  # How much base speed increases per second

# Special pixel spawn odds (percentage)
RED_PIXEL_ODDS = 10  # 10% chance for a red pixel
GREEN_PIXEL_ODDS = 15  # 15% chance for a green pixel
ORANGE_PIXEL_ODDS = 20  # 20% chance for an orange pixel

# Orange pixel settings
ORANGE_SPLASH_RADIUS = 150  # Radius in which orange pixel spawns white pixels
ORANGE_SPLASH_COUNT = 3  # Number of white pixels spawned by orange pixel

# Game exit button settings
GAME_EXIT_ICON_SCALE = 0.2  # Scale for the exit icon in game screen
GAME_EXIT_ICON_PADDING = 20  # Padding from the top-right corner
