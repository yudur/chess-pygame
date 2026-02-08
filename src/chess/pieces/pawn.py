from src.chess.pieces.piece import Piece


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn")

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        start_row = 6 if self.color == "white" else 1

        one_step = row + self.direction
        two_step = row + 2 * self.direction

        # Move forward
        if board.is_empty(one_step, col):
            moves.append((one_step, col))

        # Initial two-step move
        if (
            row == start_row
            and board.is_empty(two_step, col)
            and board.is_empty(one_step, col)
        ):
            moves.append((two_step, col))

        # diagonal capture
        for dc in (-1, 1):
            r, c = row + self.direction, col + dc
            if board.is_inside(r, c):
                target_piece = board.get_piece(r, c)
                if target_piece and target_piece.color != self.color:
                    moves.append((r, c))

        return moves
