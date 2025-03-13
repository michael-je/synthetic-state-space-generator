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
    transition_function: Callable [[int, int, int, int], int]
    max_depth: int
    max_states: int
    seed: int
    retain_tree: bool


# TODO: refactor so that randint and randf are accessible, and the first arguments of every function here
def default_branching_function(depth: int, randf: float) -> int:
    """Generates a binary tree."""
    return 2

def default_value_function(parent_val: int, randf: float) -> int:
    """Randomly generate a value of either 0 or 1."""
    return int(randf * 2)

def default_transition_function(current_move_number: int, randint: int, max_states: int, max_depth: int) -> int:
    """Generate children anywhere in the entire state space."""
    return randint % max_states

def uniformly_binned_transitions(current_move_number: int, randint: int, max_states: int, max_depth: int) -> int:
    """Generate children such that states are "binned" according to their move number.
    This ensures that transpositions of states always have the same depth and eliminates cycles."""
    binsize = max_states // max_depth
    child_bin_start = binsize * current_move_number
    child_id = randint % binsize
    child_id += child_bin_start
    return child_id

def uniformly_binned_transitions_with_cycles(current_move_number: int, randint: int, max_states: int, max_depth: int) -> int:
    """Generate children such that states are "binned" according to their move number.
    There is an added chance of a state creating a cycle up to an ancestor."""
    binsize = max_states // max_depth
    child_bin_start = binsize * current_move_number + 1
    if randint / TMAX_32BIT < 0.2:
        child_bin_start -= ((randint % 3) + 1) * binsize
        child_bin_start = max(0, child_bin_start)
    child_id = randint % binsize
    child_id += child_bin_start
    return child_id