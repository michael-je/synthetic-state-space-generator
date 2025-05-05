from typing import Self
import math

from RNGHasher import RNGHasher
from custom_types import *
from constants import ID_BIT_SIZE
from utils import bit_size
from custom_exceptions import IdOverflow


class StateNode():
    def __init__(self, stateid: int,
                 globals: GlobalParameters, 
                 parent: "StateNode|None"=None):
        self.id: int = stateid
        self._branching_factor: int|None = None
        self._value: int|None = None
        self.globals = globals
        self.parent = parent
        self._state_params: StateParams|None = None
        
        self.children: list[StateNode] = []
        self._RNG: RNGHasher = RNGHasher(
            distribution=self.globals.vars.distribution, nodeid=self.id, seed=self.globals.vars.seed)
    
    def __str__(self) -> str:
        return "{}-{}".format(*self._decode_id(self.id))

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateNode):
            return False
        return self.id == other.id
    
    # TODO: test
    def _encode_id(self, depth: int, transposition_space_record: int) -> int:
        # TODO: docstring
        if not 0 <= depth <= self.globals.vars.max_depth:
            # TODO: test
            raise IdOverflow(f"depth {depth}.")
        if not 0 <= transposition_space_record <= self.globals.vars.max_transposition_space_size:
            # TODO: test
            raise IdOverflow(f"state_space_record {transposition_space_record}.")
        depth_bits = depth << bit_size(self.globals.vars.max_transposition_space_size) - 1
        return depth_bits | transposition_space_record
    
    # TODO: test
    def _decode_id(self, state_id: int) -> tuple[int, int]:
        # TODO: docstring
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
    
    def _generate_child_id(self) -> int:
        """Generate a child id using values for depth and random bits."""
        self_tspace_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params().globals, self.depth())
        child_depth = self._calculate_child_depth()
        child_tspace_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params().globals, child_depth)
        # apply locality scaling
        tspace_scaling_factor = child_tspace_size / self_tspace_size
        child_tspace_record_center = math.floor(self.tspace_record() * tspace_scaling_factor)
        child_tspace_variance_margin = (child_tspace_size-1) * (1-self.globals.vars.locality) / 2 
        child_tspace_record = self._RNG.next_int(
            low=math.floor(child_tspace_record_center - child_tspace_variance_margin),
            high=math.floor(child_tspace_record_center + child_tspace_variance_margin)
        )
        child_tspace_record %= child_tspace_size
        return self._encode_id(child_depth, child_tspace_record)
    
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
    
    def tspace_record(self) -> int:
        """Return the transposition space record of the state."""
        _, tspace_record = self._decode_id(self.id)
        return tspace_record
    
    def heuristic_value(self) -> int:
        """Return a heuristic value estimate based on the state's true value."""
        return self.globals.funcs.heuristic_value_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params(), self.value())

    def actions(self) -> list[int]:
        """Return indices of children."""
        self.generate_children()
        return list(range(len(self.children)))
    
    def reset(self) -> Self:
        """Reset state to before any randomness-depentant actions were taken."""
        self.children = []
        self._branching_factor = None
        self._value = None
        self._RNG.reset()
        return self
    
    def branching_factor(self) -> int:
        """Get or set branching factor."""
        if self._branching_factor is None:
            self._branching_factor = self.globals.funcs.branching_function(
                self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        return self._branching_factor
    
    def value(self) -> int:
        """Get or set true value."""
        if self._value is None:
            self._value = self.globals.funcs.value_function(
                self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        return self._value

    def generate_children(self) -> Self:
        """Generate child states."""
        if self.is_terminal():
            return self
        if self.children:
            return self
        new_children: list["StateNode"] = []
        for _ in range(self.branching_factor()):
            child_id = self._generate_child_id()
            new_child = StateNode(
                stateid=child_id, globals=self.globals, parent=self)
            new_children.append(new_child)
        self.children = new_children
        return self
