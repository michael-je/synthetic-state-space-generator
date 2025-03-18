from graphviz import Digraph
from typing import Self

from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import *


class State():
    """Wrapper class for state nodes. Should be used as the main API."""
    def __init__(self,
                 max_depth: int=2**8-1,
                 root_value: int=1,
                 branching_function: BranchingFunc=default_branching_function, 
                 child_value_function: ChildValueFunc=default_child_value_function, 
                 child_depth_function: ChildDepthFunc=default_child_depth_function,
                 transposition_space_function: TranspositionSpaceFunc=default_transposition_space_function,
                 seed: int=0, 
                 retain_tree: bool=False):
        
        self._RNG = RNGHasher(seed=seed)
        id_depth_bits_size = bit_size(max_depth)
        state_distribution_map = transposition_space_function(
            self._RNG.next_int, self._RNG.next_uniform, max_depth)
        # TODO: verify state space bits size
        
        self.globals = GlobalParameters(
            branching_function = branching_function,
            child_value_function = child_value_function,
            child_depth_function = child_depth_function,
            transposition_space_map=state_distribution_map,
            max_depth = max_depth,
            id_depth_bits_size=id_depth_bits_size,
            seed = seed,
            retain_tree = retain_tree,
        )

        self._root: StateNode = StateNode(
            stateid=0, value=root_value, depth=0, globals=self.globals, parent=None)
        self._current: StateNode = self._root
    
    def __str__(self) -> str:
        return str(self._current)
    
    def __repr__(self) -> str:
        return self._current.__repr__()

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self._current.is_terminal()
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self._current.is_root()

    def id(self) -> int:
        """Return the id of the current state."""
        return self._current.id

    def actions(self) -> list[int]:
        """Return the current state's possible actions."""
        return self._current.actions()
    
    def value(self) -> int:
        return self._current.value

    def make(self, action: int) -> Self:
        """Transition to the next state via action (represented as an index into the states children)."""
        self._current.generate_children()
        self._current = self._current.children[action]
        if not self.globals.retain_tree:
            if self._current.parent is None:
                raise RootHasNoParent() # can't happen, but suppresses type warning
            self._current.parent.kill_siblings()
        return self
    
    def make_random(self) -> Self:
        """Make a random action."""
        actions = self.actions()
        i = int(self._RNG.next_uniform() * len(actions))
        self.make(actions[i])
        return self

    def undo(self) -> Self:
        """Move back to previous state."""
        if self._current.parent is None:
            raise RootHasNoParent()
        self._current = self._current.parent
        if not self.globals.retain_tree:
            self._current.reset() # release memory as we climb back up the tree
        return self

    def draw_tree(self) -> None:
        """Draw the current node tree. Best used when retaining the tree."""
        visited: set[tuple[int, int]] = set()
        def draw_tree_recur(graph: Digraph, node: StateNode):
            graph.node(name=str(node.id), label=str(node))
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
