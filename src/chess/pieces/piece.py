class Piece:
    def __init__(self, color: str, kind: str):
        self.color = color
        self.kind = kind  # "pawn" | "rook" | "knight" | "bishop" | "queen" | "king"
        self.position: tuple[int, int] | None = None
        self.direction = -1 if self.color == "white" else 1
        # Tracks whether this piece has moved at least once (used for castling)
        self.has_moved = False

    def valid_moves(self, board) -> list[tuple[int, int]]:
        pass
