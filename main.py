from  State  import  State

INF = 1000
def minimax(state: State, depth: int, isMaximizingPlayer: bool):
    if state.is_terminal():
        return state.value()
    if depth == 0:
        print(state.value())
        return state.value()
        return state.heuristic_value()

    if isMaximizingPlayer:
        maxEval = -INF

        for action in state.actions():
            state.make(action)
            sEval = minimax(state, depth-1, not isMaximizingPlayer)
            state.undo()
            maxEval = max(maxEval, sEval)
        return maxEval
    else:
        minEval = INF
        for action in state.actions():
            state.make(action)
            sEval = minimax(state, depth-1, not isMaximizingPlayer)
            state.undo()
            minEval = min(minEval, sEval)			
        return minEval

def dfs(state: State):
    
    def dfs_recur(state: State, depth: int):
        if depth == 1:
            print(state.id())
            return 
        for action in state.actions():
            state.make(action)
            dfs_recur(state, depth+1)
            state.undo()
    
    dfs_recur(state, 0)


def  main():
    state = State()
    print("not in dfs: ", state.id())
    print("DFS:")
    print("not in dfs: ", state.id())
    dfs(state)
    print("DFS:")
    print("not in dfs: ", state.id())
    dfs(state)
    print("DFS:")
    dfs(state)
    print("DFS:")
    dfs(state)

    """
    print("Minimax")
    rootVal = minimax(state, 3, isMaximizingPlayer=True)
    print(f"Value of root is {rootVal}")
    """



if __name__ == "__main__":
    main()
