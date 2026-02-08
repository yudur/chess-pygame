from src.chess.pieces.piece import Piece


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop")

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        directions = [
            (-1, -1),  # up-left
            (-1, 1),  # up-right
            (1, -1),  # down-left
            (1, 1),  # down-right
        ]

        for d_row, d_col in directions:
            for i in range(1, 8):
                new_row = row + d_row * i
                new_col = col + d_col * i

                if not board.is_inside(new_row, new_col):
                    break

                if board.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                else:
                    if board.get_piece(new_row, new_col).color != self.color:
                        moves.append((new_row, new_col))
                    break

        return moves
