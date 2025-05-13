from typing import Protocol
from enum import Enum
from collections.abc import Callable
from dataclasses import dataclass

class RandomnessDistribution(Enum):
    UNIFORM = 0
    GAUSSIAN = 1

class Player(Enum):
    MIN = 0
    MAX = 1

@dataclass
class ChildTrueValueInformation:
    total_children_generated: int=0
    total_child_wins: int=0
    total_child_losses: int=0
    total_child_ties: int=0
@dataclass
class GlobalVariables:
    seed: int
    max_depth: int
    distribution: RandomnessDistribution
    branching_factor_base: int
    branching_factor_variance: int
    terminal_minimum_depth: int
    child_depth_minumum: int # depth can be negative
    child_depth_maximum: int
    locality_grouping: float
    true_value_forced_ratio: float
    true_value_similarity_chance: float
    true_value_tie_chance: float
    symmetry_factor: float
    symmetry_frequency: float
    heuristic_accuracy_base: float
    heuristic_depth_scaling: float
    heuristic_locality_scaling: float
    max_transposition_space_size: int
@dataclass
class StateParamsSelf:
    id: int
    true_value: int
    player: Player
    depth: int
    transposition_space_record: int
    transposition_space_size: int
@dataclass
class StateParams:
    globals: GlobalVariables
    self: StateParamsSelf

# use Protocol to support type hints for keyword argument
class RandomFloatFunction(Protocol):
    def __call__(self, low: float=..., high: float=..., distribution: RandomnessDistribution|None=...) -> float: ...
class RandomIntFunction(Protocol):
    def __call__(self, low: int=..., high: int=..., distribution: RandomnessDistribution|None=...) -> int: ...
BranchingFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]
ChildTrueValueFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams, int, ChildTrueValueInformation], int]
ChildDepthFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], int]
TranspositionSpaceFunction = Callable[[RandomIntFunction, RandomFloatFunction, GlobalVariables, int], int]
HeuristicValueFunction = Callable[[RandomIntFunction, RandomFloatFunction, StateParams], float]

@dataclass
class GlobalFunctions:
    branching_function: BranchingFunction
    child_true_value_function: ChildTrueValueFunction
    child_depth_function: ChildDepthFunction
    transposition_space_function: TranspositionSpaceFunction
    heuristic_value_function: HeuristicValueFunction

@dataclass
class GlobalParameters:
    vars: GlobalVariables
    funcs: GlobalFunctions
