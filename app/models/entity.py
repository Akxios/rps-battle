import random

from app.core.config import HEIGHT, WIDTH


class Entity:
    def __init__(self, x, y, vx, vy, kind, radius=5) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.radius = radius

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # левая / правая стенка
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
            self.vx += random.uniform(-0.5, 0.5)

        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1
            self.vx += random.uniform(-0.5, 0.5)

        # верх / низ
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
            self.vy += random.uniform(-0.5, 0.5)

        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -1
            self.vy += random.uniform(-0.5, 0.5)

    @staticmethod
    def collide(a, b):
        dx = a.x - b.x
        dy = a.y - b.y

        return dx * dx + dy * dy < (a.radius + b.radius) ** 2

    @staticmethod
    def resolve(a, b):
        if a.kind == b.kind:
            return

        if (
            (a.kind == "rock" and b.kind == "scissors")
            or (a.kind == "scissors" and b.kind == "paper")
            or (a.kind == "paper" and b.kind == "rock")
        ):
            b.kind = a.kind
        else:
            a.kind = b.kind
