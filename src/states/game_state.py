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

        self.dragging = False
        self.drag_piece = None
        self.drag_origin = None  # (row, col)
        self.mouse_pos = (0, 0)

    def enter(self):
        print("Entering Game State")

    def exit(self):
        print("exitting Game State")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = (
                (y - settings.START_GRID_BOARD_POS[1]) // settings.TILESIZE,
                (x - settings.START_GRID_BOARD_POS[0]) // settings.TILESIZE,
            )

            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.logic.board.get_piece(row, col)

                # Start drag if clicking on a piece of the side to move
                if piece and piece.color == self.logic.current_turn:
                    self.dragging = True
                    self.drag_piece = piece
                    self.drag_origin = (row, col)
                    self.mouse_pos = event.pos

                    # Also let the logic compute valid moves for this piece
                    self.logic.select_square(row, col)
                else:
                    # Clicked an empty square or enemy piece: delegate to logic (may clear selection)
                    self.logic.select_square(row, col)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                x, y = event.pos
                row, col = (
                    (y - settings.START_GRID_BOARD_POS[1]) // settings.TILESIZE,
                    (x - settings.START_GRID_BOARD_POS[0]) // settings.TILESIZE,
                )

                if 0 <= row < 8 and 0 <= col < 8:
                    # Drop on a board square: let GameLogic decide if it's a valid move
                    self.logic.select_square(row, col)
                else:
                    # Dropped outside the board: cancel selection
                    self.logic.selected_piece = None
                    self.logic.valid_moves = []

                self.dragging = False
                self.drag_piece = None
                self.drag_origin = None

    def update(self, dt):
        if self.logic.game_over:
            print(f"Game Over: {self.logic.result[0]} - {self.logic.result[1]}")
            # Here you could transition to a GameOverState or reset the game

    def render(self, screen):
        self.board_renderer.draw(screen)
        self.board_renderer.draw_highlights(screen, self.logic.valid_moves)

        dragging_piece = self.drag_piece if self.dragging else None

        for row in range(8):
            for col in range(8):
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    # When dragging, don't draw the piece at its board square
                    if dragging_piece is not None and piece is dragging_piece:
                        continue
                    self.piece_renderer.draw(screen, piece)

        # Draw the dragged piece following the mouse cursor, if any
        if dragging_piece is not None:
            mx, my = self.mouse_pos
            self.piece_renderer.draw_at(screen, dragging_piece, (mx, my))
