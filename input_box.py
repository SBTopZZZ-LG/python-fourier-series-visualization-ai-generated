# input_box.py

import pygame
from constants import Constants

class InputBox:
    def __init__(self, x, y, w, h, placeholder='', unit=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = Constants.GRAY
        self.text = ''
        self.placeholder = placeholder
        self.unit = unit
        self.font = pygame.font.SysFont(None, Constants.FONT_SIZE)
        self.txt_surface = self.font.render(
            self.text if self.text else self.placeholder,
            True,
            Constants.WHITE if self.text else Constants.GRAY
        )
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            self.active = self.rect.collidepoint(event.pos)
            self.color = Constants.LIGHT_BLUE if self.active else Constants.GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = Constants.GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 10 and event.unicode.isprintable():
                        self.text += event.unicode
                # Re-render the text.
                display_text = self.text if self.text else self.placeholder
                self.txt_surface = self.font.render(
                    display_text,
                    True,
                    Constants.WHITE if self.text else Constants.GRAY
                )

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit the unit label
        if self.unit:
            unit_surf = self.font.render(self.unit, True, Constants.WHITE)
            screen.blit(unit_surf, (self.rect.x + self.rect.width + 10, self.rect.y + 8))

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return None

    def clear(self):
        self.text = ''
        self.txt_surface = self.font.render(self.placeholder, True, Constants.GRAY)

class ColorInput(InputBox):
    def __init__(self, x, y, w, h, placeholder='', unit=''):
        super().__init__(x, y, w, h, placeholder, unit)
        # Set default color to a visible color, e.g., red
        if not self.text:
            self.text = '#FF0000'
            self.txt_surface = self.font.render(self.text, True, Constants.WHITE)

    def get_color(self):
        text = self.text.strip()
        if text.startswith('#'):
            text = text[1:]
        if len(text) != 6:
            return None
        try:
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            return (r, g, b)
        except ValueError:
            return None
