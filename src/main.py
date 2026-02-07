import pygame
import settings


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()  # Update the display
            self.clock.tick(60)  # Limit to 60 frames per second
        pygame.quit()


if __name__ == "__main__":
    Game().run()
