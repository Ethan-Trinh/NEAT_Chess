import pygame
import os

from sound import Sound
from theme import Theme

class Config:

    def __init__(self):
        self.themes = []
        self._add_themes()
        self.idx = 0
        self.theme = self.themes[self.idx]

        self.font = pygame.font.SysFont('monospace', 18, bold=True)

        self.move_sound = Sound(
            os.path.join('assets/sounds/move.wav')
        )
        self.capture_sound = Sound(
            os.path.join('assets/sounds/capture.wav')
        )
    
    def change_theme(self):
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = self.themes[self.idx]

    def _add_themes(self):
        default = Theme((234, 235, 200), (119, 154, 88), (244, 247, 116), (172, 195, 51), '#C86464', '#C84646')

        self.themes = [default]