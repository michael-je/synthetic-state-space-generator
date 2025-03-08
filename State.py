from graphviz import Digraph
from typing import Self

from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import *


class State():
    """Wrapper class for state nodes. Should be used as the main API."""
    def __init__(self, max_depth: int, branching_function: Callable[[int, float], int]|None=None, 
                 max_states: int=TMAX_32BIT, node_type_ratio: float=0.5, seed: int=0, 
                 retain_tree: bool=False):
        if branching_function is None:
            branching_function = lambda depth, rand: 2 # binary tree by default
        self.globals = GlobalParameters(
            branching_function = branching_function,
            max_depth = max_depth,
            max_states = max_states, # maximum number of different states,
            seed = seed,
            node_type_ratio = node_type_ratio, # choice / forced,
            retain_tree = retain_tree,
        )
        
        self._current: StateNode = StateNode(0, self.globals)
        self._root = self._current
        self._current.parent = None
        self._current.value = 1
        self._current.depth = 0
        self._current.player = Player.MAX
        self._current.node_type = NodeType.CHOICE
        
        self.hasher = RNGHasher(seed_int=self.globals.seed)

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self._current.is_terminal()

    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self._current.is_root()

    def id(self) -> int:
        """Return the id of the current state."""
        return self._current.id

    def actions(self):
        """Return indices of the current state's children."""
        return self._current.actions()

    def make(self, idx: int) -> Self:
        """Transition to the next state via action idx."""
        self._current.generate_children()
        self._current = self._current.children[idx]
        if not self.globals.retain_tree and not self.is_root():
            self._current.parent.children = [self._current]
        return self
    
    def make_random(self) -> Self:
        """Take a deterministic pseudo-random choice."""
        actions = self.actions()
        i = int(self.hasher.next_uniform() * len(actions))
        self.make(actions[i])
        return self

    def undo(self) -> Self:
        """Move back to previous state."""
        if self._current.parent is None:
            return self
        self._current = self._current.parent
        if not self.globals.retain_tree:
            self._current.reset() # release memory as we climb back up the tree
        return self

    def draw_tree(self) -> None:
        """Draw the current node tree. Best used when retaining the tree."""
        visited: set[tuple[int, int]] = set()
        def draw_tree_recur(graph: Digraph, node: StateNode):
            graph.node(name=str(node.id))
            if node.is_terminal():
                return
            for child in node.children:
                edge = (node.id, child.id)
                if edge not in visited:
                    visited.add(edge)
                    graph.edge(str(node.id), str(child.id))
                draw_tree_recur(graph, child)
        
        graph = Digraph(format="png")
        draw_tree_recur(graph, self._root)
        graph.render(f"trees/tree_seed_{self.globals.seed}" , view=True)  
    
    def __str__(self) -> str:
        return self._current.__str__()
    
    def __repr__(self) -> str:
        return self._current.__repr__()
