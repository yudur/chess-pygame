from pathlib import Path
import pygame

GRID_SIZE = 8

# Base design values (used to scale to the current display)
BASE_TILESIZE = 70
BASE_SIDEBAR_WIDTH = 500
BASE_SIDEBAR_HEIGHT = 110
BASE_START_GRID_BOARD_POS = (55, 55)

# Default values (will be updated after pygame.init())
TILESIZE = BASE_TILESIZE
WIDTH = TILESIZE * GRID_SIZE + BASE_SIDEBAR_WIDTH
HEIGHT = TILESIZE * GRID_SIZE + BASE_SIDEBAR_HEIGHT
FPS = 60

START_GRID_BOARD_POS = BASE_START_GRID_BOARD_POS

BACKGROUND_COLOR_RGB = (48, 46, 43)

# Board theme colors
BOARD_LIGHT_COLOR = (240, 217, 181)
BOARD_DARK_COLOR = (181, 136, 99)

ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
PIECES_PATH = ASSETS_PATH / "images" / "pieces"

PIECES_COLOR = {
    "white": "white\\w_",
    "black": "black\\b_",
}


def initialize_display_settings():
    """Initialize screen constants ONCE after pygame.init()."""
    global TILESIZE, WIDTH, HEIGHT, START_GRID_BOARD_POS

    info = pygame.display.Info()
    max_w = int(info.current_w * 0.9)
    max_h = int(info.current_h * 0.85)

    base_width = BASE_TILESIZE * GRID_SIZE + BASE_SIDEBAR_WIDTH
    base_height = BASE_TILESIZE * GRID_SIZE + BASE_SIDEBAR_HEIGHT

    scale = min(max_w / base_width, max_h / base_height)

    TILESIZE = max(1, int(BASE_TILESIZE * scale))
    sidebar_width = int(BASE_SIDEBAR_WIDTH * scale)
    sidebar_height = int(BASE_SIDEBAR_HEIGHT * scale)

    WIDTH = TILESIZE * GRID_SIZE + sidebar_width
    HEIGHT = TILESIZE * GRID_SIZE + sidebar_height
    START_GRID_BOARD_POS = (
        int(BASE_START_GRID_BOARD_POS[0] * scale),
        int(BASE_START_GRID_BOARD_POS[1] * scale),
    )
