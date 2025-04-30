from custom_types import *
from constants import ID_BITS_SIZE
from utils import bit_size


def default_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Constant branching factor with variance."""
    variance = randf(low=-params.globals.branching_factor_variance, high=params.globals.branching_factor_variance)
    branching_factor = max(0, params.globals.branching_factor_base + round(variance))
    # make sure we do not prematurely create a terminal
    if params.self.depth < params.globals.terminal_minimum_depth:
        branching_factor = min(1, branching_factor)
    return branching_factor


def default_child_value_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Randomly generate a value between minimum and maximum."""
    return randint(low=params.globals.value_minimum, high=params.globals.value_maximum)


def default_child_depth_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Randomly generate a depth between minimum and maximum depth."""
    min_depth = max(params.globals.child_depth_minumum + params.self.depth, 0)
    max_depth = min(params.globals.child_depth_maximum + params.self.depth, params.globals.max_depth)
    return randint(low=min_depth, high=max_depth)


def default_transposition_space_function(randint: RandomIntFunction, randf: RandomFloatFunction, max_depth: int) -> dict[int, int]:
    """Maximum number of different states per depth, ensuring minimal transpositions."""
    max_states = 1 << (ID_BITS_SIZE - bit_size(max_depth))
    constant_states_per_depth = max_states // max_depth
    return {d: constant_states_per_depth for d in range(max_depth)}


def default_heuristic_value_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Simulates a heuristic function with 70%-85% accuracy depending on depth."""
    accuracy = 0.7 + (0.15 * params.self.depth / params.globals.max_depth)
    return params.self.value if randf() < accuracy else -params.self.value
