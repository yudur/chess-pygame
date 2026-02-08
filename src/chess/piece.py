class Piece:
    def __init__(self, color: str, kind: str):
        self.color = color
        self.kind = kind  # "pawn" | "rook" | "knight" | "bishop" | "queen" | "king"
        self.position: tuple[int, int] | None = None

    def valid_moves(self, board) -> list[tuple[int, int]]:
        pass
