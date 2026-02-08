from src.chess.pieces.pawn import Pawn
from src.chess.board import Board


class GameLogic:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.last_move = None  # (piece, from_row, from_col, to_row, to_col)

    def select_square(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected_piece is None:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.valid_moves = piece.valid_moves(self.board)

                # En passant: add a special capturing square to pawn moves
                if isinstance(piece, Pawn) and self.last_move is not None:
                    last_piece, from_row, _, to_row, to_col = self.last_move

                    if (
                        isinstance(last_piece, Pawn)
                        and last_piece.color != piece.color
                        and abs(to_row - from_row) == 2  # moved two spaces
                        and to_row == row  # is on the same line as our pawn
                        and abs(to_col - col) == 1  # adjacent column
                    ):
                        ep_row = row + piece.direction
                        ep_col = to_col
                        if self.board.is_inside(ep_row, ep_col) and self.board.is_empty(
                            ep_row, ep_col
                        ):
                            self.valid_moves.append((ep_row, ep_col))
            return

        if (row, col) in self.valid_moves:
            self.move_piece(self.selected_piece, row, col)

        self.selected_piece = None
        self.valid_moves = []

    def move_piece(self, piece, row, col):
        from_row, from_col = piece.position
        target = self.board.get_piece(row, col)

        # en passant: indirect capture
        if isinstance(piece, Pawn) and col != from_col and target is None:
            captured_row = from_row
            self.board.remove_piece(captured_row, col)

        if target:
            self.board.remove_piece(row, col)

        self.board.remove_piece(from_row, from_col)
        self.board.place_piece(piece, row, col)

        self.last_move = (piece, from_row, from_col, row, col)
        self.current_turn = "black" if self.current_turn == "white" else "white"
