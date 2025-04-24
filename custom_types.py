from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass


class Player(Enum):
    MAX = 1
    MIN = -1

class RandomnessDistribution(Enum):
    UNIFORM = 0
    GAUSSIAN = 1
    # TODO: add more distributions?

@dataclass
class StateParamsGlobals:
    root_value: int
    seed: int
    max_depth: int
    distribution: RandomnessDistribution
    branching_factor_base: int
    branching_factor_variance: int
    terminal_minimum_depth: int
    # terminal_minimum_density: float
    # terminal_maximum_density: float
    value_minimum: int # TODO: change to float?
    value_maximum: int
    child_depth_minumum: int # depth can be negative
    child_depth_maximum: int
@dataclass
class StateParamsParent:
    id: int
    value: int
    depth: int
    branching_factor: int
@dataclass
class StateParamsSelf:
    id: int
    value: int
    depth: int
    branching_factor: int|None
@dataclass
class StateParamsSiblins:
    id: list[int]
    value: list[int]
    depth: list[int]
    branching_factor: Callable[[], list[int]]
# TODO: rename
@dataclass
class StateParams:
    globals: StateParamsGlobals
    parent: StateParamsParent|None
    self: StateParamsSelf
    siblings: StateParamsSiblins|None

RandomIntFunc = Callable[[], int]
RandomFloatFunc = Callable[[], float]
BranchingFunc = Callable[[RandomIntFunc, RandomFloatFunc, StateParams], int]
ChildValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, StateParams], int]
ChildDepthFunc = Callable[[RandomIntFunc, RandomFloatFunc, StateParams], int]
TranspositionSpaceFunc = Callable[[RandomIntFunc, RandomFloatFunc, int], dict[int, int]]
HeuristicValueFunc = Callable[[RandomIntFunc, RandomFloatFunc, StateParams], int]

@dataclass
class GlobalParameters:
    root_value: int
    seed: int
    max_depth: int
    distribution: RandomnessDistribution
    retain_tree: bool
    id_depth_bits_size: int
    branching_function: BranchingFunc
    child_value_function: ChildValueFunc
    child_depth_function: ChildDepthFunc
    transposition_space_map: dict[int, int]
    heuristic_value_function: HeuristicValueFunc
