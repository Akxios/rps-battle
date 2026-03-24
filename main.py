import pygame

from app.core.config import FPS, GREY, HEIGHT, WIDTH

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def main():
    running = True
    playing = False

    while running:
        clock.tick(FPS)

    pygame.display.set_caption("Playing" if playing else "Stop")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                playing = not playing

        screen.fill(GREY)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
