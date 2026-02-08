from src.chess.board import Board


class GameLogic:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"
