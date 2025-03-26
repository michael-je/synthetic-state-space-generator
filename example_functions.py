from custom_types import *


def child_depth_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Generate children anywhere in the entire state space."""
    return randint() % info_dump.max_depth

def child_depth_function_example_2(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Allows children to create cycles by a few levels."""
    if info_dump.parent is None:
        return 1
    if randf() < 0.1:
        return int(max(1, info_dump.self.depth - 3))
    return info_dump.self.depth + 1

def transposition_space_function_example_1(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Example showing only 5 possible transpositions per depth."""
    constant_states_per_depth = 10
    return {d: constant_states_per_depth for d in range(max_depth)}
