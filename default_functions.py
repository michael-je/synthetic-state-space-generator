from custom_types import *
from constants import *
from utils import *

import math


def default_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
    """Constant branching factor with variance. Does not allow a branching factor < 0 until a depth 
    of terminal_minimum_depth has been reached."""
    variance = randf(low=-params.globals.branching_factor_variance, high=params.globals.branching_factor_variance)
    branching_factor = max(0, params.globals.branching_factor_base + round(variance))
    # make sure we do not prematurely create a terminal
    if params.self.depth < params.globals.terminal_minimum_depth:
        branching_factor = min(1, branching_factor)
    return branching_factor


def default_child_true_value_function(
        randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams, 
        self_branching_factor: int, child_true_value_information: ChildTrueValueInformation) -> int:
    """Generates a true value for a child state. Ensures that the values behave in a sensible
    manner by adhering to the following rules:
      1. If we are a winning state, then at least some fixed number of our children must 
        share our value. The rest of the children can have any values.
      2. If we are a tied state, then at least some fixed number of our children must share 
         our value. The rest of the children can either be ties, or be losses for us.
      3. If we are a losing state, then all of our children must share our value.
    A more detailed explanation can be found in the documentation."""
    self_win = 1 if params.self.player == Player.MAX else -1
    self_loss = -self_win
    # no winning moves 
    if params.self.true_value == self_loss:
        return self_loss
    # if we are a tie, at least true_value_forced_ratio children must be a tie. The rest are losses
    elif params.self.true_value == 0:
        child_tie_ratio =  child_true_value_information.total_child_ties / self_branching_factor
        if child_tie_ratio < params.globals.true_value_forced_ratio:
            return 0
        if randf() < params.globals.true_value_tie_chance:
            return 0
        return self_loss
    # else, we are a win
    else:
        # in that case, at least true_value_forced_ratio children must be wins.
        child_win_ratio =  child_true_value_information.total_child_wins / self_branching_factor
        if child_win_ratio < params.globals.true_value_forced_ratio:
            return self_win
        # then we check if we are a tie
        if randf() < params.globals.true_value_tie_chance:
            return 0
        # if not a tie, we check if we should be the same as our parent or not
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


# TODO: test
def default_heuristic_value_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> float:
    """Simulates a heuristic function whose accuracy is dependant on:
    1. heuristic_accuracy_base: Baseline accuracy of the function. Lower values give greatly less accuracy
       while larger values give near perfect accuracy.
    2. heuristic_depth_scaling: Scales the accuracy relative to the depth of the state in the graph. Shallow
       states give less accurate evaluations, while deeper states are more accurate.
    3. heuristic_locality_scaling: Scales the accuracy relative to the states position in the record space.
       This helps simulate the heuristic evaluation function's ability to evaluate certain states over others. """
    # calculate the state's relative depth and record to the whole.
    relative_depth = params.self.depth / params.globals.max_depth
    relative_record = params.self.transposition_space_record / params.self.transposition_space_size
    # use that, and the global scaling factors to estimate 'accuracy' variables in ranges [-1, 1] where
    # -1 represents the most possible INACCURACY and 1 represents the most possible ACCURACY.
    depth_accuracy = params.globals.heuristic_depth_scaling * (2 * relative_depth - 1 )
    locality_accuracy = params.globals.heuristic_locality_scaling * math.sin(relative_record * 2 * math.pi)
    # based on accuracy parameters, there is some probability that the heuristic will be completely wrong 
    # and choose a value at random.
    if randf() < 0.1 * (1 - params.globals.heuristic_accuracy_base) * (3 - depth_accuracy - locality_accuracy):
        return randf(-1, 1)
    # otherwise, we calculate an estimated heuristic value that is based off the true value of the state.
    # The accuracy of this estimate is also based off of the previous accuracy variables.
    # The final value is a random variable within some calculated upper and lower bounds.
    if params.self.true_value == 0:
        # if we are a tie, then the accuracy is centered around 0
        bound = (1 - params.globals.heuristic_accuracy_base) * (2 - depth_accuracy - locality_accuracy) / 4
        return randf(-bound, bound)
    # otherwise the center of the bounds is set closer to the true value. After finding the center, we calculate
    # the distances of the upper and lower bounds from the center. The amount of variance, as well as how
    # positively or negatively the bound is biased depends on the previously calculated accuracy variables.
    accuracy_mean = params.globals.heuristic_accuracy_base
    distance_from_mean_to_true_value = 1 - accuracy_mean
    positive_accuracy_range = distance_from_mean_to_true_value * (2 + depth_accuracy + locality_accuracy) / 4
    negative_accuracy_range = distance_from_mean_to_true_value - positive_accuracy_range
    positive_bound = params.self.true_value * (accuracy_mean + positive_accuracy_range)
    negative_bound = params.self.true_value * (accuracy_mean - negative_accuracy_range)
    return randf(min(positive_bound, negative_bound), max(positive_bound, negative_bound))
