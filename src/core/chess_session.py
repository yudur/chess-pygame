from abc import ABC, abstractmethod

from src.chess.game_logic import GameLogic


class ChessSession(ABC):
    """Abstracts a game mode (local, online, vs AI).

    It encapsulates GameLogic and exposes high-level operations
    that the game state (GameState) needs to call.
    """

    def __init__(self, local_color: str | None) -> None:
        # Chess rules engine, shared across all modes
        self.logic = GameLogic()
        self.local_color = local_color

    @abstractmethod
    def handle_board_click(self, row: int, col: int) -> None:
        """Handle a click on a board square (logical coordinates)."""
        raise NotImplementedError

    def update(self, dt: float) -> None:
        """Session-specific updates (network, AI, timers, etc.).

        In a pure local game, there is nothing to do here.
        """


class LocalChessSession(ChessSession):
    """Local game session (Player vs Player on the same PC)."""

    def handle_board_click(self, row: int, col: int) -> None:
        # In local mode, just delegate to GameLogic to decide selection/move
        self.logic.select_square(row, col)


class OnlineChessSession(ChessSession):
    pass


class AiChessSession(ChessSession):
    def __init__(self, local_color):
        from src.chess.ai import AiEngine

        super().__init__(local_color)

        # Human plays as local_color; AI plays as the opposite color
        self.human_color = local_color
        self.ai_color = "black" if local_color == "white" else "white"
        self.ai = AiEngine(color=self.ai_color, elo=1900)

    def handle_board_click(self, row, col):
        """Handle human input only when it's the human's turn."""

        if self.logic.game_over:
            return

        if self.logic.current_turn != self.human_color:
            # Ignore clicks when it's not the human's turn
            return

        self.logic.select_square(row, col)

    def update(self, dt: float) -> None:
        """Let the AI move automatically when it's its turn."""

        if self.logic.game_over:
            return

        if self.logic.current_turn != self.ai_color:
            return

        move = self.ai.get_move(self.logic.board, self.ai_color)
        if move is None:
            return

        (from_row, from_col), (to_row, to_col) = move

        # Apply the move using the existing selection/move logic
        self.logic.select_square(from_row, from_col)
        self.logic.select_square(to_row, to_col)

        # If AI's move created a pending promotion, auto-promote to queen
        if self.logic.pending_promotion is not None:
            self.logic.promote_pawn(
                "queen"
            )  # TODO: adapt to AI to do your own promotion
