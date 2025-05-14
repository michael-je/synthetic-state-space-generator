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


def branching_function_tictactoe(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Simulates how the branching factor reduces by 1 with every s"""
    if (params.self.depth >= params.globals.terminal_minimum_depth and
        randf() < params.globals.terminal_chance):
        return 0
    return 9 - params.self.depth


def branching_function_connect_four_complex(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Approximates the branching factor of the real Connect-4 game tree using hard-coded
    statistics gathered from analysis of actual game data.

    This function is intended for use in synthetic game graph generation and mimics the 
    observed distribution of branching factors at different depths of real Connect-4 
    gameplay. It provides branching behavior for depths 0 through 10, based on empirical 
    frequencies of nodes with 0, 6, or 7 children in the actual game graph. 
    
    This function is intended as a proof of concept and is not a complete model of 
    branching factor for Connect-4"""
    rand_num = randf()
    if params.self.depth < 6 :
        return 7
    match params.self.depth:
        case 6:
            if rand_num < 7/(7+16415):
                return 6
        case 7:
            if rand_num < 294/(294+728+53837):
                return 6
            if rand_num < (294+728)/(294+728+53837):
                return 0
        case 8:
            if rand_num < 4326/(4326+1892+178057):
                return 6
            if rand_num < (4326+1892)/(4326+1892+178057):
                return 0
        case 9:
            if rand_num < 31984/(31984+19412+506790):
                return 6
            if rand_num <  (31984+19412)/(31984+19412+506790):
                return 0
        case _:
            if rand_num < 157734/(157734+4425+1460664):
                return 6
            if rand_num < (157734+44225)/(157734+44225+1460664):
                return 0
    return 7


def transposition_space_function_connect_four_complex(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """Uses the statistics from the real game to explicitly make the transpositon space 
    behave correctly in the synthetic game graph. Only has information on the first 10 
    levels of Connect-4 
    
    This function is intended as a proof of concept and is not a complete model of 
    transposition space for Connect-4"""
    trans_map = {0: 1,
                 1: globals.max_transposition_space_size,  # No transpositions
                 2: globals.max_transposition_space_size,
                 3: 438,
                 4: 1950,
                 5: 5708,
                 6: 22209,
                 7: 66822,
                 8: 227191,
                 9: 649959,
                 10: 1662623} 
    return trans_map[depth]


def transposition_space_function_connect_four_simple(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """Simple transposition space function, which uses an estimation of the 
    transposition-space at each level"""
    if depth <= 1:
        return globals.max_transposition_space_size # No transpositions when depth < 2
    else:
        return (4 ** (depth - 2)) * (7 ** 2)