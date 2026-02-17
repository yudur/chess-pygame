import pygame
from src.core.state import State
from src.ui.button_renderer import ButtonRenderer
from src.utils import settings

from src.core.chess_session import AiChessSession
from src.states.game_state import GameState


class SelectColorVsAiState(State):
    def __init__(self, manager):
        self.manager = manager

        self.button_playing_with_white = ButtonRenderer(
            pos=(
                settings.START_GRID_BOARD_POS[0],
                settings.START_GRID_BOARD_POS[1] + 20,
            ),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Playing with White",
        )
        self.button_playing_with_black = ButtonRenderer(
            pos=(
                settings.START_GRID_BOARD_POS[0],
                settings.START_GRID_BOARD_POS[1] + settings.TILESIZE * 1 + 20,
            ),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Playing with Black",
        )

        self.back_to_home = ButtonRenderer(
            pos=(
                settings.START_GRID_BOARD_POS[0],
                settings.START_GRID_BOARD_POS[1] + settings.TILESIZE * 2 + 20,
            ),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Back to Home",
        )

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.button_playing_with_white.is_clicked((x, y)):
                self.manager.change_state(
                    GameState(self.manager, AiChessSession("white"))
                )
            elif self.button_playing_with_black.is_clicked((x, y)):
                self.manager.change_state(
                    GameState(self.manager, AiChessSession("black"))
                )
            elif self.back_to_home.is_clicked((x, y)):
                from src.states.home_state import HomeState

                self.manager.change_state(HomeState(self.manager))

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()

        self.button_playing_with_white.update(mouse_pos)
        self.button_playing_with_black.update(mouse_pos)
        self.back_to_home.update(mouse_pos)

    def render(self, screen):
        self.button_playing_with_white.draw(screen)
        self.button_playing_with_black.draw(screen)
        self.back_to_home.draw(screen)
