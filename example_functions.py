from custom_types import *


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
    """Generate children anywhere in the entire state space."""
    return randint(low=0, high=params.globals.max_depth)


def child_depth_function_cycles_allowed(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Allows children to create cycles by a few levels."""
    if params.parent is None:
        return 1
    if randf() < params.globals.cycle_chance:
        return int(max(1, params.self.depth - 3))
    return params.self.depth + 1


def transposition_space_function_simple_constant(randint: RandomIntFunction, randf: RandomFloatFunction, max_depth: int) -> dict[int, int]:
    """Example showing only 5 possible transpositions per depth."""
    max_states_per_depth = 10
    return {d: max_states_per_depth for d in range(max_depth)}


def tictactoe_transposition_space_function(randint: RandomIntFunction, randf: RandomFloatFunction, max_depth: int) -> dict[int, int]:
    """Example tictactoe transposition space function"""
    tsf = {0:1, 1:9, 2:72, 3:252, 4:756, 5:1260, 6:1520, 7:1140, 8:390, 9:78}
    #tsf = {0:1, 1:9+3, 2:72+35, 3:252+100, 4:756+250, 5:1260+160, 6:1520+120, 7:1140+30, 8:390+50, 9:78+25}
    return tsf

def tictactoe_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """simulates branching factor of tictactoe (function of depth)"""
    currDepth = params.self.depth
    terminalDensityDistribution = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.10526315789473684,
        6: 0.10787172011661808,
        7: 0.6379310344827587,
        8: 0.7567567567567568,
        9: 1.0
    }
    if terminalDensityDistribution[currDepth] > randf():
        return 0
    
    return 9 - params.self.depth

def tictactoe_child_value_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Randomly generate a value of either -1, 0, 1 according to the true value distro of tictactoe"""
    valueCountPerDepth = {
        0: [0, 1, 0],
        1: [0, 9, 0],
        2: [0, 24, 48],
        3: [50, 138, 64],
        4: [36, 136, 584],
        5: [540, 264, 456],
        6: [264, 200, 1056],
        7: [416, 200, 524],
        8: [168, 80, 142],
        9: [0, 16, 62]
    }
    valueDistribution = {
        0: [0.0, 1.0, 0.0],
        1: [0.0, 1.0, 0.0],
        2: [0.0, 0.3333333333333333, 0.6666666666666666],
        3: [0.1984126984126984, 0.5476190476190477, 0.25396825396825395],
        4: [0.047619047619047616, 0.17989417989417988, 0.7724867724867724],
        5: [0.42857142857142855, 0.20952380952380953, 0.3619047619047619],
        6: [0.1736842105263158, 0.13157894736842105, 0.6947368421052632],
        7: [0.3649122807017544, 0.17543859649122806, 0.45964912280701753],
        8: [0.4307692307692308, 0.20512820512820512, 0.3641025641025641],
        9: [0.0, 0.20512820512820512, 0.7948717948717948]
    }

    pNeg, pZero, pPos = valueDistribution[params.self.depth+1]
    r = randf()
    if r <= pNeg:
        return -1
    elif pNeg < r < pNeg + pZero:
        return 0
    else:
        return 1
