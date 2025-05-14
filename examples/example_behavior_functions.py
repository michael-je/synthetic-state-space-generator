from sssg.custom_types import *


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


def tictactoe_transposition_space_function(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """A 2-degree polynomial to approximate the transposition space at each depth"""
    x = depth
    a, b, c, C = - 44, 0, 1575, 5.9
    y = int(a*(x-C)**2 + (x-c)*b + c)
    return y


def tictactoe_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Simulates how the branching factor reduces by 1 with every s"""
    if (params.self.depth >= params.globals.terminal_minimum_depth and
        randf() < params.globals.terminal_chance):
        return 0
    return 9 - params.self.depth