import pygame
from src.chess.pieces.piece import Piece
from src.utils import settings
from src.utils.image_cache import ImageCache


class PieceRenderer:
    def __init__(self):
        self.img = None
        self.image_cache = ImageCache()

    def draw(self, screen: pygame.Surface, piece: Piece, flipped: bool = False):
        row, col = piece.position

        # Map board coordinates to screen coordinates depending on orientation
        screen_row = 7 - row if flipped else row
        screen_col = 7 - col if flipped else col

        center = (
            screen_col * settings.TILESIZE
            + settings.TILESIZE // 2
            + settings.START_GRID_BOARD_POS[0],
            screen_row * settings.TILESIZE
            + settings.TILESIZE // 2
            + settings.START_GRID_BOARD_POS[1],
        )

        self.img = self.image_cache.get(
            f"{settings.PIECES_PATH / settings.PIECES_COLOR[piece.color]}{piece.kind.title()}.png",
            (settings.TILESIZE, settings.TILESIZE),
        )
        screen.blit(self.img, self.img.get_rect(center=center))

    def draw_at(self, screen: pygame.Surface, piece: Piece, center: tuple[int, int]):
        """Draw the given piece centered at an arbitrary pixel position (used for drag-and-drop)."""

        self.img = self.image_cache.get(
            f"{settings.PIECES_PATH / settings.PIECES_COLOR[piece.color]}{piece.kind.title()}.png",
            (settings.TILESIZE, settings.TILESIZE),
        )
        screen.blit(self.img, self.img.get_rect(center=center))
