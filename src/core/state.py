from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, surface):
        pass
