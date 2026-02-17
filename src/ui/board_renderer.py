import pygame
from src.chess.board import Board
from src.utils import settings


class BoardRenderer:
    def __init__(self, board: Board):
        self.board = board

    def draw(self, screen: pygame.Surface, flipped: bool = False):
        for row in range(8):
            for col in range(8):
                # Map board coordinates to screen coordinates depending on orientation
                screen_row = 7 - row if flipped else row
                screen_col = 7 - col if flipped else col

                color = (
                    settings.BOARD_LIGHT_COLOR
                    if (screen_row + screen_col) % 2 == 0
                    else settings.BOARD_DARK_COLOR
                )
                rect = pygame.Rect(
                    screen_col * settings.TILESIZE + settings.START_GRID_BOARD_POS[0],
                    screen_row * settings.TILESIZE + settings.START_GRID_BOARD_POS[1],
                    settings.TILESIZE,
                    settings.TILESIZE,
                )
                pygame.draw.rect(screen, color, rect)

    def draw_highlights(self, screen: pygame.Surface, moves, flipped: bool = False):
        for row, col in moves:
            # Map board coordinates of highlighted squares to screen coordinates
            screen_row = 7 - row if flipped else row
            screen_col = 7 - col if flipped else col

            rect = pygame.Rect(
                screen_col * settings.TILESIZE + settings.START_GRID_BOARD_POS[0],
                screen_row * settings.TILESIZE + settings.START_GRID_BOARD_POS[1],
                settings.TILESIZE,
                settings.TILESIZE,
            )
            pygame.draw.rect(screen, (0, 255, 0), rect, 4)
