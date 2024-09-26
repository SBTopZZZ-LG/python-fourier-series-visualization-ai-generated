# constants.py

class Constants:
    # Screen dimensions
    WIDTH = 1000
    HEIGHT = 700
    CENTER = (WIDTH // 2, HEIGHT // 2)

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LIGHT_BLUE = (173, 216, 230)
    DRAW_COLOR = (200, 200, 200)  # Slightly darker than white
    GRAY = (100, 100, 100)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    FAINT_WHITE = (200, 200, 200)  # For faint labels

    # Fonts
    FONT_SIZE = 24
    BUTTON_FONT_SIZE = 28

    # Frame rate
    FPS = 60

    # Application States
    INPUT_MODE = 'input'
    VISUALIZE_MODE = 'visualize'
