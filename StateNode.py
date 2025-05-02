from typing import Self

from RNGHasher import RNGHasher
from custom_types import *
from constants import ID_BIT_SIZE
from utils import bit_size
from custom_exceptions import IdOverflow


class StateNode():
    def __init__(self, stateid: int,
                 value: int,
                 globals: GlobalParameters, 
                 parent: "StateNode|None"=None):
        self.id: int = stateid
        self._branching_factor: int|None = None
        self.value = value
        self.globals = globals
        self.parent = parent
        self._state_params: StateParams|None = None
        
        self.children: list[StateNode] = []
        self._RNG: RNGHasher = RNGHasher(
            distribution=self.globals.vars.distribution, nodeid=self.id, seed=self.globals.vars.seed)
    
    def __str__(self) -> str:
        depth, transposition_space_record = self._decode_id(self.id)
        return f"{depth}-{transposition_space_record}"

    def __repr__(self) -> str:
        return str(self)
    
    # TODO: test
    def _encode_id(self, depth: int, transposition_space_record: int) -> int:
        if not 0 <= depth <= self.globals.vars.max_depth:
            # TODO: test
            raise IdOverflow(f"depth {depth}.")
        if not 0 <= transposition_space_record <= self.globals.vars.max_transposition_space_Size:
            # TODO: test
            raise IdOverflow(f"state_space_record {transposition_space_record}.")
        depth_bits = depth << (ID_BIT_SIZE - bit_size(self.globals.vars.max_depth))
        return depth_bits | transposition_space_record
    
    # TODO: test
    def _decode_id(self, state_id: int) -> tuple[int, int]:
        state_space_record_bit_size = ID_BIT_SIZE - bit_size(self.globals.vars.max_depth)
        transposition_space_record_bit_mask = (1 << state_space_record_bit_size) - 1
        depth = state_id >> state_space_record_bit_size
        transposition_space_record = state_id & transposition_space_record_bit_mask
        return depth, transposition_space_record
    
    def _construct_state_params(self) -> StateParams:
        """Construct StateParams, this contains necessary information used by behavioral functions."""
        depth, transposition_space_record = self._decode_id(self.id)
        state_params_self = StateParamsSelf(
            id = self.id,
            transposition_space_record = transposition_space_record,
            depth = depth,
        )
        state_params = StateParams(
            globals = self.globals.vars,
            self = state_params_self,
        )
        return state_params
    
    def _calculate_child_depth(self) -> int:
        """Calculate depth of a child node and ensure it stays within the allowed range."""
        child_depth = self.globals.funcs.child_depth_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        if child_depth < 0:
            raise IdOverflow(f"Depth can not be negative.")
        if child_depth > self.globals.vars.max_depth:
            raise IdOverflow(f"Depth can not exceed max_depth.")
        return child_depth
    
    def _generate_child_id(self, child_depth: int) -> int:
        """Generate a child id using values for depth and random bits."""
        transposition_space_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params().globals, child_depth)
        transposition_space_record = self._RNG.next_int() % transposition_space_size
        return self._encode_id(child_depth, transposition_space_record)
    
    def get_state_params(self) -> StateParams:
        """Construct StateParams, if necessary, and return them."""
        if self._state_params is None:
            self._state_params = self._construct_state_params()
        return self._state_params
    
    def kill_siblings(self) -> None:
        """Deallocate sibling memory."""
        if self.parent is None:
            return # in case we are root
        self.parent.children = [self]

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth() >= self.globals.vars.max_depth - 1 or self.branching_factor() < 1
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.parent is None
    
    def depth(self) -> int:
        """Return the depth of the state."""
        depth, _ = self._decode_id(self.id)
        return depth
    
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
                stateid=child_id, value=child_value, globals=self.globals, parent=self)
            new_children.append(new_child)
        self.children = new_children
        return self
