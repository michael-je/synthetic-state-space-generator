from typing import Self

from RNGHasher import RNGHasher
from custom_types import *
from constants import ID_BITS_SIZE
from exceptions import IdOverflow


class StateNode():
    def __init__(self, stateid: int,
                 value: int,
                 depth: int,
                 globals: GlobalParameters, 
                 parent: "StateNode|None"=None):
        self.id: int = stateid
        self._branching_factor: int|None = None
        self.value = value
        self.depth = depth
        self.globals = globals
        self.parent = parent
        self._state_params: StateParams|None = None
        
        self.children: list[StateNode] = []
        self._RNG: RNGHasher = RNGHasher(
            distribution=self.globals.vars.distribution, nodeid=self.id, seed=self.globals.vars.seed)
    
    def __str__(self) -> str:
        random_id_bits_mask = (1 << (ID_BITS_SIZE - self.globals.vars.id_depth_bits_size)) - 1
        return f"{self.depth}-{self.id & random_id_bits_mask}"

    def __repr__(self) -> str:
        return str(self)
    
    def _construct_state_params(self) -> StateParams:
        """Construct StateParams, this contains necessary information used by behavioral functions."""
        if self.parent is None:
            state_params_parent = None
            state_params_siblings = None
        else:
            state_params_parent = StateParamsParent(
                id = self.parent.id,
                value = self.parent.value,
                depth = self.parent.depth,
                branching_factor = self.parent.branching_factor()
            )
            state_params_siblings = StateParamsSiblings(
                id = [child.id for child in self.parent.children],
                value = [child.value for child in self.parent.children],
                depth = [child.depth for child in self.parent.children],
                branching_factor = lambda : [child.branching_factor() for child in self.parent.children] if self.parent else []
            )
        state_params_self = StateParamsSelf(
            id = self.id,
            value = self.value,
            depth = self.depth,
            branching_factor = self._branching_factor # TODO, this is to avoid recursion, but are we ever actually not returning None here?
        )
        state_params = StateParams(
            globals = self.globals.vars,
            parent = state_params_parent,
            self = state_params_self,
            siblings = state_params_siblings
        )
        return state_params
    
    def get_state_params(self) -> StateParams:
        """Construct StateParams, if necessary, and return them."""
        if self._state_params is None:
            self._state_params = self._construct_state_params()
        return self._state_params
    
    def _calculate_child_depth(self) -> int:
        """Calculate depth of a child node and ensure it stays within the allowed range."""
        child_depth = self.globals.funcs.child_depth_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        if child_depth >= (1 << self.globals.vars.id_depth_bits_size):
            raise IdOverflow(f"Depth {self.depth} too large for {self.globals.vars.id_depth_bits_size} bits")
        if child_depth < 0:
            raise IdOverflow(f"Depth can not be negative.")
        if child_depth > self.globals.vars.max_depth:
            raise IdOverflow(f"Depth can not exceed max_depth.")
        return child_depth
    
    def _generate_child_id(self, child_depth: int) -> int:
        """Generate a child id using values for depth and random bits."""
        depth_bits = child_depth << (ID_BITS_SIZE - self.globals.vars.id_depth_bits_size)
        random_bits = self._RNG.next_int() % self.globals.funcs.transposition_space_map[child_depth]
        return depth_bits | random_bits
    
    def kill_siblings(self) -> None:
        """Deallocate sibling memory."""
        if self.parent is None:
            return # in case we are root
        self.parent.children = [self]

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth >= self.globals.vars.max_depth - 1 or self.branching_factor() < 1
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.parent is None
    
    def heuristic_value(self) -> int:
        """Return a heuristic value estimate based on the state's true value."""
        return self.globals.funcs.heuristic_value_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())

    def actions(self) -> list[int]:
        """Return indices of children."""
        self.generate_children()
        return list(range(len(self.children)))
    
    def reset(self) -> Self:
        """Reset state to before an action on it was taken."""
        self.children = []
        self._RNG.reset()
        return self
    
    def branching_factor(self) -> int:
        """Get or set branching factor."""
        if self._branching_factor is None:
            self._branching_factor = self.globals.funcs.branching_function(
                self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        return self._branching_factor

    def generate_children(self) -> Self:
        """Generate child states."""
        if self.is_terminal():
            return self
        if self.children:
            return self
        
        new_children: list["StateNode"] = []
        for _ in range(self.branching_factor()):
            child_depth = self._calculate_child_depth()
            child_id = self._generate_child_id(child_depth)
            child_value = self.globals.funcs.child_value_function(
                self._RNG.next_int, self._RNG.next_float, self.get_state_params())
            new_child = StateNode(
                stateid=child_id, value=child_value, depth=child_depth, globals=self.globals, parent=self)
            new_children.append(new_child)
        self.children = new_children
        return self
