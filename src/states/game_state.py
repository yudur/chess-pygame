import pygame
from src.core.state import State
from src.core.chess_session import ChessSession, OnlineChessSession

from src.ui.board_renderer import BoardRenderer
from src.ui.piece_renderer import PieceRenderer
from src.ui.modal_upgrade_pawn_renderer import ModalUpgradePawnRenderer
from src.ui.button_renderer import ButtonRenderer
from src.ui.overlay_game_over_notification_renderer import GameOverNotificationRenderer

from src.utils import settings


class GameState(State):
    def __init__(self, manager, session: ChessSession):
        self.manager = manager
        # Game session (local, online, vs AI, etc.)
        self.session = session
        # GameLogic comes from inside the session
        self.logic = session.logic

        self.board_renderer = BoardRenderer(self.logic.board)
        self.piece_renderer = PieceRenderer()
        self.promotion_modal = ModalUpgradePawnRenderer(None, None)
        self.button_exit = ButtonRenderer(
            pos=(
                settings.WIDTH
                - (settings.TILESIZE * 4 + settings.START_GRID_BOARD_POS[0]),
                settings.START_GRID_BOARD_POS[1],
            ),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Quit to Menu",
        )
        self.game_over_notification = GameOverNotificationRenderer(None)

        self.sounds = {
            "entry": pygame.mixer.Sound(str(settings.SOUNDS_PATH / "notify.mp3")),
            "move": pygame.mixer.Sound(str(settings.SOUNDS_PATH / "move-self.mp3")),
            "capture": pygame.mixer.Sound(str(settings.SOUNDS_PATH / "capture.mp3")),
            "check": pygame.mixer.Sound(str(settings.SOUNDS_PATH / "move-check.mp3")),
            "checkmate": pygame.mixer.Sound(
                str(settings.SOUNDS_PATH / "checkmate.mp3")
            ),
            "castling": pygame.mixer.Sound(str(settings.SOUNDS_PATH / "castle.mp3")),
        }

        self.dragging = False
        self.drag_piece = None
        self.drag_origin = None  # (row, col)
        self.mouse_pos = (0, 0)
        # Track last move and game-over state to trigger sounds once
        self._last_move_seen = self.logic.last_move
        self._was_game_over = self.logic.game_over

    def enter(self):
        self.sounds["entry"].play()

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Determine if board should be rendered from Black's perspective
            flipped = getattr(self.session, "local_color", None) == "black"

            # If there is a pending promotion, only the promoting side
            # should interact with the modal (in online mode).
            if self.logic.pending_promotion is not None:
                if isinstance(self.session, OnlineChessSession):
                    color, _, _ = self.logic.pending_promotion
                    # Only the owner of the pawn can choose the promotion piece
                    if self.session.local_color == color:
                        choice = self.promotion_modal.handle_click(x, y)
                        if choice is not None:
                            self.session.promote_pawn(choice)
                else:
                    choice = self.promotion_modal.handle_click(x, y)
                    if choice is not None:
                        self.session.promote_pawn(choice)
                return

            # Check if button was clicked
            if self.button_exit.is_clicked((x, y)):
                from src.states.home_state import HomeState

                # If this is an online session, close the network connection
                if isinstance(self.session, OnlineChessSession):
                    self.session.close()

                self.manager.change_state(
                    HomeState(self.manager)
                )  # Go back to home menu
                return

            screen_row = (y - settings.START_GRID_BOARD_POS[1]) // settings.TILESIZE
            screen_col = (x - settings.START_GRID_BOARD_POS[0]) // settings.TILESIZE

            if flipped:
                row = 7 - screen_row
                col = 7 - screen_col
            else:
                row = screen_row
                col = screen_col

            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.logic.board.get_piece(row, col)

                # Start drag if clicking on a piece of the side to move
                if piece and piece.color == self.logic.current_turn:
                    self.dragging = True
                    self.drag_piece = piece
                    self.drag_origin = (row, col)
                    self.mouse_pos = event.pos

                    # Also let the session/logic compute valid moves
                    self.session.handle_board_click(row, col)
                else:
                    # Clicked an empty square or enemy piece: delegate to session/logic
                    self.session.handle_board_click(row, col)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                x, y = event.pos
                flipped = getattr(self.session, "local_color", None) == "black"

                screen_row = (y - settings.START_GRID_BOARD_POS[1]) // settings.TILESIZE
                screen_col = (x - settings.START_GRID_BOARD_POS[0]) // settings.TILESIZE

                if flipped:
                    row = 7 - screen_row
                    col = 7 - screen_col
                else:
                    row = screen_row
                    col = screen_col

                if 0 <= row < 8 and 0 <= col < 8:
                    # Drop on a board square: let the session/logic decide if it's a valid move
                    self.session.handle_board_click(row, col)
                else:
                    # Dropped outside the board: cancel selection
                    self.logic.selected_piece = None
                    self.logic.valid_moves = []

                self.dragging = False
                self.drag_piece = None
                self.drag_origin = None

    def update(self, dt):
        # Update exit button hover state
        self.button_exit.update(pygame.mouse.get_pos())

        # Keep previous values to detect changes after the session updates
        prev_last_move = self._last_move_seen
        prev_game_over = self._was_game_over

        # Let the session update itself (AI move, online opponent move, etc.)
        self.session.update(dt)

        # In online games, if the connection is closed (e.g. opponent left),
        # send the player back to the home menu.
        if isinstance(self.session, OnlineChessSession):
            if self.session.connection_status == "closed":
                from src.states.home_state import HomeState

                self.manager.change_state(HomeState(self.manager))
                return

        # Check if a new move happened since the last frame
        new_last_move = self.logic.last_move
        if new_last_move is not None and new_last_move is not prev_last_move:
            # Choose appropriate sound based on the last move characteristics
            if (
                self.logic.game_over
                and self.logic.result
                and self.logic.result[0] == "checkmate"
            ):
                # Checkmate sound will be handled below
                pass
            elif getattr(self.logic, "last_move_was_castling", False):
                self.sounds["castling"].play()
            elif getattr(self.logic, "last_move_was_capture", False):
                self.sounds["capture"].play()
            else:
                # If the side to move is in check after this move, play check sound
                if hasattr(self.logic, "is_in_check") and self.logic.is_in_check():
                    self.sounds["check"].play()
                else:
                    self.sounds["move"].play()

            self._last_move_seen = new_last_move

        # Play game over sound once, when the game transitions to over
        if self.logic.game_over and not prev_game_over:
            if self.logic.result and self.logic.result[0] == "checkmate":
                self.sounds["checkmate"].play()

        self._was_game_over = self.logic.game_over

    def render(self, screen):
        self.button_exit.draw(screen)

        flipped = getattr(self.session, "local_color", None) == "black"

        self.board_renderer.draw(screen, flipped=flipped)
        self.board_renderer.draw_highlights(
            screen, self.logic.valid_moves, flipped=flipped
        )

        dragging_piece = self.drag_piece if self.dragging else None

        for row in range(8):
            for col in range(8):
                piece = self.logic.board.get_piece(row, col)
                if piece:
                    # When dragging, don't draw the piece at its board square
                    if dragging_piece is not None and piece is dragging_piece:
                        continue
                    self.piece_renderer.draw(screen, piece, flipped=flipped)

        # Draw the dragged piece following the mouse cursor, if any
        if dragging_piece is not None:
            mx, my = self.mouse_pos
            self.piece_renderer.draw_at(screen, dragging_piece, (mx, my))

        # Draw promotion modal if a pawn is waiting to be promoted
        if self.logic.pending_promotion is not None:
            color, _, _ = self.logic.pending_promotion

            # In online mode, the modal only appears for the player
            # who is promoting the pawn.
            if isinstance(self.session, OnlineChessSession):
                if self.session.local_color != color:
                    # Opponent: do not show the modal; just wait for
                    # the promotion message coming from the network.
                    pass
                else:
                    self.promotion_modal.screen = screen
                    self.promotion_modal.color = color
                    self.promotion_modal.render()
            else:
                # Local / vs AI: always show the modal
                self.promotion_modal.screen = screen
                self.promotion_modal.color = color
                self.promotion_modal.render()

        if self.logic.game_over:
            self.game_over_notification.winner_color = self.logic.result[1]
            self.game_over_notification.render(screen)
