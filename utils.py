from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass

TMAX_32BIT = 2**32 - 1

class Player(Enum):
    MAX = 1
    MIN = -1

@dataclass
class GlobalParameters:
    branching_function: Callable[[int, float], int]
    value_function: Callable[[int, float], int]
    transition_function: Callable [[int, int], int]
    max_depth: int
    max_states: int
    seed: int
    retain_tree: bool


def default_branching_function(depth: int, randf: float) -> int:
    """Generates a binary tree."""
    return 2

def default_value_function(parent_val: int, randf: float) -> int:
    """Randomly generate a value of either 0 or 1."""
    return int(randf * 2)

def default_transition_function(randint: int, max_states: int) -> int:
    return randint % max_states
