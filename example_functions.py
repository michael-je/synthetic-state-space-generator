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

def tictactoe_transposition_space_function(randint: RandomIntFunc, randf: RandomFloatFunc, max_depth: int) -> dict[int, int]:
    """Example tictactoe transposition space function"""
    tsf = {0:1, 1:9, 2:72, 3:252, 4:756, 5:1260, 6:1520, 7:1140, 8:390, 9:78}
    #tsf = {0:1, 1:9+3, 2:72+35, 3:252+100, 4:756+250, 5:1260+160, 6:1520+120, 7:1140+30, 8:390+50, 9:78+25}
    return tsf

def tictactoe_branching_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """simulates branching factor of tictactoe (function of depth)"""
    
    currDepth = info_dump.self.depth
    terminalDensityDistribution = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.10526315789473684,
        6: 0.10787172011661808,
        7: 0.6379310344827587,
        8: 0.7567567567567568,
        9: 1.0
    }
    if terminalDensityDistribution[currDepth] > randf():
        return 0
    
    return 9 - info_dump.self.depth

def tictactoe_child_value_function(randint: RandomIntFunc, randf: RandomFloatFunc, info_dump: InfoDump) -> int:
    """Randomly generate a value of either -1, 0, 1 according to the true value distro of tictactoe"""
    valueCountPerDepth = {
        0: [0, 1, 0],
        1: [0, 9, 0],
        2: [0, 24, 48],
        3: [50, 138, 64],
        4: [36, 136, 584],
        5: [540, 264, 456],
        6: [264, 200, 1056],
        7: [416, 200, 524],
        8: [168, 80, 142],
        9: [0, 16, 62]
    }
    valueDistribution = {
        0: [0.0, 1.0, 0.0],
        1: [0.0, 1.0, 0.0],
        2: [0.0, 0.3333333333333333, 0.6666666666666666],
        3: [0.1984126984126984, 0.5476190476190477, 0.25396825396825395],
        4: [0.047619047619047616, 0.17989417989417988, 0.7724867724867724],
        5: [0.42857142857142855, 0.20952380952380953, 0.3619047619047619],
        6: [0.1736842105263158, 0.13157894736842105, 0.6947368421052632],
        7: [0.3649122807017544, 0.17543859649122806, 0.45964912280701753],
        8: [0.4307692307692308, 0.20512820512820512, 0.3641025641025641],
        9: [0.0, 0.20512820512820512, 0.7948717948717948]
    }

    pNeg, pZero, pPos = valueDistribution[info_dump.self.depth+1]
    r = randf()
    if r <= pNeg:
        return -1
    elif pNeg < r < pNeg + pZero:
        return 0
    else:
        return 1
