import pygame

from src.core.state_manager import StateManager

from src.states.home_state import HomeState
from src.utils import settings


class GameApp:
    def __init__(self):
        pygame.init()
        settings.initialize_display_settings()

        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager()
        self.state_manager.change_state(HomeState(self.state_manager))

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000  # delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.state_manager.handle_event(event)

            self.state_manager.update(dt)
            self.screen.fill(settings.BACKGROUND_COLOR_RGB)
            self.state_manager.render(self.screen)
            pygame.display.flip()
        pygame.quit()
