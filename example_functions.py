from custom_types import *


def branching_function_midgame_heavy(randint: RandomIntFunc, randf: RandomFloatFunc, params: StateParams) -> int:
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


# def child_depth_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, params: StateParams) -> int:
#     """Generate children anywhere in the entire state space."""
#     return randint() % params.globals.max_depth

# def child_depth_function_example_2(randint: RandomIntFunc, randf: RandomFloatFunc, params: StateParams) -> int:
#     """Allows children to create cycles by a few levels."""
#     if params.parent is None:
#         return 1
#     if randf() < 0.1:
#         return int(max(1, params.self.depth - 3))
#     return params.self.depth + 1

# def transposition_space_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
#     """Example showing only 5 possible transpositions per depth."""
#     constant_states_per_depth = 10
#     return {d: constant_states_per_depth for d in range(max_depth)}
