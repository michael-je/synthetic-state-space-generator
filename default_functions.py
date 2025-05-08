from custom_types import *
from constants import *
from utils import *

# TODO: make sure default functions are behaving the same after refactor

def default_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Constant branching factor with variance."""
    variance = randf(low=-params.globals.branching_factor_variance, high=params.globals.branching_factor_variance)
    branching_factor = max(0, params.globals.branching_factor_base + round(variance))
    # make sure we do not prematurely create a terminal
    if params.self.depth < params.globals.terminal_minimum_depth:
        branching_factor = min(1, branching_factor)
    return branching_factor


def default_child_value_function(
        randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams, 
        self_branching_factor: int, sibling_value_information: SiblingValueInformation) -> int:
    """""" # TODO: docstring
    self_win = 1 if params.self.player == Player.MAX else -1
    self_loss = -self_win
    # no winning moves 
    if params.self.true_value == self_loss:
        return self_loss
    # if we are a tie, at least true_value_forced_ratio children must be a tie
    if params.self.true_value == 0:
        sibling_tie_ratio =  sibling_value_information.total_sibling_ties / self_branching_factor
        if sibling_tie_ratio < params.globals.true_value_forced_ratio:
            return 0
        if randf() < params.globals.true_value_tie_chance:
            return 0
        return self_loss
    # else, if we are a win, at least true_value_forced_radio children must be wins
    sibling_win_ratio =  sibling_value_information.total_sibling_wins / self_branching_factor
    if sibling_win_ratio < params.globals.true_value_forced_ratio:
        return self_win
    if randf() < params.globals.true_value_tie_chance:
        return 0
    if randf() < params.globals.true_value_similarity_chance:
        return self_win
    return self_loss


def default_child_depth_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Randomly generate a depth between minimum and maximum depth."""
    min_depth = max(params.globals.child_depth_minumum + params.self.depth, 0)
    max_depth = min(params.globals.child_depth_maximum + params.self.depth, params.globals.max_depth)
    return randint(low=min_depth, high=max_depth)


def default_transposition_space_function(randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
    """Maximum number of different states per depth, ensuring minimal transpositions."""
    return globals.max_transposition_space_size


def default_heuristic_value_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Simulates a heuristic function with 70%-85% accuracy depending on depth."""
    accuracy = 0.7 + (0.15 * params.self.depth / params.globals.max_depth)
    # TODO: might need to change how Value is encoded, need in range [-1, 1]
    return params.self.true_value if randf() < accuracy else -params.self.true_value
