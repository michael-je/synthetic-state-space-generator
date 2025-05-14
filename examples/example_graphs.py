from sssg.SyntheticGraph import SyntheticGraph
from sssg.custom_types import *
from queue import deque



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

tictactoeGraph = SyntheticGraph(
            max_depth=10,
            transposition_space_function=tictactoe_transposition_space_function,
            branching_function=tictactoe_branching_function,
            true_value_forced_ratio=0.5,
            true_value_tie_chance=0.2,
            true_value_similarity_chance=0.7,
            symmetry_factor=0.35,
            symmetry_frequency=0.2,
            terminal_minimum_depth=5,
            terminal_chance = 0.75,
        )


