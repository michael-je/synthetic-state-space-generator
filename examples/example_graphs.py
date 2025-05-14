from sssg.SyntheticGraph import SyntheticGraph
from examples.example_behavior_functions import *


state = SyntheticGraph()


def connect_four_example_simple():
    """Example creation of synthetic Connect-4 graph. This is a simple and naive approximation of the graph.
    For more detailed and accurate Connect-4 graph, see the connect_four_example_complex() function"""
    state = SyntheticGraph(
        max_depth = 42, #Maximum depth of Connect-4 graph is 42
        branching_factor_base = 7, #Estimating the branching factor to be constant 7. 
        transposition_space_function = connect_four_transposition_space_function_simple, # Simple function which 
        terminal_minimum_depth=7, #Assuming th
        terminal_chance=0.01, #Assuming that 1% of states after the terminal minimum depth are terminal stats
        symmetry_factor=0.5, #Double symmetry due to mirror along the vertical center line
        symmetry_frequency=0.01, #Assuming that 1% states are reflections
    )

def connect_four_example_complex():
    """More complex version of the synthetic Connect-4 graph. This was made by studying how the Connect-4 game-tree behaves, 
    and uses functions where detailed and explicit branching factor and transposition space have been calculated and implemented.
    """
    state = SyntheticGraph(
        max_depth = 42,
        branching_function = connect_four_branching_function_complex,
        transposition_space_function = connect_four_transposition_space_function_complex,
    )