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


@dataclass
class InfoDumpParent:
    id: int
    value: int
    depth: int
    branching_factor: int
@dataclass
class InfoDumpSelf:
    id: int
    value: int
    depth: int
    branching_factor: int|None
@dataclass
class InfoDumpSiblings:
    id: list[int]
    value: list[int]
    depth: list[int]
    branching_factor: Callable[[], list[int]]
# TODO: rename
@dataclass
class InfoDump:
    parent: InfoDumpParent|None
    self: InfoDumpSelf
    siblings: InfoDumpSiblings|None
    max_depth: int

RandomIntFunc = Callable[[], int]
RandomFloatFunc = Callable[[], float]
BranchingFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoDump], int]
ChildValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoDump], int]
ChildDepthFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoDump], int]
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

def default_branching_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Generates a binary tree."""
    return 2

def default_child_value_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Randomly generate a value of either 0 or 1."""
    return int(randf() * 2)

def default_child_depth_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Ensures no cycles, and an even stride."""
    return info_dump.self.depth + 1

def child_depth_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Generate children anywhere in the entire state space."""
    return randint() % info_dump.max_depth

def child_depth_function_example_2(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Allows children to create cycles by a few levels."""
    if info_dump.parent is None:
        return 1
    if randf() < 0.1:
        return max(1, info_dump.self.depth - 3)
    return info_dump.self.depth + 1

def default_transposition_space_function(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Maximum number of different states per depth, ensuring minimal transpositions."""
    max_states = 1 << (ID_BITS_SIZE - bit_size(max_depth))
    constant_states_per_depth = max_states // max_depth
    return {d: constant_states_per_depth for d in range(max_depth)}

def transposition_space_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Example showing only 5 possible transpositions per depth."""
    constant_states_per_depth = 10
    return {d: constant_states_per_depth for d in range(max_depth)}
