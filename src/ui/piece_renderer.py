import pygame
from src.chess.pieces.piece import Piece
from src.utils import settings

COLORS = {
    "white": "white/w_",
    "black": "black/b_",
}


class PieceRenderer:
    def __init__(self):
        self.img = None

    def draw(self, screen: pygame.Surface, piece: Piece):
        row, col = piece.position
        center = (
            col * settings.TILESIZE + settings.TILESIZE // 2,
            row * settings.TILESIZE + settings.TILESIZE // 2,
        )

        self.img = pygame.image.load(
            f"{settings.PIECES_PATH / COLORS[piece.color]}{piece.kind.title()}.png"
        ).convert_alpha()
        self.img = pygame.transform.smoothscale(
            self.img, (settings.TILESIZE, settings.TILESIZE)
        )
        screen.blit(self.img, self.img.get_rect(center=center))
