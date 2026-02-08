from src.chess.piece import Piece


class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]  # 8x8

        self.setup_initial_position()

    def setup_initial_position(self):
        # Pawns
        for col in range(8):
            self.place_piece(Piece("black", "pawn"), 1, col)
            self.place_piece(Piece("white", "pawn"), 6, col)

        # black (line 0)
        self.place_piece(Piece("black", "rook"), 0, 0)
        self.place_piece(Piece("black", "rook"), 0, 7)
        self.place_piece(Piece("black", "knight"), 0, 1)
        self.place_piece(Piece("black", "knight"), 0, 6)
        self.place_piece(Piece("black", "bishop"), 0, 2)
        self.place_piece(Piece("black", "bishop"), 0, 5)
        self.place_piece(Piece("black", "queen"), 0, 3)
        self.place_piece(Piece("black", "king"), 0, 4)

        # white (line 7)
        self.place_piece(Piece("white", "rook"), 7, 0)
        self.place_piece(Piece("white", "rook"), 7, 7)
        self.place_piece(Piece("white", "knight"), 7, 1)
        self.place_piece(Piece("white", "knight"), 7, 6)
        self.place_piece(Piece("white", "bishop"), 7, 2)
        self.place_piece(Piece("white", "bishop"), 7, 5)
        self.place_piece(Piece("white", "queen"), 7, 3)
        self.place_piece(Piece("white", "king"), 7, 4)

    def place_piece(self, piece, row, col):
        self.board[row][col] = piece
        piece.position = (row, col)

    def get_piece(self, row, col):
        return self.board[row][col]
