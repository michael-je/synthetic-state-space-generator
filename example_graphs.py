from example_functions import *
from default_functions import *
from State import State
from math import comb

def dfs(state: State, example: int):
    visited = set()
    count = {0:0}
    valueCountPerDepth = {i:{-1:0, 0:0, 1:0} for i in range(10)}
    terminalCountPerDepth = {i:0 for i in range(10)}
    stateCountPerDepth = {i:0 for i in range(10)}
    sumBranchingFactorPerDepth = {i:0 for i in range(10)}

    actualValueCountPerDepth = {
        0: {-1:0, 0:1, 1:0},
        1: {-1:0, 0:9, 1:0},
        2: {-1:0, 0:24, 1:48},
        3: {-1:50, 0:138, 1:64},
        4: {-1:36, 0:136, 1:584},
        5: {-1:540, 0:264, 1:456},
        6: {-1:264, 0:200, 1:1056},
        7: {-1:416, 0:200, 1:524},
        8: {-1:168, 0:80, 1:142},
        9: {-1:0, 0:16, 1:62}
    }
    actualValueDistribution = {
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
    actualStateCountPerDepth = {0:1, 1:9, 2:72, 3:252, 4:756, 5:1260, 6:1520, 7:1140, 8:390, 9:78}


    

    def dfs_recur(state: State, depth: int):
        sid = str(state.id())
        if sid in visited:
            return
        visited.add(sid)

        count[0] += 1

        stateTrueVal = state.value()
        valueCountPerDepth[depth][stateTrueVal] += 1

        if state.is_terminal():
            terminalCountPerDepth[depth] += 1
        
        stateCountPerDepth[depth] += 1

        actions = state.actions()
        sumBranchingFactorPerDepth[depth] += len(actions)
        for action in actions:
            state.make(action)
            child_id = str(state.id())
            dfs_recur(state, depth+1)
            state.undo()
    
    dfs_recur(state, 0)
    print("#####################################")
    print(f"Example {example}")
    print()
    print()

    ##True value Count at each depth:
    print("True value Distribution:")
    print(f"True values : -1  0  1")
    print("____________________________________")
    for depth in valueCountPerDepth:
        print(f"   depth  {depth} :  ",end="")
        for val in valueCountPerDepth[depth]:
            print(f"{valueCountPerDepth[depth][val]}  ", end="")
        print()
    print()
    print()

    ##True value Count at each depth:
    print("True value Distribution ratio:")
    print(f"True values :  -1     0      1")
    print("________________________________")
    for depth in valueCountPerDepth:
        print(f"   depth  {depth} :  ",end="")
        tot = sum([valueCountPerDepth[depth][val] for val in valueCountPerDepth[depth]])
        for val in valueCountPerDepth[depth]:
            print(f"{valueCountPerDepth[depth][val]/tot:.2f}  ", end="")
        print()
    print()
    print()


    ##Terminal state distribution
    print("Terminal State Count Per depth:")
    for depth in terminalCountPerDepth:
        print(f"depth {depth} : {terminalCountPerDepth[depth]:<3}   |    Ratio: {terminalCountPerDepth[depth]/stateCountPerDepth[depth]:.2f}")
    print()
    print()





    ##Unique states Count per depth
    print("Unique states Count per depth:")
    for depth in stateCountPerDepth:
        print(f"depth {depth} : {stateCountPerDepth[depth]}")
    print()
    print()


    ##Average branching factor per depth
    print("Average branching factor per depth:")
    for depth in sumBranchingFactorPerDepth:
        print(f"depth {depth} : {round(sumBranchingFactorPerDepth[depth]/stateCountPerDepth[depth], 4)}")
    print()
    print()


    print("#####################################################")
    print("#####################################################")
    print()
    print("Actual values:")
    print()
   
   
    print("True value Distribution ratio:")
    print(f"True values :  -1     0      1")
    print("________________________________")
    for depth in actualValueCountPerDepth:
        print(f"   depth  {depth} :  ",end="")
        tot = sum([actualValueCountPerDepth[depth][val] for val in actualValueCountPerDepth[depth]])
        for val in actualValueCountPerDepth[depth]:
            print(f"{actualValueCountPerDepth[depth][val]/tot:.2f}  ", end="")
        print()
    print()
    print()

    print("Unique states Count per depth:")
    for depth in actualStateCountPerDepth:
        print(f"depth {depth} : {actualStateCountPerDepth[depth]}")
    print()
    print()



    input()



def tictactoeExample():
    #number of reachable states are 5478



    for i in range(100):
        state = State(
            max_depth=10,
            root_value=0,
            branching_function=tictactoe_branching_function,
            child_value_function=tictactoe_child_value_function,
            child_depth_function=default_child_depth_function,
            transposition_space_function=tictactoe_transposition_space_function,
            seed=i,
            retain_tree=True
        )
        
        dfs(state, example=i)

tictactoeExample()
