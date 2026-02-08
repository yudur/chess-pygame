from src.chess.pieces.piece import Piece


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight")

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        offsets = [
            (-2, -1),
            (-2, 1),  # up-left, up-right
            (2, -1),
            (2, 1),  # down-left, down-right
            (-1, -2),
            (1, -2),  # left-up, left-down
            (-1, 2),
            (1, 2),  # right-up, right-down
        ]

        for d_row, d_col in offsets:
            new_row = row + d_row
            new_col = col + d_col

            if not board.is_inside(new_row, new_col):
                continue

            target = board.get_piece(new_row, new_col)

            if target is None or target.color != self.color:
                moves.append((new_row, new_col))

        return moves
