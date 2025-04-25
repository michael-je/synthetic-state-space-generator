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


def transposition_space_function_tictactoe(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Example showing only 5 possible transpositions per depth."""
    
    trans_map = {0: 1,
                 1: 100000, #No transpositions at this level
                 2: 100000, #No transpositions at this level
                 3: 252,    # 252 unique boards at this level
                 4: 756,    # -||- unique boards at this level
                 5: 1260,   # -||- unique boards at this level
                 6: 1520,   # -||- unique boards at this level
                 7: 1248,   # -||- unique boards at this level
                 8: 966,    # -||- unique boards at this level
                 9: 78,     # -||- unique boards at this level
                 }
    

    return trans_map


def branching_function_tictactoe(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
        if info_dump.self.depth < 5:
            return 9 - info_dump.self.depth
        
        if info_dump.self.depth == 5:
            if randf() < 0.105:
                return 0
            return 4
        if info_dump.self.depth == 6:
            if randf() < 0.107:
                return 0
            return 3
        if info_dump.self.depth == 7:
            # 63.8% return 0 else return 2
            if randf() < 0.638:
                return 0
            return 2
        if info_dump.self.depth == 8:
            #75.7% return 0 else return 1
            if randf() < 0.757:
                return 0
            return 1
        if  info_dump.self.depth == 9:
            return 0
        return 0
        




def branching_function_connect_four(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    if info_dump.self.depth < 5:
        return 9 - info_dump.self.depth
    

    if info_dump.self.depth >= 7:
        # 63.8% return 0 else return 2
        if randf() < 0.001:
            return 0
    else:
        return 7    
    return 9

def transposition_space_function_connect_four(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> dict[int, int]:
    trans_map = {0: 1
                 }
    

    return trans_map
