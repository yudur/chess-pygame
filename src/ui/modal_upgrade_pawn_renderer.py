import pygame
from src.utils import settings



class ModalUpgradePawnRenderer:
    def __init__(self, screen, color):
        self.screen = screen
        # color of the promoting side ("white" or "black")
        self.color = color

        # Layout configuration: 2x2 grid centered on the board
        self.grid_rows = 2
        self.grid_cols = 2
        self.cell_size = settings.TILESIZE

        # Board area on screen
        board_x, board_y = settings.START_GRID_BOARD_POS
        board_size = settings.TILESIZE * 8

        inner_width = self.grid_cols * self.cell_size
        inner_height = self.grid_rows * self.cell_size

        # Center modal in the middle of the board (no extra margin)
        x = board_x + (board_size - inner_width) // 2
        y = board_y + (board_size - inner_height) // 2

        self.rect = pygame.Rect(x, y, inner_width, inner_height)

        # Map 2x2 positions to promotion piece kinds
        # Order (row-major):
        # [ ["queen", "rook"],
        #   ["bishop", "knight"] ]
        self.options_grid = [
            ["queen", "rook"],
            ["bishop", "knight"],
        ]

    def render(self):
        # Slightly darker overlay over the whole screen
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        # Default to white pieces if color not set (should be overwritten by GameState)
        color = self.color or "white"

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = self.rect.x + col * self.cell_size
                cell_y = self.rect.y + row * self.cell_size
                cell_rect = pygame.Rect(
                    cell_x,
                    cell_y,
                    self.cell_size,
                    self.cell_size,
                )

                # Cell background: alternate light/dark like the board
                bg_color = (
                    settings.BOARD_LIGHT_COLOR
                    if (row + col) % 2 == 0
                    else settings.BOARD_DARK_COLOR
                )
                pygame.draw.rect(self.screen, bg_color, cell_rect)

                # Draw piece option icon (queen, rook, bishop, knight)
                kind = self.options_grid[row][col]
                prefix = settings.PIECES_COLOR[color]
                img_path = settings.PIECES_PATH / f"{prefix}{kind.title()}.png"

                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.smoothscale(
                    img, (self.cell_size, self.cell_size)
                )
                self.screen.blit(img, img.get_rect(center=cell_rect.center))

    def handle_click(self, x: int, y: int):
        """Given a mouse click, return chosen promotion kind or None if outside."""

        if not self.rect.collidepoint(x, y):
            return None

        rel_x = x - self.rect.x
        rel_y = y - self.rect.y

        col = rel_x // self.cell_size
        row = rel_y // self.cell_size

        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            return self.options_grid[row][col]

        return None