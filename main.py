from State import State
from custom_types import Player

INF = 1000
visited: dict[int, int] = {}
def minimax(state: State, depth: int) -> int:
	if state.id() in visited.keys():
		return state.true_value()
	if state.is_terminal():
		return state.true_value()
	if depth == 0:
		return state.heuristic_value()
	
	if state.player() == Player.MAX:
		max_eval = -INF
		for action in state.actions():
			state.make(action)
			s_eval = minimax(state, depth-1)
			state.undo()
			max_eval = max(max_eval, s_eval)
		visited[state.id()] = max_eval
		return max_eval
	else:
		min_eval = INF
		for action in state.actions():
			state.make(action)
			s_eval = minimax(state, depth-1)
			state.undo()
			min_eval = min(min_eval, s_eval)			
		visited[state.id()] = min_eval
		return min_eval

def main():
	state = State(max_depth=9)
	val = minimax(state, 9)
	print(f"Minimax Value: {val}")
	print(f"True value: {state.true_value()}")

main()