import pygame
from src.core.state import State

from src.ui.button_renderer import ButtonRenderer

from src.utils import settings


class HomeState(State):
    def __init__(self, manager):
        self.manager = manager

        self.button_start_game_against_computer = ButtonRenderer(
            pos=(settings.START_GRID_BOARD_POS[0], settings.START_GRID_BOARD_POS[1] + 20),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Player vs Computer"
        )
        self.button_start_local_game = ButtonRenderer(
            pos=(settings.START_GRID_BOARD_POS[0], settings.START_GRID_BOARD_POS[1] + settings.TILESIZE * 1 + 20),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Player vs Player"
        )
        self.button_start_online_game = ButtonRenderer(
            pos=(settings.START_GRID_BOARD_POS[0], settings.START_GRID_BOARD_POS[1] + settings.TILESIZE * 2 + 20),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Play Online"
        )
        self.button_exit = ButtonRenderer(
            pos=(settings.START_GRID_BOARD_POS[0], settings.START_GRID_BOARD_POS[1] + settings.TILESIZE * 3 + 20),
            size=(settings.TILESIZE * 4, settings.TILESIZE),
            text="Exit"
        )

    def enter(self):
        print("Entering Home State")

    def exit(self):
        print("Exiting Home State")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if self.button_start_game_against_computer.is_clicked((x, y)):
                print("Start game against computer")
                # Here you would transition to the GameState with a flag for vs computer
                return
            
            if self.button_start_local_game.is_clicked((x, y)):
                print("Start local game")
                from src.states.game_state import GameState
                # Here you would transition to the GameState for local play
                self.manager.change_state(GameState(self.manager))  # For now just go to GameState without vs computer flag
            
            if self.button_start_online_game.is_clicked((x, y)):
                print("Start online game")
                # Here you would transition to an OnlineLobbyState or similar
                return
            
            if self.button_exit.is_clicked((x, y)):
                print("Exit game")
                pygame.quit()
                exit()

    def update(self, dt):
        self.button_start_game_against_computer.update(pygame.mouse.get_pos())
        self.button_start_local_game.update(pygame.mouse.get_pos())
        self.button_start_online_game.update(pygame.mouse.get_pos())
        self.button_exit.update(pygame.mouse.get_pos())

    def render(self, screen):
        self.button_start_game_against_computer.draw(screen)
        self.button_start_local_game.draw(screen)
        self.button_start_online_game.draw(screen)
        self.button_exit.draw(screen)
