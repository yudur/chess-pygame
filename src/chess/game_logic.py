from src.chess.pieces.pawn import Pawn
from src.chess.board import Board


class GameLogic:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.last_move = None  # (piece, from_row, from_col, to_row, to_col)
        self.game_over = False
        self.result: tuple[str, str] | None = None  # (reason, winner)

    def select_square(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected_piece is None:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece

                # Start with the basic pseudo-legal moves for the piece
                base_moves = piece.valid_moves(self.board)

                # Filter out moves that would leave this side's king in check
                self.valid_moves = self.get_legal_moves_for_moves(piece, base_moves)

                # Castling: add king-side/queen-side castling squares if available
                if piece.kind == "king":
                    castle_moves = self._get_castling_moves_for_king(piece)
                    self.valid_moves.extend(castle_moves)

                # En passant: add special capture square to pawn moves based on last move
                if isinstance(piece, Pawn) and self.last_move is not None:
                    last_piece, from_row, _, to_row, to_col = self.last_move

                    if (
                        isinstance(last_piece, Pawn)
                        and last_piece.color != piece.color
                        and abs(to_row - from_row) == 2  # moved two squares
                        and to_row == row  # on the same rank as our pawn
                        and abs(to_col - col) == 1  # adjacent file
                    ):
                        ep_row = row + piece.direction
                        ep_col = to_col
                        if self.board.is_inside(ep_row, ep_col) and self.board.is_empty(
                            ep_row, ep_col
                        ):
                            # It must also be a legal move (not leave our king in check)
                            if (ep_row, ep_col) in self.get_legal_moves_for_moves(
                                piece, [(ep_row, ep_col)]
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

        # Castling: if king moved two files horizontally, move the rook as well
        if piece.kind == "king" and abs(col - from_col) == 2:
            rook_row = row
            if col > from_col:  # king-side castling
                rook_from_col, rook_to_col = 7, 5
            else:  # queen-side castling
                rook_from_col, rook_to_col = 0, 3

            rook = self.board.get_piece(rook_row, rook_from_col)
            if rook:
                self.board.remove_piece(rook_row, rook_from_col)
                self.board.place_piece(rook, rook_row, rook_to_col)
                rook.has_moved = True

        # Mark piece as having moved (important for king/rook castling checks)
        piece.has_moved = True

        self.last_move = (piece, from_row, from_col, row, col)
        self.current_turn = "black" if self.current_turn == "white" else "white"

        if self.is_checkmate(self.current_turn):
            self.game_over = True
            winner = "black" if self.current_turn == "white" else "white"
            self.result = ("checkmate", winner)
        elif self.is_stalemate(self.current_turn):
            self.game_over = True
            self.result = ("stalemate", self.current_turn)

    def is_square_attacked(self, board, target_row, target_col, by_color):
        """Return True if (target_row, target_col) is attacked by any piece of by_color."""

        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece and piece.color == by_color:
                    if (target_row, target_col) in piece.valid_moves(board):
                        return True
        return False

    def _king_in_check_after(self, board, color):
        king_pos = board.find_king(color)
        if not king_pos:
            return False  # King is missing, should not happen in a valid game

        enemy = "black" if color == "white" else "white"
        return self.is_square_attacked(board, king_pos[0], king_pos[1], enemy)

    def get_legal_moves_for_moves(self, piece, candidate_moves):
        """Filter candidate_moves, removing moves that leave the moving side's king in check."""

        legal_moves = []

        for to_row, to_col in candidate_moves:
            # Simulate the move on a cloned board
            temp_board = self.board.clone()

            from_row, from_col = piece.position

            temp_piece = temp_board.get_piece(from_row, from_col)
            temp_board.remove_piece(from_row, from_col)
            temp_board.place_piece(temp_piece, to_row, to_col)

            # Check if the king is in check after this move
            if not self._king_in_check_after(temp_board, piece.color):
                legal_moves.append((to_row, to_col))

        return legal_moves

    def _get_castling_moves_for_king(self, king):
        """Return a list of castling target squares for the given king on the current board."""

        # King must not have moved
        if getattr(king, "has_moved", False):
            return []

        row, col = king.position
        color = king.color
        enemy = "black" if color == "white" else "white"

        # King must be on the original file (e file: col == 4) and correct rank
        back_rank = 7 if color == "white" else 0
        if row != back_rank or col != 4:
            return []

        # King cannot currently be in check
        if self.is_square_attacked(self.board, row, col, enemy):
            return []

        castles = []

        # King-side castling
        king_side_rook_col = 7
        rook = self.board.get_piece(back_rank, king_side_rook_col)
        if (
            rook
            and rook.color == color
            and getattr(rook, "has_moved", False) is False
            and self.board.is_empty(back_rank, 5)
            and self.board.is_empty(back_rank, 6)
        ):
            if not self.is_square_attacked(
                self.board, back_rank, 5, enemy
            ) and not self.is_square_attacked(self.board, back_rank, 6, enemy):
                castles.append((back_rank, 6))

        # Queen-side castling
        queen_side_rook_col = 0
        rook = self.board.get_piece(back_rank, queen_side_rook_col)
        if (
            rook
            and rook.color == color
            and getattr(rook, "has_moved", False) is False
            and self.board.is_empty(back_rank, 1)
            and self.board.is_empty(back_rank, 2)
            and self.board.is_empty(back_rank, 3)
        ):
            if not self.is_square_attacked(
                self.board, back_rank, 3, enemy
            ) and not self.is_square_attacked(self.board, back_rank, 2, enemy):
                castles.append((back_rank, 2))

        return castles

    def _has_any_legal_move(self, color: str) -> bool:
        """Return True if the side with `color` has at least one legal move."""

        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if not piece or piece.color != color:
                    continue

                candidate_moves = piece.valid_moves(self.board)

                # Include castling options when scanning king moves for game-over logic
                if piece.kind == "king":
                    candidate_moves += self._get_castling_moves_for_king(piece)
                if not candidate_moves:
                    continue

                legal_moves = self.get_legal_moves_for_moves(piece, candidate_moves)
                if legal_moves:
                    return True

        return False

    def is_checkmate(self, color: str) -> bool:
        """Return True if `color` is in check and has no legal moves (checkmate)."""

        if not self._king_in_check_after(self.board, color):
            return False

        return not self._has_any_legal_move(color)

    def is_stalemate(self, color: str) -> bool:
        """Return True if `color` is not in check but has no legal moves (stalemate)."""

        if self._king_in_check_after(self.board, color):
            return False

        return not self._has_any_legal_move(color)
