from src.chess.pieces.pawn import Pawn
from src.chess.pieces.queen import Queen
from src.chess.pieces.rook import Rook
from src.chess.pieces.bishop import Bishop
from src.chess.pieces.knight import Knight

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
        # Promotion state: when not None, the game waits for the UI to choose a piece
        # (color, row, col)
        self.pending_promotion: tuple[str, int, int] | None = None
        # For draw detection
        self.halfmove_clock = 0  # Fifty-move rule counter
        self.position_history: list[str] = [self.board.get_position_hash()]  # For threefold repetition (starts with initial position)

    def select_square(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected_piece is None:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece

                # Start with the basic pseudo-legal moves for the piece
                base_moves = piece.valid_moves(self.board)

                # Filter out moves that would leave this side's king in check
                self.valid_moves = self._get_legal_moves_for_moves(piece, base_moves)

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
                            if (ep_row, ep_col) in self._get_legal_moves_for_moves(
                                piece, [(ep_row, ep_col)]
                            ):
                                self.valid_moves.append((ep_row, ep_col))
            return

        if (row, col) in self.valid_moves:
            self._move_piece(self.selected_piece, row, col)

        self.selected_piece = None
        self.valid_moves = []

    def _move_piece(self, piece, row, col):
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

        # Pawn promotion: if a pawn reaches the last rank, mark pending promotion
        if isinstance(piece, Pawn):
            last_rank = 0 if piece.color == "white" else 7
            if row == last_rank:
                self.pending_promotion = (piece.color, row, col)

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
        
        # Update halfmove clock for fifty-move rule
        # Reset to 0 on pawn move or capture, otherwise increment
        if isinstance(piece, Pawn) or target:
            self.halfmove_clock = 0
            # Also reset position history when capture/pawn move occurs (threefold repetition resets)
            self.position_history = [self.board.get_position_hash()]
        else:
            self.halfmove_clock += 1
        
        # Do not advance turn or check mate/stalemate if waiting for promotion choice
        if self.pending_promotion is not None:
            return

        self.current_turn = "black" if self.current_turn == "white" else "white"
        
        # Track position for threefold repetition (only if no reset above)
        if self.halfmove_clock > 0:  # Only track if not in reset state
            pos_hash = self.board.get_position_hash()
            self.position_history.append(pos_hash)
            
            # Keep history limited to avoid memory bloat
            # Only keep the last 100 positions (since fifty-move rule caps at 100 halfmoves anyway)
            if len(self.position_history) > 200:
                self.position_history = self.position_history[-200:]

        if self._is_checkmate(self.current_turn):
            self.game_over = True
            winner = "black" if self.current_turn == "white" else "white"
            self.result = ("checkmate", winner)
        elif self._is_draw():
            self.game_over = True
            self.result = ("draw", None)
        elif self._is_stalemate(self.current_turn):
            self.game_over = True
            self.result = ("stalemate", None)  # not have a winner in stalemate

    def promote_pawn(self, new_piece_kind: str):
        """Replace the pawn at pending_promotion with a new piece of the given kind.

        new_piece_kind should be one of: "queen", "rook", "bishop", "knight".
        """

        if self.pending_promotion is None:
            return

        color, row, col = self.pending_promotion

        # Remove the pawn and create the new piece
        self.board.remove_piece(row, col)

        if new_piece_kind == "queen":
            new_piece = Queen(color)
        elif new_piece_kind == "rook":
            new_piece = Rook(color)
        elif new_piece_kind == "bishop":
            new_piece = Bishop(color)
        elif new_piece_kind == "knight":
            new_piece = Knight(color)
        else:
            # Fallback: promote to queen if unknown kind
            new_piece = Queen(color)

        self.board.place_piece(new_piece, row, col)

        # Clear promotion state and continue the game
        self.pending_promotion = None

        self.current_turn = "black" if self.current_turn == "white" else "white"
        
        # Track position for threefold repetition
        # Note: pawn promotion counts like a pawn move for halfmove clock (already reset in _move_piece),
        # so position_history was already reset
        pos_hash = self.board.get_position_hash()
        self.position_history.append(pos_hash)
        
        # Keep history limited to avoid memory bloat
        if len(self.position_history) > 200:
            self.position_history = self.position_history[-200:]

        if self._is_checkmate(self.current_turn):
            self.game_over = True
            winner = "black" if self.current_turn == "white" else "white"
            self.result = ("checkmate", winner)
        elif self._is_draw():
            self.game_over = True
            self.result = ("draw", None)
        elif self._is_stalemate(self.current_turn):
            self.game_over = True
            self.result = ("stalemate", None)  # not have a winner in stalemate

    def _is_square_attacked(self, board, target_row, target_col, by_color):
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
        return self._is_square_attacked(board, king_pos[0], king_pos[1], enemy)

    def _get_legal_moves_for_moves(self, piece, candidate_moves):
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
        if self._is_square_attacked(self.board, row, col, enemy):
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
            if not self._is_square_attacked(
                self.board, back_rank, 5, enemy
            ) and not self._is_square_attacked(self.board, back_rank, 6, enemy):
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
            if not self._is_square_attacked(
                self.board, back_rank, 3, enemy
            ) and not self._is_square_attacked(self.board, back_rank, 2, enemy):
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

                legal_moves = self._get_legal_moves_for_moves(piece, candidate_moves)
                if legal_moves:
                    return True

        return False

    def _is_checkmate(self, color: str) -> bool:
        """Return True if `color` is in check and has no legal moves (checkmate)."""

        if not self._king_in_check_after(self.board, color):
            return False

        return not self._has_any_legal_move(color)

    def _is_stalemate(self, color: str) -> bool:
        """Return True if `color` is not in check but has no legal moves (stalemate)."""

        if self._king_in_check_after(self.board, color):
            return False

        return not self._has_any_legal_move(color)

    def _is_draw(self) -> bool:
        """Return True if the game is a draw by any rule."""
        
        # Fifty-move rule: 50 full moves (100 halfmoves) without pawn move or capture
        if self.halfmove_clock >= 100:
            return True
        
        # Threefold repetition: same position appears 3 times
        # Note: current position was already added to position_history before calling this method
        if len(self.position_history) > 0:
            current_pos = self.board.get_position_hash()
            repetition_count = self.position_history.count(current_pos)  # Already includes current position
            if repetition_count >= 3:
                return True
        
        # Insufficient material: neither side can deliver checkmate
        if self._has_insufficient_material():
            return True
        
        return False
    
    def _has_insufficient_material(self) -> bool:
        """Return True if neither side has enough material to deliver checkmate."""
        
        # Possible material for white and black
        white_pieces = []
        black_pieces = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    if piece.color == "white":
                        white_pieces.append(piece.kind)
                    else:
                        black_pieces.append(piece.kind)
        
        # Can checkmate if either side has: queen, rook, or 2+ minor pieces
        white_can_mate = (
            "queen" in white_pieces 
            or "rook" in white_pieces 
            or white_pieces.count("bishop") + white_pieces.count("knight") >= 2
        )
        
        black_can_mate = (
            "queen" in black_pieces 
            or "rook" in black_pieces 
            or black_pieces.count("bishop") + black_pieces.count("knight") >= 2
        )
        
        # Draw only if BOTH sides cannot deliver mate
        return not (white_can_mate or black_can_mate)
