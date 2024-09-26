# button.py

import pygame
from constants import Constants

class Button:
    def __init__(self, x, y, w, h, text, callback, color=Constants.GRAY, hover_color=Constants.LIGHT_BLUE):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, Constants.BUTTON_FONT_SIZE)
        self.txt_surface = self.font.render(text, True, Constants.BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        # Center the text
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
