from src.chess.game_logic import GameLogic
from src.core.state import State

from src.ui.board_renderer import BoardRenderer
from src.ui.piece_renderer import PieceRenderer


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
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        self.board_renderer.draw(screen)

        for row in range(8):
            for col in range(8):
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    self.piece_renderer.draw(screen, piece)
