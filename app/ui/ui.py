from collections import Counter

import pygame


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 20)

    def get_counts(self, entities):
        return Counter(e.kind for e in entities)

    def draw(self, screen, entities, mode, playing, game_x, game_y, game_width):
        counts = self.get_counts(entities)

        ui_x = game_x + game_width + 20
        ui_y = game_y

        lines = [
            f"Mode: {mode}",
            f"Status: {'Playing' if playing else 'Paused'}",
            "",
            f"Rock: {counts['rock']}",
            f"Paper: {counts['paper']}",
            f"Scissors: {counts['scissors']}",
            "",
            "Controls:",
            "SPACE - pause",
            "TAB - mode",
            "R - restart",
        ]

        for i, text in enumerate(lines):
            surface = self.font.render(text, True, (255, 255, 255))
            screen.blit(surface, (ui_x, ui_y + i * 25))
