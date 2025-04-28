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
        sumBranchingFactorPerDepth[depth] += len(state.actions())

        for action in state.actions():
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

    ##Terminal state distribution
    print("Terminal State Count Per depth:")
    for depth in terminalCountPerDepth:
        print(f"depth {depth} : {terminalCountPerDepth[depth]}   |   Ratio: {terminalCountPerDepth[depth]/stateCountPerDepth[depth]}")
    print()
    print()





    ##Unique states Count per depth
    print("Unique states Count per depth:")
    for depth in stateCountPerDepth:
        print(f"depth {depth} : {stateCountPerDepth[depth]}")
    print()
    print()



    input()



def tictactoeExample():
    #number of reachable states are 5478


    input()
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
