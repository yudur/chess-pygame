import pygame
from src.core.chess_session import OnlineChessSession
from src.core.state import State

from src.states.game_state import GameState
from src.utils import settings


class WaitingForOpponentState(State):
    def __init__(self, manager):
        self.manager = manager
        self.session: OnlineChessSession | None = None
        self.font = pygame.font.Font(None, 32)
        self._has_started_game = False

    def enter(self):
        self.session = OnlineChessSession(settings.URI_SERVER_ONLINE_GAME)

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        if self.session is None:
            return

        if self._has_started_game:
            return

        status = self.session.connection_status

        if status == "matched" and self.session.assigned_color is not None:
            self._has_started_game = True
            self.manager.change_state(GameState(self.manager, self.session))

    def render(self, screen):
        status_text = "Connecting to server..."
        if self.session is not None:
            if self.session.connection_status == "waiting_for_opponent":
                status_text = "Waiting for opponent..."
            elif self.session.connection_status == "matched":
                status_text = f"Match found! You are {self.session.assigned_color}."
            elif self.session.connection_status == "error":
                status_text = "Connection error."
            elif self.session.connection_status == "closed":
                status_text = "Connection closed."

        text_surface = self.font.render(status_text, True, (240, 217, 181))
        text_rect = text_surface.get_rect(
            center=(settings.WIDTH // 2, settings.HEIGHT // 2)
        )
        screen.blit(text_surface, text_rect)
