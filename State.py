from graphviz import Digraph
from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import *


class State():
    """Wrapper class for state nodes. Should be used as the main API."""
    def __init__(self, branching_function: int, max_depth: int,
                 node_type_ratio: float=0.5, seed: int=0, retain_tree: bool=False):
        self.branching_function = branching_function
        self.max_depth = max_depth
        self.seed = seed
        self.node_type_ratio = node_type_ratio # choice / forced
        self.retain_tree = retain_tree
        
        self._current = StateNode(branching_function, branching_function(0), max_depth, node_type_ratio, seed)

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
        """Take a deterministic pseudo-random choice."""
        self.make(int(self.hasher.next_random() * self._current.branching_factor))
        return self

    def undo(self):
        """Move back to previous state."""
        self._current = self._current.parent
        if not self.retain_tree:
            self._current.reset() # release memory as we climb back up the tree
        return self

    def draw_tree(self):
        """Draw the current node tree. Best used when retaining the tree."""
        def draw_tree_recur(graph: Digraph, node: StateNode):
            graph.node(name=node.id, label=node.id.split('.')[-1])
            if node.is_terminal():
                return
            for child in node.children:
                graph.edge(node.id, child.id)
                draw_tree_recur(graph, child)
        
        graph = Digraph(format="png")
        draw_tree_recur(graph, self._root)
        graph.render(f"trees/tree_seed_{self.seed}" , view=True)  
    
    def __str__(self):
        return self._current.__str__()
    
    def __repr__(self):
        return self._current.__repr__()
