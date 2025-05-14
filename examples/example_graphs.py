from sssg.SyntheticGraph import SyntheticGraph
from example_behavior_functions import *


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


