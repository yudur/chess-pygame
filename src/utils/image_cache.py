import pygame


class ImageCache:
    def __init__(self):
        self._cache = {}

    def get(self, path: str, size: tuple[int, int] = None) -> pygame.Surface:
        key = (path, size)
        if key not in self._cache:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            self._cache[key] = img
        return self._cache[key]
