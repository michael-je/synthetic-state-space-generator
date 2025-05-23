from typing import Self
import math

from .RNGHasher import RNGHasher
from .custom_types import *
from .constants import *
from .utils import *
from .custom_exceptions import IdOverflow


class StateNode():
    def __init__(self, 
                 stateid: int,
                 globals: GlobalParameters, 
                 true_value: int,
                 player: Player,
                 depth: int,
                 tspace_record: int,
                 parent: "StateNode|None"=None):
        self.id: int = stateid
        self.globals = globals
        self.true_value = true_value
        self.player = player
        self.depth = depth
        self.tspace_record = tspace_record
        self.parent = parent
        self._random_values_generated: bool = False
        self._branching_factor: int|None = None
        self._heuristic_value: float|None = None
        self._state_params: StateParams|None = None
        
        self.children: list[StateNode] = []
        self._RNG: RNGHasher = RNGHasher(
            distribution=self.globals.vars.distribution, nodeid=self.id, seed=self.globals.vars.seed)
    
    def __str__(self) -> str:
        return f"true_value: {self.true_value}, player: {self.player.name}, depth: {self.depth}, tspace_record: {self.tspace_record}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StateNode):
            return False
        return self.id == other.id
    
    def _encode_id(self, true_value: int, player: Player, depth: int, tspace_record: int) -> int:
        """"Encodes provided state attributes to a unique state id."""
        if not -1 <= true_value <= 1:
            raise ValueError(f"Invalid value {true_value}. Value should be in [-1, 1].")
        if not 0 <= depth <= self.globals.vars.max_depth:
            raise IdOverflow(f"depth {depth}.")
        if not 0 <= tspace_record <= self.globals.vars.max_transposition_space_size:
            raise IdOverflow(f"state_space_record {tspace_record}.")
        true_value_bit_shift = ID_BIT_LENGTH - ID_TRUE_VALUE_BIT_LENGTH
        player_bit_shift = true_value_bit_shift - ID_PLAYER_BIT_LENGTH
        depth_bit_shift = player_bit_shift - self.globals.vars.max_depth.bit_length()
        player_bits = player.value << player_bit_shift
        true_value_bits = encode_true_value_to_bits(true_value) << true_value_bit_shift
        depth_bits = depth << depth_bit_shift
        return true_value_bits | player_bits | depth_bits | tspace_record
    
    def _construct_state_params(self) -> StateParams:
        """Construct StateParams, this contains necessary information used by 
        behavioral functions."""
        transposition_space_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.globals.vars, self.depth
        )
        state_params_self = StateParamsSelf(
            id = self.id,
            true_value = self.true_value,
            player = self.player,
            depth = self.depth,
            transposition_space_record = self.tspace_record,
            transposition_space_size = transposition_space_size,
        )
        state_params = StateParams(
            globals = self.globals.vars,
            self = state_params_self,
        )
        return state_params
    
    def _calculate_child_true_value(self, child_true_value_information: ChildTrueValueInformation) -> int:
        """Wrapper function to calculate a true value for a child state, by calling the
        child_true_value_function."""
        true_value = self.globals.funcs.child_true_value_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params(), 
            self.branching_factor(), child_true_value_information)
        return true_value
    
    def _calculate_child_player(self) -> Player:
        """Calculate the player attribute for child states."""
        return Player.MAX if self.player == Player.MIN else Player.MIN
    
    def _calculate_child_depth(self) -> int:
        """Calculate depth of a child node and ensure it stays within the allowed range."""
        child_depth = self.globals.funcs.child_depth_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        if child_depth < 0:
            raise IdOverflow("Depth can not be negative.")
        if child_depth > self.globals.vars.max_depth:
            raise IdOverflow("Depth can not exceed max_depth.")
        return child_depth
    
    def _calculate_child_tspace_record(self, child_depth: int) -> int:
        """Calculate a transposition space record for a state at a given depth. The main bulk
        of this function is correctly scaling the tspace record from one depth to the next,
        based on the relative sizes of the transposition spaces and the locality parameter."""
        self_tspace_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params().globals, self.depth)
        child_tspace_size = self.globals.funcs.transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params().globals, child_depth)
        # the below code applies the locality scaling
        tspace_scaling_factor = child_tspace_size / self_tspace_size
        child_tspace_record_center = math.floor(self.tspace_record * tspace_scaling_factor)
        child_tspace_variance_margin = (child_tspace_size - 1) * (1-self.globals.vars.locality_grouping) / 2 
        lower_margin = math.floor(child_tspace_record_center - child_tspace_variance_margin)
        upper_margin = math.floor(child_tspace_record_center + child_tspace_variance_margin)
        child_tspace_record = self._RNG.next_int(low=lower_margin, high=upper_margin)
        child_tspace_record %= (child_tspace_size + 1) # +1 because the maximum is inclusive
        return child_tspace_record
    
    def _generate_child(self, child_true_value_information: ChildTrueValueInformation) -> "StateNode":
        """Generate a child id using values for depth and random bits."""
        child_true_value = self._calculate_child_true_value(child_true_value_information)
        child_player = self._calculate_child_player()
        child_depth = self._calculate_child_depth()
        child_tspace_record = self._calculate_child_tspace_record(child_depth)
        child_id = self._encode_id(child_true_value, child_player, child_depth, child_tspace_record)
        new_child = StateNode(
            stateid=child_id, globals=self.globals, true_value=child_true_value, 
            player=child_player, depth=child_depth, tspace_record=child_tspace_record,
            parent=self)
        return new_child
    
    def get_state_params(self) -> StateParams:
        """Construct StateParams, if necessary, and return them."""
        if self._state_params is None:
            self._state_params = self._construct_state_params()
        return self._state_params

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth >= self.globals.vars.max_depth or self.branching_factor() < 1
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.parent is None
    
    def branching_factor(self) -> int:
        """Get or set branching factor."""
        self._execute_all_randomness_dependant_functions()
        assert(self._branching_factor is not None)
        return self._branching_factor
    
    def heuristic_value(self) -> float:
        """Return a heuristic value estimate based on the state's true value."""
        self._execute_all_randomness_dependant_functions()
        assert(self._heuristic_value is not None)
        return self._heuristic_value

    def actions(self) -> list[int]:
        """Return indices of children."""
        self._execute_all_randomness_dependant_functions()
        return list(range(len(self.children)))
    
    def reset(self) -> Self:
        """Reset state to before any randomness-depentant actions were taken."""
        self.children = []
        self._branching_factor = None
        self._heuristic_value = None
        self._random_values_generated = False
        self._RNG.reset()
        return self

    def _generate_children(self) -> Self:
        """Generate child states."""
        if self.is_terminal():
            return self
        if self.children:
            return self
        new_children: list["StateNode"] = []
        sibling_true_value_information = ChildTrueValueInformation()
        if self._RNG.next_float() < self.globals.vars.symmetry_frequency:
            unique_children_count = max(1, math.floor(self.branching_factor() * self.globals.vars.symmetry_factor))
        else:
            unique_children_count = self.branching_factor()
        for _ in range(unique_children_count):
            new_child = self._generate_child(sibling_true_value_information)
            sibling_true_value_information.total_children_generated += 1
            assign_child_true_value_information(
                sibling_true_value_information, self.player, new_child.true_value)
            new_children.append(new_child)
        for i in range(self.branching_factor() - unique_children_count):
            symmetrical_child = new_children[i % unique_children_count]
            new_children.append(symmetrical_child)
        self.children = new_children
        return self
    
    def _execute_all_randomness_dependant_functions(self) -> Self:
        """To ensure determinism, all calls to the RNG within the state must be taken in the 
        same order each time. When any random calculation is needed, this function is called
        first to ensure that all random calculations are performed in a specific sequence."""
        if self._random_values_generated:
            return self
        self._random_values_generated = True
        self._branching_factor = self.globals.funcs.branching_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        self._heuristic_value = self.globals.funcs.heuristic_value_function(
            self._RNG.next_int, self._RNG.next_float, self.get_state_params())
        self._generate_children()
        return self
