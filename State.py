from graphviz import Digraph
from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import *


class State():
    """Wrapper class for state nodes."""
    def __init__(self, branching_factor: int, max_depth: int,
                 node_type_ratio: float=0.5, seed: int=0, retain_tree: bool=False):
        self.branching_factor: int = branching_factor
        self.max_depth: int = max_depth
        self.seed = seed
        self.node_type_ratio = node_type_ratio # choice / forced
        self.retain_tree = retain_tree
        
        self._current = StateNode(branching_factor, max_depth, node_type_ratio, seed)
        self._root = self._current
        self._current.parent = None
        self._current.value = 1
        self._current.id = '0'
        self._current.depth = 0
        self._current.player = Player.MAX
        self._current.node_type = NodeType.CHOICE
        
        self.hasher = RNGHasher(seed_int=self.seed)

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self._current.is_terminal()
    

    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self._current.is_root()

    def id(self):
        """Return the id of the current state."""
        return self._current.id

    def actions(self):
        """Return values of the current state's children."""
        return self._current.actions()

    def make(self, i: int):
        """Transition to the next state via action i."""
        self._current.generate_children()
        self._current = self._current.children[i]
        if not self.retain_tree:
            self._current.parent.children = [self._current]
        return self
    
    def make_random(self):
        """Take a pseudo-random deterministic choice."""
        i = int(self.hasher.next_random() * self.branching_factor)
        self.make(i)

    def undo(self):
        """Move back to previous state."""
        self._current = self._current.parent
        if not self.retain_tree:
            self._current.reset() # release memory as we climb back up the tree
        return self
    
    def _draw_tree_recur(self, graph: Digraph, node: StateNode):
        graph.node(name=node.id, label=node.id.split('.')[-1])
        if node.is_terminal():
            return
        for child in node.children:
            graph.edge(node.id, child.id)
            self._draw_tree_recur(graph, child)

    def draw_tree(self):
        graph = Digraph(format="png")
        self._draw_tree_recur(graph, self._root)
        graph.render('tree_visualization', view=True)  
    
    def __str__(self):
        return self._current.__str__()
    
    def __repr__(self):
        return self._current.__repr__()
