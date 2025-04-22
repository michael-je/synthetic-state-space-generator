from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass


class Player(Enum):
    MAX = 1
    MIN = -1

@dataclass
class InfoPackageParent:
    id: int
    value: int
    depth: int
    branching_factor: int
@dataclass
class InfoPackageSelf:
    id: int
    value: int
    depth: int
    branching_factor: int|None
@dataclass
class InfoPackageSiblings:
    id: list[int]
    value: list[int]
    depth: list[int]
    branching_factor: Callable[[], list[int]]
# TODO: rename
@dataclass
class InfoPackage:
    parent: InfoPackageParent|None
    self: InfoPackageSelf
    siblings: InfoPackageSiblings|None
    max_depth: int

RandomIntFunc = Callable[[], int]
RandomFloatFunc = Callable[[], float]
BranchingFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoPackage], int]
ChildValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoPackage], int]
ChildDepthFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoPackage], int]
TranspositionSpaceFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], dict[int, int]]
HeuristicValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, InfoPackage], int]

@dataclass
class GlobalParameters:
    branching_function: BranchingFunc
    child_value_function: ChildValueFunc
    child_depth_function: ChildDepthFunc
    transposition_space_map: dict[int, int]
    heuristic_value_function: HeuristicValueFunc
    max_depth: int
    id_depth_bits_size: int
    seed: int
    retain_tree: bool
