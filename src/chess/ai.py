from __future__ import annotations

from typing import Optional, Tuple

from stockfish import Stockfish

from src.utils import settings
from src.chess.board import Board
from src.chess.pieces.king import King
from src.chess.pieces.rook import Rook


Coord = Tuple[int, int]
MoveCoords = Tuple[Coord, Coord]


class AiEngine:
    """Thin wrapper around the Stockfish engine.

    This class is responsible only for:
    - holding a Stockfish instance
    - translating our Board into FEN
    - translating a UCI move (e2e4) into (row, col) coordinates
    """

    def __init__(self, color: str, elo: int = 1350) -> None:
        # 'white' or 'black' that this engine plays as
        self.color = color

        # Path to the Stockfish binary is configured in settings
        self.sf = Stockfish(settings.STOCKFISH_PATH)
        self.sf.set_elo_rating(elo)

    def get_move(
        self,
        board: Board,
        side_to_move: str,
        time_limit_ms: int = 1000,
    ) -> Optional[MoveCoords]:
        """Ask Stockfish for a move for the given side.

        :param board: Current Board instance.
        :param side_to_move: 'white' or 'black'. Should match the current_turn
                             in GameLogic when this is called.
        :param time_limit_ms: Time limit hint in milliseconds (not all
                              Stockfish Python bindings use it; we fall back
                              to get_best_move() if needed).
        :return: ((from_row, from_col), (to_row, to_col)) or None if no move.
        """

        fen = _board_to_fen(board, side_to_move)
        self.sf.set_fen_position(fen)

        # Some versions expose get_best_move_time, others only get_best_move.
        move_str: Optional[str]
        if hasattr(self.sf, "get_best_move_time"):
            move_str = self.sf.get_best_move_time(time_limit_ms)
        else:
            move_str = self.sf.get_best_move()

        if not move_str:
            return None

        return _uci_to_coords(move_str)


def _board_to_fen(board: Board, color: str) -> str:
    """Convert internal Board representation to a FEN string.

    This includes:
    - piece placement from our 8x8 array
    - active color ("w" or "b")
    - basic castling rights inferred from king/rook has_moved flags
    - en-passant and move counters simplified ("- 0 1")
    """

    rows = []
    for row in range(8):  # 0 (black back rank) -> 7 (white back rank)
        empty = 0
        row_str = ""
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece is None:
                empty += 1
                continue

            if empty > 0:
                row_str += str(empty)
                empty = 0

            kind = piece.kind
            if kind == "pawn":
                letter = "p"
            elif kind == "rook":
                letter = "r"
            elif kind == "knight":
                letter = "n"
            elif kind == "bishop":
                letter = "b"
            elif kind == "queen":
                letter = "q"
            elif kind == "king":
                letter = "k"
            else:
                letter = "?"

            if piece.color == "white":
                letter = letter.upper()

            row_str += letter

        if empty > 0:
            row_str += str(empty)
        rows.append(row_str)

    placement = "/".join(rows)

    active_color = "w" if color == "white" else "b"

    rights = []

    # White castling
    wk = board.get_piece(7, 4)
    if isinstance(wk, King) and not wk.has_moved:
        wr_h = board.get_piece(7, 7)
        wr_a = board.get_piece(7, 0)
        if isinstance(wr_h, Rook) and not wr_h.has_moved:
            rights.append("K")
        if isinstance(wr_a, Rook) and not wr_a.has_moved:
            rights.append("Q")

    # Black castling
    bk = board.get_piece(0, 4)
    if isinstance(bk, King) and not bk.has_moved:
        br_h = board.get_piece(0, 7)
        br_a = board.get_piece(0, 0)
        if isinstance(br_h, Rook) and not br_h.has_moved:
            rights.append("k")
        if isinstance(br_a, Rook) and not br_a.has_moved:
            rights.append("q")

    castling = "".join(rights) if rights else "-"

    en_passant = "-"
    halfmove = 0
    fullmove = 1

    return f"{placement} {active_color} {castling} {en_passant} {halfmove} {fullmove}"


def _uci_to_coords(move: str) -> MoveCoords:
    """Convert a UCI move string (e.g. 'e2e4') to (row, col) coordinates."""

    if len(move) < 4:
        raise ValueError(f"Invalid UCI move: {move}")

    from_file, from_rank, to_file, to_rank = move[0], move[1], move[2], move[3]

    def file_to_col(ch: str) -> int:
        return ord(ch) - ord("a")

    def rank_to_row(ch: str) -> int:
        # Rank '8' is row 0, rank '1' is row 7
        return 8 - int(ch)

    from_col = file_to_col(from_file)
    from_row = rank_to_row(from_rank)
    to_col = file_to_col(to_file)
    to_row = rank_to_row(to_rank)

    return (from_row, from_col), (to_row, to_col)

