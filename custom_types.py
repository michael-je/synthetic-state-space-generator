from typing import Protocol
from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass


class Player(Enum):
    MAX = 1
    MIN = -1

class RandomnessDistribution(Enum):
    UNIFORM = 0
    GAUSSIAN = 1
    # TODO: more distributions?

@dataclass
class GlobalVariables:
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
    cycle_chance: float
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
    globals: GlobalVariables
    parent: StateParamsParent|None
    self: StateParamsSelf
    siblings: StateParamsSiblings|None

# use Protocol to support type hints for keyword argument
class RandomFloatFunction(Protocol):
    def __call__(self, low: float=..., high: float=..., distribution: RandomnessDistribution|None=...) -> float: ...
class RandomIntFunction(Protocol):
    def __call__(self, low: int=..., high: int=..., distribution: RandomnessDistribution|None=...) -> int: ...
BranchingFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]
ChildValueFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]
ChildDepthFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]
TranspositionSpaceFunction = Callable[[RandomIntFunction, RandomFloatFunction, int], dict[int, int]]
HeuristicValueFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]

@dataclass
class GlobalFunctions:
    branching_function: BranchingFunction
    child_value_function: ChildValueFunction
    child_depth_function: ChildDepthFunction
    transposition_space_map: dict[int, int]
    heuristic_value_function: HeuristicValueFunction

@dataclass
class GlobalParameters:
    vars: GlobalVariables
    funcs: GlobalFunctions
    retain_tree: bool
