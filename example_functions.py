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

    if info_dump.self.depth <6 :
        return 7
    
    if info_dump.self.depth <7 :
        if rand_num < 7/(7+16415):
            return 6
        return 7
    if info_dump.self.depth <8 :
        if rand_num < 294/(294+728+53837):
            return 6
        elif rand_num < (294+728)/(294+728+53837):
            return 0
        return 7
    if info_dump.self.depth <9 :
        if rand_num < 4326/(4326+1892+178057):
            return 6
        elif rand_num <  (4326+1892)/(4326+1892+178057):
            return 0
        return 7
    else:
        if rand_num < 45748/(45748+29054+1197553):
            return 6
        elif rand_num <  (45748+29054)/(45748+29054+1197553):
            return 0
        return 7
    


def transposition_space_function_connect_four(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    trans_map = {0: 1,
                 1: 7,
                 2: 49,
                 3: 238,
                 4: 1120,
                 5: 4263,
                 6: 16415,
                 7: 728+294+53837,
                 8: 1892+4326+178057,
                 9: 119412+31984+506790   
                 }
    
    return trans_map
