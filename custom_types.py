from dataclasses import dataclass
from enum import Enum


@dataclass
class MoveDirection:
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(direction: tuple[int, int]) -> tuple[int, int]:
        if direction == MoveDirection.UP:
            return MoveDirection.DOWN
        elif direction == MoveDirection.DOWN:
            return MoveDirection.UP
        elif direction == MoveDirection.LEFT:
            return MoveDirection.RIGHT
        return MoveDirection.LEFT


DIRECTION_LIST = (MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT)

    
class EnemyType(Enum):
    CHASER = 0
    WAYCUTTER = 1
    COMPLEXONE = 2
    SCAREDYCAT = 3

