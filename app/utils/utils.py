import random

from app.core.config import COUNT_OBJECT, GAME_HEIGHT, GAME_WIDTH
from app.models.entity import Entity


def create_entities():
    entities = []
    types = ["rock", "paper", "scissors"]

    for _ in range(COUNT_OBJECT):
        entities.append(
            Entity(
                x=random.randint(0, GAME_WIDTH),
                y=random.randint(0, GAME_HEIGHT),
                vx=random.uniform(-2, 2),
                vy=random.uniform(-2, 2),
                kind=random.choice(types),
            )
        )
    return entities
