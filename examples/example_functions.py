from .custom_types import *


def branching_function_midgame_heavy(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Generate a larger mid-game state space using a parabolic curve."""
    x = 2 * params.self.depth / params.globals.max_depth
    y = -(x-1)**2 + 1
    branching_factor = y * params.globals.branching_factor_base
    variance = (randf() - 0.5) * 2 * params.globals.branching_factor_variance
    branching_factor = int(max(0, branching_factor + round(variance)))
    # make sure we do not prematurely create a terminal
    if params.self.depth < params.globals.terminal_minimum_depth:
        branching_factor = min(1, branching_factor)
    return branching_factor


def branching_function_simple_constant(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Generates a tree with a constant branching factor."""
    return params.globals.branching_factor_base


def child_depth_function_random(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Generate children at any random depth."""
    return randint(low=0, high=params.globals.max_depth)


def transposition_space_function_simple_constant(randint: RandomIntFunction, randf: RandomFloatFunction, max_depth: int) -> int:
    """Allow only exactly 100 different states per depth."""
    return 100
