import pygame
from src.chess.board import Board
from src.utils import settings

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)


class BoardRenderer:
    def __init__(self, board: Board):
        self.board = board

    def draw(self, screen: pygame.Surface):
        for row in range(8):
            for col in range(8):
                color = LIGHT if (row + col) % 2 == 0 else DARK
                rect = pygame.Rect(
                    col * settings.TILESIZE,
                    row * settings.TILESIZE,
                    settings.TILESIZE,
                    settings.TILESIZE,
                )
                pygame.draw.rect(screen, color, rect)

    def draw_highlights(self, screen: pygame.Surface, moves):
        for row, col in moves:
            rect = pygame.Rect(col * 96, row * 96, 96, 96)
            pygame.draw.rect(screen, (0, 255, 0), rect, 4)
