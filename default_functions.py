from custom_types import *
from constants import ID_BITS_SIZE
from utils import bit_size


def default_branching_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Generates a binary tree."""
    return 2

def default_child_value_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Randomly generate a value of either 0 or 1."""
    return int(randf() * 2)

def default_child_depth_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Ensures no cycles, and an even stride."""
    return info_dump.self.depth + 1

def default_transposition_space_function(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Maximum number of different states per depth, ensuring minimal transpositions."""
    max_states = 1 << (ID_BITS_SIZE - bit_size(max_depth))
    constant_states_per_depth = max_states // max_depth
    return {d: constant_states_per_depth for d in range(max_depth)}
