import tests
from State import State

INF = 1000

def minimax(state: State, depth: int, isMaximizingPlayer: bool):
    if state.is_terminal():
        return state.value()
    if depth == 0:
        return state.heuristic_value()

    if isMaximizingPlayer:
        maxEval = -INF
        for action in state.actions():
            state.make(action)
            eval = minimax(state, depth-1, not isMaximizingPlayer)
            state.undo()
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = INF
        for action in state.actions():
            state.make(action)
            eval = minimax(state, depth-1, not isMaximizingPlayer)
            state.undo()
            minEval = min(minEval, eval)

        return minEval

def main():
    for i in range(100):
        state = State(max_depth=10, seed=i)

        val1 = minimax(state, 5, isMaximizingPlayer=True)
        val2 = minimax(state, 5, isMaximizingPlayer=False)
        print(val1, val2)



main()
