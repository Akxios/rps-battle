import math
import random

from app.core.config import (
    GAME_HEIGHT,
    GAME_WIDTH,
    MAX_SPEED,
    RADIUS,
    VISION_RADIUS,
    WALL_MARGIN,
    WALL_PUSH,
)


class Entity:
    def __init__(self, x, y, vx, vy, kind, radius=RADIUS) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.radius = radius

    def move(self):
        self.vx *= 0.99
        self.vy *= 0.99

        # мягкое отталкивание от стен
        if self.x < WALL_MARGIN:
            self.vx += (WALL_MARGIN - self.x) / WALL_MARGIN * WALL_PUSH
        elif self.x > GAME_WIDTH - WALL_MARGIN:
            self.vx -= (self.x - (GAME_WIDTH - WALL_MARGIN)) / WALL_MARGIN * WALL_PUSH

        if self.y < WALL_MARGIN:
            self.vy += (WALL_MARGIN - self.y) / WALL_MARGIN * WALL_PUSH
        elif self.y > GAME_HEIGHT - WALL_MARGIN:
            self.vy -= (self.y - (GAME_HEIGHT - WALL_MARGIN)) / WALL_MARGIN * WALL_PUSH

        self.x += self.vx
        self.y += self.vy

        # левая / правая стенка
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
            self.vx += random.uniform(-0.5, 0.5)

        elif self.x + self.radius > GAME_WIDTH:
            self.x = GAME_WIDTH - self.radius
            self.vx *= -1
            self.vx += random.uniform(-0.5, 0.5)

        # верх / низ
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
            self.vy += random.uniform(-0.5, 0.5)

        elif self.y + self.radius > GAME_HEIGHT:
            self.y = GAME_HEIGHT - self.radius
            self.vy *= -1
            self.vy += random.uniform(-0.5, 0.5)
        self.limit_speed()

    def limit_speed(self, max_speed=MAX_SPEED):
        speed = (self.vx**2 + self.vy**2) ** 0.5
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed

    @staticmethod
    def collide(a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        dist_sq = dx * dx + dy * dy

        contact_dist = (a.radius + b.radius) * 1

        return dist_sq < contact_dist * contact_dist

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

    @staticmethod
    def separate(a, b):
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.001:
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            dist = math.sqrt(dx * dx + dy * dy)

        overlap = (a.radius + b.radius) - dist
        if overlap > 0:
            # нормаль
            nx = dx / dist
            ny = dy / dist

            # раздвигаем
            a.x -= nx * overlap / 2
            a.y -= ny * overlap / 2
            b.x += nx * overlap / 2
            b.y += ny * overlap / 2

            # лёгкий пинок
            a.vx -= nx * 0.5
            a.vy -= ny * 0.5
            b.vx += nx * 0.5
            b.vy += ny * 0.5

    def think(self, entities):
        nearest_target = None
        nearest_threat = None

        min_target_dist = float("inf")
        min_threat_dist = float("inf")

        center_x = 0
        center_y = 0

        avg_vx = 0
        avg_vy = 0

        count = 0

        for other in entities:
            if other is self:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            dist = dx * dx + dy * dy

            # --- цель / угроза ---
            if beats(self.kind, other.kind):
                if dist < min_target_dist:
                    min_target_dist = dist
                    nearest_target = other

            elif loses_to(self.kind, other.kind):
                if dist < min_threat_dist:
                    min_threat_dist = dist
                    nearest_threat = other

            # --- стая ---
            if other.kind == self.kind and dist < VISION_RADIUS * VISION_RADIUS:
                center_x += other.x
                center_y += other.y

                avg_vx += other.vx
                avg_vy += other.vy

                count += 1

        # --- движение (охота / бегство) ---
        if nearest_threat and min_threat_dist < min_target_dist:
            dx = self.x - nearest_threat.x
            dy = self.y - nearest_threat.y
        elif nearest_target:
            dx = nearest_target.x - self.x
            dy = nearest_target.y - self.y
        else:
            dx, dy = 0, 0

        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            dx /= length
            dy /= length
            self.vx += dx * 0.1
            self.vy += dy * 0.1

        if count > 0:
            center_x /= count
            center_y /= count

            avg_vx /= count
            avg_vy /= count

            # к центру стаи
            self.vx += (center_x - self.x) * 0.01
            self.vy += (center_y - self.y) * 0.01

            # выравнивание
            self.vx += (avg_vx - self.vx) * 0.05
            self.vy += (avg_vy - self.vy) * 0.05


def beats(a, b):
    return (
        (a == "rock" and b == "scissors")
        or (a == "scissors" and b == "paper")
        or (a == "paper" and b == "rock")
    )


def loses_to(a, b):
    return beats(b, a)
