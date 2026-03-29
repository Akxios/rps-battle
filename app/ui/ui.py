from collections import Counter

import pygame

from app.core.config import COLOR_MAP, WHITE


class UI:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)

        self.bg = (20, 20, 20)
        self.panel = (35, 35, 35)
        self.panel_border = (90, 90, 90)
        self.text = (240, 240, 240)
        self.muted = (170, 170, 170)
        self.green = (70, 200, 120)
        self.red = (220, 80, 80)
        self.yellow = (240, 200, 80)

    def get_counts(self, entities):
        return Counter(e.kind for e in entities)

    def _draw_text(self, screen, text, font, color, x, y):
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))
        return surface.get_height()

    def _draw_box(self, screen, rect, fill, border=None, radius=10):
        pygame.draw.rect(screen, fill, rect, border_radius=radius)
        if border:
            pygame.draw.rect(screen, border, rect, 1, border_radius=radius)

    def _draw_species_row(self, screen, x, y, label, value, color):
        dot_radius = 6
        pygame.draw.circle(screen, color, (x + dot_radius, y + 11), dot_radius)

        self._draw_text(screen, label, self.font_text, self.text, x + 18, y)
        value_surface = self.font_text.render(str(value), True, WHITE)
        screen.blit(value_surface, (x + 135, y))

    def draw(self, screen, entities, mode, playing, game_x, game_y, game_width):
        counts = self.get_counts(entities)

        panel_x = game_x + game_width + 20
        panel_y = game_y
        panel_w = 290
        panel_h = 400

        # main panel
        self._draw_box(
            screen,
            pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            self.panel,
            self.panel_border,
            radius=14,
        )

        x = panel_x + 16
        y = panel_y + 14

        # title
        self._draw_text(screen, "RPS Simulation", self.font_title, WHITE, x, y)
        y += 38

        # status
        status_text = "Playing" if playing else "Paused"
        status_color = self.green if playing else self.red
        self._draw_box(
            screen,
            pygame.Rect(x, y, 110, 30),
            (50, 50, 50),
            status_color,
            radius=10,
        )
        self._draw_text(
            screen, status_text, self.font_text, status_color, x + 16, y + 4
        )

        mode_color = self.yellow if mode == "smart" else self.muted
        self._draw_box(
            screen,
            pygame.Rect(x + 120, y, 140, 30),
            (50, 50, 50),
            mode_color,
            radius=10,
        )
        self._draw_text(
            screen, f"Mode: {mode}", self.font_text, mode_color, x + 132, y + 4
        )

        y += 48

        # counts section
        self._draw_text(screen, "Counts", self.font_text, WHITE, x, y)
        y += 30

        self._draw_species_row(screen, x, y, "Rock", counts["rock"], COLOR_MAP["rock"])
        y += 28
        self._draw_species_row(
            screen, x, y, "Paper", counts["paper"], COLOR_MAP["paper"]
        )
        y += 28
        self._draw_species_row(
            screen, x, y, "Scissors", counts["scissors"], COLOR_MAP["scissors"]
        )
        y += 36

        # controls section
        self._draw_text(screen, "Controls", self.font_text, WHITE, x, y)
        y += 30

        controls = [
            ("SPACE", "pause / resume"),
            ("TAB", "switch mode"),
            ("R", "restart"),
        ]

        for key, desc in controls:
            key_width = 80
            key_height = 26
            gap = 12  # расстояние между кнопкой и текстом

            # кнопка
            self._draw_box(
                screen,
                pygame.Rect(x, y, key_width, key_height),
                (55, 55, 55),
                self.panel_border,
                radius=8,
            )

            # текст внутри кнопки (по центру)
            key_surface = self.font_small.render(key, True, WHITE)
            key_rect = key_surface.get_rect(
                center=(x + key_width // 2, y + key_height // 2)
            )
            screen.blit(key_surface, key_rect)

            # описание — дальше справа
            self._draw_text(
                screen,
                desc,
                self.font_small,
                self.muted,
                x + key_width + gap,
                y + 4,
            )

            y += 34
