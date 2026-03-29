from collections import Counter, defaultdict

import pygame

from app.core.config import (
    CAPTURE_FRAMES,
    COLOR_MAP,
    FPS,
    GAME_HEIGHT,
    GAME_WIDTH,
    GREY,
    PAIR_COOLDOWN_FRAMES,
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

touch_frames = defaultdict(int)
pair_cooldowns = defaultdict(int)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

game_x = (WINDOW_WIDTH - GAME_WIDTH) // 2
game_y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2

clock = pygame.time.Clock()
ui = UI()

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
    mode = "smart"  # or "chaos"

    while running:
        clock.tick(FPS)

        pygame.display.set_caption(
            f"{'Playing' if playing else 'Paused'} | Mode: {mode} | SPACE pause | TAB switch | R reset"
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing

                elif event.key == pygame.K_TAB:
                    mode = "smart" if mode == "chaos" else "chaos"

                elif event.key == pygame.K_r:
                    entities = create_entities()
                    touch_frames.clear()
                    pair_cooldowns.clear()

        if playing:
            population = Counter(e.kind for e in entities)

            for e in entities:
                e.reset_forces()

            if mode == "smart":
                for e in entities:
                    e.think(entities, population)
            else:
                for e in entities:
                    e.wander()

            for e in entities:
                e.integrate()

            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    a = entities[i]
                    b = entities[j]
                    key = (i, j)

                    if pair_cooldowns[key] > 0:
                        pair_cooldowns[key] -= 1
                        continue

                    if Entity.collide(a, b):
                        Entity.separate(a, b)
                        touch_frames[key] += 1

                        if touch_frames[key] >= CAPTURE_FRAMES:
                            if Entity.resolve(a, b):
                                pair_cooldowns[key] = PAIR_COOLDOWN_FRAMES
                            touch_frames[key] = 0
                    else:
                        touch_frames[key] = 0

        # draw
        screen.fill((30, 30, 30))
        pygame.draw.rect(
            screen, (255, 255, 255), (game_x, game_y, GAME_WIDTH, GAME_HEIGHT), 2
        )

        game_surface.fill(GREY)

        for e in entities:
            img = images[e.kind]
            game_surface.blit(img, (e.x - e.radius, e.y - e.radius))

            end_x = e.x + e.vx * 6
            end_y = e.y + e.vy * 6
            pygame.draw.line(
                game_surface, COLOR_MAP[e.kind], (e.x, e.y), (end_x, end_y), 1
            )

        screen.blit(game_surface, (game_x, game_y))
        ui.draw(screen, entities, mode, playing, game_x, game_y, GAME_WIDTH)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
