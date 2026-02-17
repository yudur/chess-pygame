import pygame


class NumericInputRenderer:
    def __init__(self, pos, size, placeholder="", min_value=400, max_value=3000):
        self.pos = pos
        self.size = size
        self.placeholder = placeholder
        self.min_value = min_value
        self.max_value = max_value
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

        # Colors
        self.color_default = (181, 136, 99)
        self.placeholder_color = (130, 94, 65)
        self.border_color = (48, 46, 43)
        self.text_color = (48, 46, 43)

        self.is_active = False
        self.input_field = ""

        self.font = pygame.font.Font(None, 24)

    def is_clicked(self, mouse_pos):
        clicked = self.rect.collidepoint(mouse_pos)
        if clicked:
            self.is_active = True
        else:
            self.is_active = False
        return clicked

    def handle_event(self, event):
        if not self.is_active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.input_field = self.input_field[:-1]
        elif pygame.K_0 <= event.key <= pygame.K_9:
            self.input_field += str(event.key - pygame.K_0)

    def get_value(self):
        if not self.input_field:
            return self.min_value

        try:
            value = int(self.input_field)
        except ValueError:
            return self.min_value

        if value < self.min_value:
            return self.min_value
        if value > self.max_value:
            return self.max_value
        return value

    def render(self, screen):
        # Render the numeric input field
        pygame.draw.rect(screen, self.color_default, self.rect)

        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        # Draw text
        text_surface = self.font.render(
            self.input_field if self.input_field else self.placeholder,
            True,
            self.text_color if self.input_field else self.placeholder_color,
        )
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
