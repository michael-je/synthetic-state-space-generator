from sssg.SyntheticGraph import SyntheticGraph
from example_behavior_functions import *


tictactoeGraph = SyntheticGraph(
            max_depth=10,
            transposition_space_function=tictactoe_transposition_space_function,
            branching_function=branching_function_tictactoe,
            true_value_forced_ratio=0.5,
            true_value_tie_chance=0.2,
            true_value_similarity_chance=0.7,
            symmetry_factor=0.25,
            symmetry_frequency=0.2,
            terminal_minimum_depth=5,
            terminal_chance = 0.75,
        )


def connect_four_example_simple():
    """Example creation of synthetic Connect-4 graph. This is a simpler approximation
    than the more complex example below."""
    state = SyntheticGraph(
        max_depth = 42,
        branching_factor_base = 7,
        transposition_space_function = transposition_space_function_connect_four_simple,
        terminal_minimum_depth=7,
        terminal_chance=0.01,    # Assuming that 1% of states after the terminal minimum depth are terminal stats
        symmetry_factor=0.5,     # Double symmetry due to mirroring along the vertical center line
        symmetry_frequency=0.01, # Assuming that 1% states are reflections
    )


def connect_four_example_complex():
    """More complex version of the synthetic Connect-4 graph. This was made by studying 
    how the Connect-4 game-tree behaves, and uses functions where detailed and explicit 
    branching factor and transposition space have been calculated and implemented."""
    state = SyntheticGraph(
        max_depth = 42,
        branching_function = branching_function_connect_four_complex,
        transposition_space_function = transposition_space_function_connect_four_complex,
    )


def pgame_with_critical_moves():
    """Example implementation of a "P-game with critical moves" as described in 
    "Lookahead Pathology in Monte-Carlo Tree Search" By Nguyen and Ramanujan."""
    state = SyntheticGraph(
        branching_factor_base=20,
        branching_factor_variance=5,
        true_value_forced_ratio=0.001,   # Ensures at least one shared true value if we are a win
        true_value_tie_chance=0,         # p-game has no ties
    )
