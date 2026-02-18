from abc import ABC, abstractmethod
import copy
import json
import threading
from queue import Queue

from src.chess.game_logic import GameLogic
import websocket


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

    @abstractmethod
    def promote_pawn(self, new_piece_kind: str) -> None:
        """Handle pawn promotion for this session.

        new_piece_kind: "queen", "rook", "bishop" or "knight".
        """
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

    def promote_pawn(self, new_piece_kind: str) -> None:
        # Promotion only updates the local board
        self.logic.promote_pawn(new_piece_kind)


class OnlineChessSession(ChessSession):
    def __init__(self, server_url: str) -> None:
        super().__init__(local_color=None)

        self.server_url = server_url

        self.connection_status: str = (
            "connecting"  # connecting | waiting_for_opponent | matched | error
        )
        self.room_id: str | None = None
        self.assigned_color: str | None = None  # "white" or "black"

        # Queue of messages received from the server (consumed by GameState/session)
        self._inbound_messages: Queue[dict] = Queue()

        # WebSocketApp from websocket-client library
        self._ws_app = websocket.WebSocketApp(
            self.server_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        # Run the websocket in a separate thread so it does not block the pygame loop
        self._ws_thread = threading.Thread(
            target=self._ws_app.run_forever,
            daemon=True,
        )
        self._ws_thread.start()

    def close(self) -> None:
        """Close the websocket connection and mark the session as closed."""

        try:
            self._ws_app.close()
        except Exception:
            pass

        if self.connection_status not in {"error", "closed"}:
            self.connection_status = "closed"

    def _on_open(self, ws) -> None:
        self.connection_status = "connected"

    def _on_message(self, ws, message: str) -> None:
        """
        - {"type": "waiting_for_opponent"}
        - {"type": "match_found", "room_id": str, "color": "white"|"black"}
        - {"type": "opponent_left"}
        - {"type": "move", "from": [row, col], "to": [row, col], "promotion": "queen"|"rook"|...}
        """

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Ignore invalid messages
            return

        if data["type"] == "waiting_for_opponent":
            self.connection_status = "waiting_for_opponent"
        elif data["type"] == "match_found":
            self.connection_status = "matched"
            self.room_id = data["room_id"]
            self.assigned_color = data["color"]

            # We now know the local player's color
            self.local_color = self.assigned_color

        # Store every message for later consumption by GameState/logic
        self._inbound_messages.put(data)

    def _on_error(self, ws, error) -> None:
        self.connection_status = "error"

    def _on_close(self, ws, close_status_code, close_msg) -> None:
        if self.connection_status != "error":
            self.connection_status = "closed"

    def get_next_message(self) -> dict | None:
        if self._inbound_messages.empty():
            return None
        return self._inbound_messages.get()

    def promote_pawn(self, new_piece_kind: str) -> None:
        """Promotion initiated by the local player.

        Updates GameLogic and notifies the opponent via the server.
        """

        # Ensure there is actually a pending promotion
        if self.logic.pending_promotion is None:
            return

        color, _, _ = self.logic.pending_promotion

        # In online mode, only the owner of the pawn should resolve promotion
        if self.local_color is not None and color != self.local_color:
            return

        # Apply promotion locally
        self.logic.promote_pawn(new_piece_kind)

        # Notify the opponent
        if self.connection_status == "matched":
            payload = {
                "type": "promotion",
                "piece": new_piece_kind,
            }
            try:
                self._ws_app.send(json.dumps(payload))
            except Exception:
                self.connection_status = "error"

    def _send_move(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> None:
        """Send a move to the server.

        The server simply forwards this message to the opponent.
        """

        if self.connection_status != "matched":
            return

        payload = {
            "type": "move",
            "from": [from_row, from_col],
            "to": [to_row, to_col],
        }

        try:
            # websocket-client sends text; the FastAPI server expects JSON
            self._ws_app.send(json.dumps(payload))
        except Exception:
            # On send error, mark the connection as broken
            self.connection_status = "error"

    def handle_board_click(self, row: int, col: int) -> None:
        """Handle board clicks in online mode.

        Reuses GameLogic.select_square to validate/execute moves.
        When a full move (from one square to another) is made, sends it
        to the server.
        """

        # Not matched yet or we still don't know our color
        if self.connection_status != "matched" or self.local_color is None:
            return

        # Do nothing if the game is already over
        if self.logic.game_over:
            return

        # Only allow input when it's the local player's turn
        if self.logic.current_turn != self.local_color:
            return

        # Save last_move before the click so we can detect when a new move was made
        prev_last_move = self.logic.last_move

        # Delegate to GameLogic (same flow as local session)
        self.logic.select_square(row, col)

        # If last_move changed, it means a move was executed
        if (
            self.logic.last_move is not None
            and self.logic.last_move is not prev_last_move
        ):
            piece, from_row, from_col, to_row, to_col = self.logic.last_move
            self._send_move(from_row, from_col, to_row, to_col)

    def update(self, dt: float) -> None:
        """Process messages received from the server (opponent moves, etc.)."""

        # Consume all pending messages in this frame
        while True:
            msg = self.get_next_message()
            if msg is None:
                break

            msg_type = msg.get("type")

            if msg_type == "move":
                # Opponent's move
                from_row, from_col = msg.get("from", [None, None])
                to_row, to_col = msg.get("to", [None, None])

                if None in (from_row, from_col, to_row, to_col):
                    continue

                if self.logic.game_over:
                    continue

                # Apply the remote move using the same GameLogic flow
                self.logic.select_square(from_row, from_col)
                self.logic.select_square(to_row, to_col)

            elif msg_type == "promotion":
                # Promotion choice made by the opponent
                piece = msg.get("piece")
                if piece and self.logic.pending_promotion is not None:
                    self.logic.promote_pawn(piece)

            elif msg_type == "opponent_left":
                # We could mark game_over or notify GameState here
                # For now we just update the connection status
                self.connection_status = "closed"


class AiChessSession(ChessSession):
    def __init__(self, local_color, elo=1900):
        from src.chess.ai import AiEngine

        super().__init__(local_color)

        # Human plays as local_color; AI plays as the opposite color
        self.human_color = local_color
        self.ai_color = "black" if local_color == "white" else "white"

        self.ai = AiEngine(color=self.ai_color, elo=elo)

        self.queue = Queue()
        self._thread: threading.Thread | None = None
        self._ai_thinking = False

    def _ai_worker(self) -> None:
        board_copy = copy.deepcopy(self.logic.board)
        move = self.ai.get_move(board_copy, self.ai_color)
        self.queue.put(move)

    def handle_board_click(self, row, col):
        """Handle human input only when it's the human's turn."""

        if self.logic.game_over:
            return

        if self.logic.current_turn != self.human_color:
            # Ignore clicks when it's not the human's turn
            return

        self.logic.select_square(row, col)

    def promote_pawn(self, new_piece_kind: str) -> None:
        # For human vs AI, promotion is only local
        self.logic.promote_pawn(new_piece_kind)

    def update(self, dt: float) -> None:
        """Let the AI move automatically when it's its turn."""

        if self.logic.game_over:
            return

        if self.logic.current_turn == self.ai_color and not self._ai_thinking:
            self._ai_thinking = True
            self._thread = threading.Thread(target=self._ai_worker, daemon=True)
            self._thread.start()

        if self._ai_thinking and not self.queue.empty():
            move = self.queue.get()
            self._ai_thinking = False

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
