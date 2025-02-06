from StateNode import StateNode
from utils import *


class State():
    """Wrapper class for state nodes."""
    def __init__(self, branching_factor: int, max_depth: int,
                 node_type_ratio: float=0.5, seed: int=0):
        self._current = StateNode(branching_factor, max_depth, node_type_ratio, seed)
        self._current.parent = None
        self._current.value = 1
        self._current.id = '0'
        self._current.depth = 0
        self._current.player = Player.MAX
        self._current.node_type = NodeType.CHOICE

    def is_terminal(self) -> bool:
        """Return whether the current state is terminal."""
        return self._current.is_terminal()

    def id(self):
        """Return the id of the current state."""
        return self._current.id

    def actions(self):
        """Return values of the current state's children."""
        return self._current.actions()

    def make(self, i: int):
        """Transition to the next state via action i."""
        if self._current.children is None:
            self._current.generate_children()
        self._current = self._current.children[i]
        return self

    def undo(self):
        """Move back to previous state."""
        self._current.reset() # release memory as we climb back up the tree
        self._current = self._current.parent
        return self
    
    def __str__(self):
        return self._current.__str__()
    
    def __repr__(self):
        return self._current.__repr__()