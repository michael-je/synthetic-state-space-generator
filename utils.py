from typing import Callable

from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass

class IdOverflow(Exception):
    pass
class PropertyNotSet(Exception):
    pass
class RootHasNoSiblings(Exception):
    pass
class RootHasNoParent(Exception):
    pass

HASH_OUTPUT_BIT_SIZE = 64
HASH_OUTPUT_TMAX = 2**HASH_OUTPUT_BIT_SIZE - 1
ID_BITS_SIZE = HASH_OUTPUT_BIT_SIZE - 1 # because Python only has signed ints

class Player(Enum):
    MAX = 1
    MIN = -1


RandomIntFunc = Callable[[], int]
RandomFloatFunc = Callable[[], float]
BranchingFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], int]
ChildValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], int]
ChildDepthFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], int]
TranspositionSpaceFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], dict[int, int]]

@dataclass
class GlobalParameters:
    branching_function: BranchingFunc
    child_value_function: ChildValueFunc
    child_depth_function: ChildDepthFunc
    transposition_space_map: dict[int, int]
    max_depth: int
    id_depth_bits_size: int
    seed: int
    retain_tree: bool

def bit_size(n: int) -> int:
    """Return the number of bits necessary to represent integer n in binary."""
    bits = 0
    while n:
        n >>= 1
        bits += 1
    return bits

# TODO: refactor so that randint and randf are accessible, and the first arguments of every function here
# TODO: maybe rather consider passing the RNG along with some exposed function, with a predetermined seed?
# this way the functions can generate as many random variables as they need, and we wouldn't have to calculate
# unnecessary and expensive uniform values, f.x -> after refactor to use single global hasher, pass
# a wrapped hashing function so that the function correctly uses the stateId -> after refactoring the hashing
# wrapper functions into state, just pass the state itself into the function
# TODO re-implement logic of discarded transition functions
def default_branching_function(randint: RandomIntFunc, randf: RandomFloatFunc, depth: int) -> int:
    """Generates a binary tree."""
    return 2

def default_child_value_function(randint: RandomIntFunc, randf: RandomFloatFunc, parent_val: int) -> int:
    """Randomly generate a value of either 0 or 1."""
    return int(randf() * 2)

def default_child_depth_function(randint: RandomIntFunc, randf: RandomFloatFunc, parent_depth: int) -> int:
    """Ensures no cycles, and an even stride."""
    return parent_depth + 1

# def default_transition_function(current_move_number: int, randint: int, max_states: int, max_depth: int) -> int:
#     """Generate children anywhere in the entire state space."""
#     return randint % max_states

def default_transposition_space_function(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Maximum number of different states per depth, ensuring minimal transpositions."""
    max_states = 1 << (ID_BITS_SIZE - bit_size(max_depth))
    constant_states_per_depth = max_states // max_depth
    return {d: constant_states_per_depth for d in range(max_depth)}

def transposition_space_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Example showing only 5 possible transpositions per depth."""
    constant_states_per_depth = 5
    return {d: constant_states_per_depth for d in range(max_depth)}

# def uniformly_binned_transitions(current_move_number: int, randint: int, max_states: int, max_depth: int) -> int:
#     """Generate children such that states are "binned" according to their move number.
#     This ensures that transpositions of states always have the same depth and eliminates cycles."""
#     binsize = max_states // max_depth
#     child_bin_start = binsize * current_move_number
#     child_id = randint % binsize
#     child_id += child_bin_start
#     return child_id

# def uniformly_binned_transitions_with_cycles(depth: int, randint: int, max_states: int, max_depth: int) -> int:
#     """Generate children such that states are "binned" according to their move number.
#     There is an added chance of a state creating a cycle up to an ancestor."""
#     binsize = max_states // max_depth
#     child_bin_start = binsize * depth + 1
#     if randint / TMAX_64BIT < 0.2:
#         child_bin_start -= ((randint % 3) + 1) * binsize
#         child_bin_start = max(0, child_bin_start)
#     child_id = randint % binsize
#     child_id += child_bin_start
#     return child_id