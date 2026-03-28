import random
from collections import defaultdict

import pygame

from app.core.config import (
    CAPTURE_FRAMES,
    COLOR_MAP,
    FPS,
    GAME_HEIGHT,
    GAME_WIDTH,
    GREY,
    PAPER_URL,
    ROCK_URL,
    SCALE_IMAGE,
    SCISSORS_URL,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from app.models.entity import Entity
from app.ui.ui import UI
from app.utils.utils import create_entities

contact_frames = defaultdict(int)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

game_x = (WINDOW_WIDTH - GAME_WIDTH) // 2
game_y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2
clock = pygame.time.Clock()
ui = UI()

# картинки
images = {
    "rock": pygame.image.load(ROCK_URL),
    "scissors": pygame.image.load(SCISSORS_URL),
    "paper": pygame.image.load(PAPER_URL),
}


for key in images:
    images[key] = pygame.transform.scale(images[key], (SCALE_IMAGE, SCALE_IMAGE))


def main():
    running = True
    playing = True
    entities = create_entities()

    mode = "chaos"  # или "smart"

    while running:
        clock.tick(FPS)

        pygame.display.set_caption(
            f"{'Playing' if playing else 'Paused'} | Mode: {mode} | SPACE pause | TAB switch | R reset"
        )

        # события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing

                if event.key == pygame.K_TAB:
                    mode = "smart" if mode == "chaos" else "chaos"

                if event.key == pygame.K_r:
                    entities = create_entities()
                    contact_frames.clear()

        # логика игры
        if playing:
            if mode == "smart":
                for e in entities:
                    e.think(entities)
                    e.move()

            if mode == "chaos":
                threshold = 1
                for e in entities:
                    e.vx += random.uniform(-0.2, 0.2)
                    e.vy += random.uniform(-0.2, 0.2)
                    e.move()
            else:
                threshold = CAPTURE_FRAMES

            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    a = entities[i]
                    b = entities[j]

                    if Entity.collide(a, b):
                        Entity.separate(a, b)
                        contact_frames[(i, j)] += 1

                        if contact_frames[(i, j)] >= threshold:
                            Entity.resolve(a, b)
                            contact_frames[(i, j)] = 0
                    else:
                        contact_frames[(i, j)] = 0

        # отрисовка
        screen.fill((30, 30, 30))

        pygame.draw.rect(
            screen, (255, 255, 255), (game_x, game_y, GAME_WIDTH, GAME_HEIGHT), 2
        )

        game_surface.fill(GREY)

        for e in entities:
            img = images[e.kind]
            game_surface.blit(img, (e.x - e.radius, e.y - e.radius))

            # направление движения
            end_x = e.x + e.vx * 5
            end_y = e.y + e.vy * 5

            pygame.draw.line(
                game_surface, COLOR_MAP[e.kind], (e.x, e.y), (end_x, end_y), 1
            )

        screen.blit(game_surface, (game_x, game_y))
        ui.draw(screen, entities, mode, playing, game_x, game_y, GAME_WIDTH)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
