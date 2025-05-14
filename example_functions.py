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



def branching_function_connect_four(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    rand_num = randf()
    bf = [
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 7],
    [0, 0, 0, 0, 0, 0, 0, 49],
    [0, 0, 0, 0, 0, 0, 0, 238],
    [0, 0, 0, 0, 0, 0, 0, 1120],
    [0, 0, 0, 0, 0, 0, 0, 4263],
    [0, 0, 0, 0, 0, 0, 7, 16415],
    [728, 0, 0, 0, 0, 0, 294, 53837],
    [1892, 0, 0, 0, 0, 0, 4326, 178057],
    [19412, 0, 0, 0, 0, 0, 31984, 506790]]

    if params.self.depth <6 :
        return 7
    
    if params.self.depth == 6 :
        if rand_num < 7/(7+16415):
            return 6
        return 7
    if params.self.depth == 7 :
        if rand_num < 294/(294+728+53837):
            return 6
        elif rand_num < (294+728)/(294+728+53837):
            return 0
        return 7
    if params.self.depth == 8 :
        if rand_num < 4326/(4326+1892+178057):
            return 6
        elif rand_num <  (4326+1892)/(4326+1892+178057):
            return 0
        return 7
    if params.self.depth == 9 :
        if rand_num < 31984/(31984+19412+506790):
            return 6
        elif rand_num <  (31984+19412)/(31984+19412+506790):
            return 0
        return 7
    else:
        if rand_num < 157734/(157734+4425+1460664):
            return 6
        elif rand_num <  (157734+44225)/(157734+44225+1460664):
            return 0
        return 7
    


def transposition_space_function_connect_four(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:

    trans_map = {0: 1,
                 1: 7+100000, #no transpotitions
                 2: 49+100000, #no transpositions
                 3: 238,
                 4: 574+546,
                 5: 1456+2037+770,
                 6: 5628+8169+2625,
                 7: 13776+24318+14525+2240,
                 8: 47712+84693+45955+5915,
                 9: 112860+226032+172436+44167+2691,
                 10: 333903+705918+503471+113373+5958   
                 }
    
    return trans_map[depth]



def transposition_space_function_connect_four_expectation(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:

    trans_map = {0: 1,
                 1: 7+100000, #no transpotitions
                 2: 49+100000, #no transpositions
                 3: 438, #238 expectation,
                 4: 1950, #574+546 expectation,
                 5: 5708, #1456+2037+770 expectation,
                 6: 22209, #5628+8169+2625 expectation,
                 7: 66822, #13776+24318+14525+2240 expectation,
                 8: 227191, #47712+84693+45955+5915 expectation,
                 9: 649959, #112860+226032+172436+44167+2691 expectation,
                 10: 333903+705918+503471+113373+5958   
                 }
    
    return trans_map[depth]

def transposition_space_function_connect_four_2(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    forced_ratio = globals.true_value_forced_ratio #0.1
    similarity_chance = globals.true_value_similarity_chance #0.5
    tie_chance = globals.true_value_tie_chance #0.2
    
    trans_map = {0: 1,
                 1: 7+100000, #no transpotitions
                 2: 49+100000, #no transpositions
                 3: 438*(1-tie_chance)*(1-similarity_chance), #238 expectation,
                 4: 1950*(1-tie_chance)*(1-similarity_chance), #574+546 expectation,
                 5: 5708*(1-tie_chance)*(1-similarity_chance), #1456+2037+770 expectation,
                 6: 22209*(1-tie_chance)*(1-similarity_chance), #5628+8169+2625 expectation,
                 7: 66822*(1-tie_chance)*(1-similarity_chance), #13776+24318+14525+2240 expectation,
                 8: 227191*(1-tie_chance)*(1-similarity_chance), #47712+84693+45955+5915 expectation,
                 9: 649959*(1-tie_chance)*(1-similarity_chance), #112860+226032+172436+44167+2691 expectation,
                 10: 333903+705918+503471+113373+5958   
                 }
    
    return int(trans_map[depth])

def transposition_space_function_connect_four_3(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    pass