from src.chess.pieces.knight import Knight
from src.chess.pieces.bishop import Bishop
from src.chess.pieces.rook import Rook
from src.chess.pieces.pawn import Pawn
from src.chess.pieces.queen import Queen
from src.chess.pieces.king import King


class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]  # 8x8

        self.setup_initial_position()

    def setup_initial_position(self):
        # Pawns
        for col in range(8):
            self.place_piece(Pawn("black"), 1, col)
            self.place_piece(Pawn("white"), 6, col)

        # black (line 0)
        self.place_piece(Rook("black"), 0, 0)
        self.place_piece(Rook("black"), 0, 7)
        self.place_piece(Knight("black"), 0, 1)
        self.place_piece(Knight("black"), 0, 6)
        self.place_piece(Bishop("black"), 0, 2)
        self.place_piece(Bishop("black"), 0, 5)
        self.place_piece(Queen("black"), 0, 3)
        self.place_piece(King("black"), 0, 4)

        # white (line 7)
        self.place_piece(Rook("white"), 7, 0)
        self.place_piece(Rook("white"), 7, 7)
        self.place_piece(Knight("white"), 7, 1)
        self.place_piece(Knight("white"), 7, 6)
        self.place_piece(Bishop("white"), 7, 2)
        self.place_piece(Bishop("white"), 7, 5)
        self.place_piece(Queen("white"), 7, 3)
        self.place_piece(King("white"), 7, 4)

    def place_piece(self, piece, row, col):
        self.board[row][col] = piece
        piece.position = (row, col)

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove_piece(self, row, col):
        self.board[row][col] = None
        return

    def is_empty(self, row, col):
        return self.is_inside(row, col) and self.board[row][col] is None

    def is_inside(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
