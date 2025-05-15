from sssg import SyntheticGraph
from sssg.custom_types import Player
from collections import deque


def bfs(state: SyntheticGraph):
	"""This function explores the graph in BFS order. The `set_root` method is used 
	to move the internal state to the node being processed so its children 
	can be generated. The original root node's ID is saved and restored 
	at the end to preserve the original state"""
	visited: set[int] = set()
	queue: deque[int] = deque()
	queue.append(state.id())
	visited.add(state.id())

	root_id = state.id() 
	while queue:
		current = queue.popleft()
		state.set_root(current)
		# do something
		for action in state.actions():
			state.make(action)
			if state.id() not in visited:
				visited.add(state.id())
				queue.append(state.id())
			state.undo()
	state.set_root(root_id)


INF = 1000
visited: dict[int, float|int] = {}
def minimax(state: SyntheticGraph, depth: int) -> float|int:
	"""This is a classic minimax search (without Alpha-Beta pruning). It calculates
	the true value of a given state up to depth d. If it doesn't reach a terminal node 
	and were at the maximum depth capacity we return the heuristic."""
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
		