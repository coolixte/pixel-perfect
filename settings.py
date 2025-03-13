# Game Settings

# Screen dimensions
SCREEN_WIDTH = 940
SCREEN_HEIGHT = 605

# Window settings
BORDERLESS_WINDOW = True  # Set to True for borderless window, False for normal window

# Colors
BLACK = (0, 0, 0)

# Assets directory
ASSETS_DIR = "assets"

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
PIXEL_MIN_INTERVAL = 4.0  # Minimum seconds between random animations
PIXEL_MAX_INTERVAL = 8.0  # Maximum seconds between random animations
PIXEL_CLICK_COUNT = 10    # Number of particles to spawn on click
PIXEL_GRAVITY = 1.5      # Gravity strength (0 = no gravity, higher values = stronger gravity)
