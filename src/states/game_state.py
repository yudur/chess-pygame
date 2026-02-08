import pygame
from src.chess.game_logic import GameLogic
from src.core.state import State

from src.ui.board_renderer import BoardRenderer
from src.ui.piece_renderer import PieceRenderer
from src.utils import settings


class GameState(State):
    def __init__(self, manager):
        self.manager = manager
        self.logic = GameLogic()

        self.board_renderer = BoardRenderer(self.logic.board)
        self.piece_renderer = PieceRenderer()

    def enter(self):
        print("Entering Game State")

    def exit(self):
        print("Exiting Game State")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // settings.TILESIZE, x // settings.TILESIZE

            print(f"Clicked on square: ({row}, {col})")

            self.logic.select_square(row, col)

    def update(self, dt):
        pass

    def render(self, screen):
        self.board_renderer.draw(screen)
        self.board_renderer.draw_highlights(screen, self.logic.valid_moves)

        for row in range(8):
            for col in range(8):
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    self.piece_renderer.draw(screen, piece)
