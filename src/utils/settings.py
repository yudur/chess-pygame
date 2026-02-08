from pathlib import Path


TILESIZE = 96
WIDTH = TILESIZE * 8
HEIGHT = TILESIZE * 8
FPS = 60

ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
PIECES_PATH = ASSETS_PATH / "images" / "pieces"
