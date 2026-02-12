import pygame

from src.utils import settings


class GameOverNotificationRenderer:
    def __init__(self, winner_color):
        self.winner_color = winner_color

    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface(
            (   
                settings.TILESIZE * 8,
                settings.TILESIZE * 8
            ), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha for transparency
        screen.blit(overlay, (settings.START_GRID_BOARD_POS[0], settings.START_GRID_BOARD_POS[1]))

        # Game Over text
        font = pygame.font.Font(None, 64)
        if self.winner_color == "white":
            text = "White wins!"
        elif self.winner_color == "black":
            text = "Black wins!"
        else:
            text = "It's a draw!"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(overlay.get_width() // 2, overlay.get_height() // 2))
        screen.blit(text_surface, text_rect)