import pygame
from src.chess.piece import Piece
from src.utils import settings

SQUARE_SIZE = 96

COLORS = {
    "white": "white/w_",
    "black": "black/b_",
}


class PieceRenderer:
    def draw(self, screen: pygame.Surface, piece: Piece):
        row, col = piece.position
        center = (
            col * SQUARE_SIZE + SQUARE_SIZE // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2,
        )

        img = pygame.image.load(
            f"{settings.PIECES_PATH / COLORS[piece.color]}{piece.kind.title()}.png"
        ).convert_alpha()
        img = pygame.transform.smoothscale(img, (settings.TILESIZE, settings.TILESIZE))
        screen.blit(img, img.get_rect(center=center))
