import pygame


class ButtonRenderer:
    def __init__(self, pos: tuple[int, int], size: tuple[int, int], text: str):
        """
        Initialize a button renderer.
        
        Args:
            pos: Tuple of (x, y) position for the button's top-left corner
            size: Tuple of (width, height) for the button
            text: Text to display on the button
        """
        self.pos = pos
        self.size = size
        self.text = text
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        
        # Colors
        self.color_default = (181, 136, 99)
        self.color_hover = (240, 217, 181)
        self.text_color = (48, 46, 43)
        self.border_color = (48, 46, 43)
        
        # State
        self.is_hovering = False
        
        # Font
        self.font = pygame.font.Font(None, 24)
    
    def update(self, mouse_pos: tuple[int, int]) -> None:
        """Update button state based on mouse position."""
        self.is_hovering = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        """Check if button was clicked."""
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen."""
        # Draw button background
        current_color = self.color_hover if self.is_hovering else self.color_default
        pygame.draw.rect(screen, current_color, self.rect)
        
        # Draw button border
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
