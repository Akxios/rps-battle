import math
import random

from app.core.config import (
    ALIGNMENT_FORCE,
    COHESION_FORCE,
    FLEE_FORCE,
    FRICTION,
    GAME_HEIGHT,
    GAME_WIDTH,
    MAX_SPEED,
    RADIUS,
    SEPARATION_FORCE,
    SEPARATION_RADIUS_SQ,
    VISION_RADIUS,
    WALL_AVOID_FORCE,
    WALL_MARGIN,
    WANDER_FORCE,
)


def beats(a, b):
    return (
        (a == "rock" and b == "scissors")
        or (a == "scissors" and b == "paper")
        or (a == "paper" and b == "rock")
    )


def loses_to(a, b):
    return beats(b, a)


def clamp(value, low, high):
    return max(low, min(high, value))


class Entity:
    def __init__(self, x, y, vx, vy, kind, radius=RADIUS) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.ax = 0.0
        self.ay = 0.0
        self.kind = kind
        self.radius = radius
        self.personality = random.uniform(0.8, 1.2)
        self.wander_angle = random.uniform(0, math.tau)

    def reset_forces(self):
        self.ax = 0.0
        self.ay = 0.0

    def add_force(self, fx, fy):
        self.ax += fx
        self.ay += fy

    def steer_towards(self, tx, ty, force):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-6:
            self.add_force(dx / dist * force, dy / dist * force)

    def steer_away(self, tx, ty, force):
        dx = self.x - tx
        dy = self.y - ty
        dist = math.hypot(dx, dy)
        if dist > 1e-6:
            self.add_force(dx / dist * force, dy / dist * force)

    def wander(self, force=WANDER_FORCE):
        self.wander_angle += random.uniform(-0.25, 0.25)
        self.add_force(
            math.cos(self.wander_angle) * force, math.sin(self.wander_angle) * force
        )

    def apply_wall_avoidance(self):
        if self.x < WALL_MARGIN:
            self.add_force((WALL_MARGIN - self.x) / WALL_MARGIN * WALL_AVOID_FORCE, 0)
        elif self.x > GAME_WIDTH - WALL_MARGIN:
            self.add_force(
                -(self.x - (GAME_WIDTH - WALL_MARGIN)) / WALL_MARGIN * WALL_AVOID_FORCE,
                0,
            )

        if self.y < WALL_MARGIN:
            self.add_force(0, (WALL_MARGIN - self.y) / WALL_MARGIN * WALL_AVOID_FORCE)
        elif self.y > GAME_HEIGHT - WALL_MARGIN:
            self.add_force(
                0,
                -(self.y - (GAME_HEIGHT - WALL_MARGIN))
                / WALL_MARGIN
                * WALL_AVOID_FORCE,
            )

    def think(self, entities, population):
        nearest_target = None
        nearest_threat = None
        min_target_d2 = float("inf")
        min_threat_d2 = float("inf")

        cohesion_x = 0.0
        cohesion_y = 0.0
        align_x = 0.0
        align_y = 0.0
        separation_x = 0.0
        separation_y = 0.0
        same_count = 0

        vision_sq = VISION_RADIUS * VISION_RADIUS

        for other in entities:
            if other is self:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            d2 = dx * dx + dy * dy

            if d2 < 1e-6:
                continue

            if d2 < SEPARATION_RADIUS_SQ:
                inv_d = 1.0 / math.sqrt(d2)
                separation_x -= dx * inv_d
                separation_y -= dy * inv_d

            if other.kind == self.kind and d2 < vision_sq:
                same_count += 1
                cohesion_x += other.x
                cohesion_y += other.y
                align_x += other.vx
                align_y += other.vy

            elif beats(self.kind, other.kind):
                if d2 < min_target_d2:
                    min_target_d2 = d2
                    nearest_target = other
            elif loses_to(self.kind, other.kind):
                if d2 < min_threat_d2:
                    min_threat_d2 = d2
                    nearest_threat = other

        total = max(1, len(entities))
        average_population = total / 3.0
        self_population = max(1, population.get(self.kind, 1))

        balance_boost = clamp(average_population / self_population, 0.85, 1.35)

        if nearest_threat is not None and min_threat_d2 < vision_sq * 1.5:
            self.steer_away(
                nearest_threat.x, nearest_threat.y, FLEE_FORCE * balance_boost
            )
        elif nearest_target is not None:
            self.steer_towards(nearest_target.x, nearest_target.y, 0.9 * balance_boost)

        if same_count > 0:
            cohesion_x /= same_count
            cohesion_y /= same_count
            align_x /= same_count
            align_y /= same_count

            self.steer_towards(cohesion_x, cohesion_y, COHESION_FORCE)
            self.add_force(
                (align_x - self.vx) * ALIGNMENT_FORCE * self.personality,
                (align_y - self.vy) * ALIGNMENT_FORCE * self.personality,
            )

        self.add_force(separation_x * SEPARATION_FORCE, separation_y * SEPARATION_FORCE)
        self.apply_wall_avoidance()

    def integrate(self):
        self.vx += self.ax
        self.vy += self.ay

        self.vx *= FRICTION
        self.vy *= FRICTION

        speed = math.hypot(self.vx, self.vy)
        if speed > MAX_SPEED:
            self.vx = self.vx / speed * MAX_SPEED
            self.vy = self.vy / speed * MAX_SPEED

        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx) * 0.8
        elif self.x + self.radius > GAME_WIDTH:
            self.x = GAME_WIDTH - self.radius
            self.vx = -abs(self.vx) * 0.8

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.8
        elif self.y + self.radius > GAME_HEIGHT:
            self.y = GAME_HEIGHT - self.radius
            self.vy = -abs(self.vy) * 0.8

        self.reset_forces()

    @staticmethod
    def collide(a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        dist_sq = dx * dx + dy * dy
        contact_dist = a.radius + b.radius
        return dist_sq < contact_dist * contact_dist

    @staticmethod
    def separate(a, b):
        dx = b.x - a.x
        dy = b.y - a.y
        dist = math.hypot(dx, dy)

        if dist < 1e-6:
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            dist = math.hypot(dx, dy)

        overlap = (a.radius + b.radius) - dist
        if overlap <= 0:
            return

        nx = dx / dist
        ny = dy / dist

        push = overlap * 0.55
        a.x -= nx * push
        a.y -= ny * push
        b.x += nx * push
        b.y += ny * push

        a.vx -= nx * 0.08
        a.vy -= ny * 0.08
        b.vx += nx * 0.08
        b.vy += ny * 0.08

    @staticmethod
    def resolve(a, b):
        if a.kind == b.kind:
            return False

        if beats(a.kind, b.kind):
            winner = a
            loser = b
        else:
            winner = b
            loser = a

        loser.kind = winner.kind

        angle = random.uniform(0, math.tau)
        loser.vx += math.cos(angle) * 0.35
        loser.vy += math.sin(angle) * 0.35
        winner.vx -= math.cos(angle) * 0.12
        winner.vy -= math.sin(angle) * 0.12

        return True
