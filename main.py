# main.py

import pygame
from constants import Constants
from visualization_app import VisualizationApp

def main():
    pygame.init()
    screen = pygame.display.set_mode((Constants.WIDTH, Constants.HEIGHT))
    pygame.display.set_caption("Rotating Lines Visualization")
    clock = pygame.time.Clock()

    app = VisualizationApp(screen)
    app.run(clock)

if __name__ == "__main__":
    main()
