from pathlib import Path


TILESIZE = 80
WIDTH = TILESIZE * 8 + 600
HEIGHT = TILESIZE * 8 + 120
FPS = 60

START_GRID_BOARD_POS = (60, 60)

BACKGROUND_COLOR_RGB = (48, 46, 43)

ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
PIECES_PATH = ASSETS_PATH / "images" / "pieces"
