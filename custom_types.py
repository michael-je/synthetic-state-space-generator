from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass


class Player(Enum):
    MAX = 1
    MIN = -1

class RandomnessDistribution(Enum):
    UNIFORM = 0
    GAUSSIAN = 1
    GEOMETRIC = 2
    PARABOLIC = 3
    # TODO: more distributions?

@dataclass
class GlobalVars:
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
    id_depth_bits_size: int
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
class StateParamsSiblings:
    id: list[int]
    value: list[int]
    depth: list[int]
    branching_factor: Callable[[], list[int]]
# TODO: rename
@dataclass
class StateParams:
    globals: GlobalVars
    parent: StateParamsParent|None
    self: StateParamsSelf
    siblings: StateParamsSiblings|None

RandomIntFuncion = Callable[[], int]
RandomFloatFunction = Callable[[], float]
BranchingFunction = Callable[[RandomIntFuncion, RandomFloatFunction, StateParams], int]
ChildValueFunction = Callable[[RandomIntFuncion, RandomFloatFunction, StateParams], int]
ChildDepthFunction = Callable[[RandomIntFuncion, RandomFloatFunction, StateParams], int]
TranspositionSpaceFunction = Callable[[RandomIntFuncion, RandomFloatFunction, int], dict[int, int]]
HeuristicValueFunction = Callable[[RandomIntFuncion, RandomFloatFunction, StateParams], int]

@dataclass
class GlobalFuncs:
    branching_function: BranchingFunction
    child_value_function: ChildValueFunction
    child_depth_function: ChildDepthFunction
    transposition_space_map: dict[int, int]
    heuristic_value_function: HeuristicValueFunction

@dataclass
class GlobalParameters:
    vars: GlobalVars
    funcs: GlobalFuncs
    retain_tree: bool
