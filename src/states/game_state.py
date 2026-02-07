from src.core.state import State


class GameState(State):
    def __init__(self, manager):
        self.manager = manager

    def enter(self):
        print("Entering Game State")

    def exit(self):
        print("Exiting Game State")

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((30, 30, 30))
