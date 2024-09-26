# checkbox.py

import pygame
from constants import Constants

class CheckBox:
    def __init__(self, x, y, size=20, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = checked

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

    def draw(self, screen):
        pygame.draw.rect(screen, Constants.WHITE, self.rect, 2)
        if self.checked:
            # Draw checkmark
            pygame.draw.line(screen, Constants.WHITE, (self.rect.x, self.rect.y),
                             (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 2)
            pygame.draw.line(screen, Constants.WHITE, (self.rect.x + self.rect.width, self.rect.y),
                             (self.rect.x, self.rect.y + self.rect.height), 2)

    def is_checked(self):
        return self.checked
