from src.chess.pieces.piece import Piece


class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king")

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        directions = [
            (-1, 0),  # up
            (1, 0),  # down
            (0, -1),  # left
            (0, 1),  # right
            (-1, -1),  # up-left
            (-1, 1),  # up-right
            (1, -1),  # down-left
            (1, 1),  # down-right
        ]

        for d_row, d_col in directions:
            new_row = row + d_row
            new_col = col + d_col

            if not board.is_inside(new_row, new_col):
                continue

            if board.is_empty(new_row, new_col):
                moves.append((new_row, new_col))
            else:
                if board.get_piece(new_row, new_col).color != self.color:
                    moves.append((new_row, new_col))
        return moves
