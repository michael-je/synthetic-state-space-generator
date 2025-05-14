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


def connect_four_branching_function_complex(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Uses the statistics from the real game to explicitly make the branching factor behave correctly in the synthetic game graph.
    Only has information on the first 10 levels of Connect-4, and only serves as a proof of concept."""
    rand_num = randf()
    if params.self.depth < 6 :
        return 7
    elif params.self.depth == 6 :
        if rand_num < 7/(7+16415):
            return 6
        return 7
    elif params.self.depth == 7 :
        if rand_num < 294/(294+728+53837):
            return 6
        elif rand_num < (294+728)/(294+728+53837):
            return 0
        return 7
    elif params.self.depth == 8 :
        if rand_num < 4326/(4326+1892+178057):
            return 6
        elif rand_num <  (4326+1892)/(4326+1892+178057):
            return 0
        return 7
    elif params.self.depth == 9 :
        if rand_num < 31984/(31984+19412+506790):
            return 6
        elif rand_num <  (31984+19412)/(31984+19412+506790):
            return 0
        return 7
    else:
        if rand_num < 157734/(157734+4425+1460664):
            return 6
        elif rand_num < (157734+44225)/(157734+44225+1460664):
            return 0
        return 7



def connect_four_transposition_space_function_complex(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """Uses the statistics from the real game to explicitly make the transpositon space behave correctly in the synthetic game graph.
    Only has information on the first 10 levels of Connect-4, but serves as a proof of concept"""
    trans_map = {0: 1,
                 1: 100000,  # Large transposition space size at this level, so likely no transpositions
                 2: 100000,  # Large transposition space size at this level, so likely no transpositions
                 3: 438,     # Having the size of the transposition space as 438, gives us expected 238 unique states, which is derived from the real game.
                 4: 1950,    # Having the size of the transposition space as 1950, gives us expected 1120 unique states, which is derived from the real game.
                 5: 5708,    # gets us the expected number of unique states, derived from the real game of Connect-4
                 6: 22209,   # gets us the expected number of unique states, derived from the real game of Connect-4
                 7: 66822,   # gets us the expected number of unique states, derived from the real game of Connect-4
                 8: 227191,  # gets us the expected number of unique states, derived from the real game of Connect-4
                 9: 649959,  # gets us the expected number of unique states, derived from the real game of Connect-4
                 10: 1662623 # gets us the expected number of unique states, derived from the real game of Connect-4
                 }
    
    return trans_map[depth]


def connect_four_transposition_space_function_simple(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """Simple transposition space function, which uses an estimation of the transposition-space at each level"""
    if depth <= 1:
        return 100000 # No transpositions when depth=0 and depth=1.
    else:
        return (4 ** (depth - 2)) * (7 ** 2) # Estimation of the state-space at each depth of the graph.