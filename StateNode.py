from typing import Self

from utils import *
from RNGHasher import RNGHasher


class StateNode():
    def __init__(self, nodeid: int, globals: GlobalParameters, parent: "StateNode|None"=None, 
                 move_number: list|None=None, player: Player|None=None):
        self.id = nodeid
        self.globals = globals
        self.parent = parent
        self.move_number = move_number
        self.player = player
        
        if move_number is None:
            self.move_number = []
            self.move_number.append(max(self.parent.move_number) + 1) if self.parent else [0]
            self.move_number.append(uniformaly_id_to_move_number(self.id, globals.max_states, globals.max_depth))
            #self.move_number = self.parent.move_number + 1 if self.parent else 0
        if player is None:
            self.player = Player(-self.parent.player.value) if self.parent else Player.MAX
        
        self._children: list["StateNode"] = []
        self._RNG = RNGHasher(self.id, self.globals.seed)
        self._branching_factor = self.globals.branching_function(min(self.move_number), self._RNG.next_uniform())
        parent_value = 1 if self.parent is None else self.parent.value() # set root value to 1 by default
        self._value = self.globals.value_function(parent_value, self._RNG.next_uniform())
    
    def __repr__(self) -> str:
        return f"id:{self.id}, depth:{self.move_number}, children:{len(self._children)}"
    
    def _generate_child_id(self) -> int:
        return self.globals.transition_function(min(self.move_number), self._RNG.next_int(), self.globals.max_states, self.globals.max_depth)

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return max(self.move_number) == self.globals.max_depth or self.branching_factor() < 1
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.parent is None

    def actions(self) -> list[int]:
        """Return indices of children."""
        self.generate_children()
        return list(range(len(self._children)))
    
    def reset(self) -> Self:
        """Reset state to before an action on it was taken."""
        self._children = []
        self._RNG.reset()
        return self
    
    def branching_factor(self) -> int:
        return self._branching_factor
    
    def value(self) -> int:
        return self._value

    def generate_children(self) -> Self:
        """Generate child states."""
        if self.is_terminal():
            return self
        if self._children:
            return self
        
        new_children: list["StateNode"] = []
        for _ in range(self.branching_factor()):
            child_id = self._generate_child_id()
            new_child = StateNode(nodeid=child_id, globals=self.globals, parent=self)
            new_children.append(new_child)
        self._children = new_children
        return self
