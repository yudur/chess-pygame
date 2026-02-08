import pygame
from src.chess.board import Board

SQUARE_SIZE = 96
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
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
                )
                pygame.draw.rect(screen, color, rect)
