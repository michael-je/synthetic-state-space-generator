from graphviz import Digraph
from typing import Self

from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import bit_size
from constants import ID_BIT_SIZE
from custom_types import *
from custom_types import RandomnessDistribution as Dist
from custom_exceptions import *
from default_functions import *


class State():
    """Wrapper class for state nodes. Should be used as the main API."""
    def __init__(self,
                 seed: int=0, 
                 max_depth: int=2**8-1,
                 distribution: RandomnessDistribution=Dist.UNIFORM,
                 retain_graph: bool=False,
                 
                 branching_factor_base: int=2,
                 branching_factor_variance: int=0,
                 terminal_minimum_depth: int=0,
                 child_depth_minumum: int=1,
                 child_depth_maximum: int=1,
                 locality_grouping: float=0,
                 true_value_forced_ratio: float=0.1,
                 true_value_similarity_chance: float=0.5,
                 true_value_tie_chance: float=0.2,
                 symmetry_factor: float=1.0,
                 symmetry_frequency: float=0.0,
                 heuristic_accuracy_base: float=0.7,
                 heuristic_depth_scaling: float=0.5,
                 heuristic_locality_scaling: float=0.5,

                 branching_function: BranchingFunction=default_branching_function, 
                 child_value_function: ChildTrueValueFunction=default_child_true_value_function, 
                 child_depth_function: ChildDepthFunction=default_child_depth_function,
                 transposition_space_function: TranspositionSpaceFunction=default_transposition_space_function,
                 heuristic_value_function: HeuristicValueFunction=default_heuristic_value_function):
        
        if not max_depth > 0:
            raise ValueError("max_depth must be > 0.")
        if bit_size(max_depth) >= ID_BIT_SIZE - ID_TRUE_VALUE_BIT_SIZE - ID_PLAYER_BIT_SIZE:
            raise ValueError("max_depth too large.")
        if not child_depth_maximum >= child_depth_minumum:
            raise ValueError("child_depth_maximum must be >= child_depth_minimum.")
        if not terminal_minimum_depth >= 0:
            raise ValueError("terminal_minimum_depth must be >= 0.")
        if not branching_factor_base >= 0:
            raise ValueError("branching_factor_base must be >= 0.")
        if not branching_factor_variance >= 0:
            raise ValueError("branching_factor_variance must be >= 0.")
        if not 0 <= locality_grouping <= 1:
            raise ValueError("locality must be in [0, 1].")
        if not 0 <= true_value_forced_ratio <= 1:
            raise ValueError("true_value_forced_ratio must be in [0, 1].")
        if not 0 <= true_value_similarity_chance <= 1:
            raise ValueError("true_value_similarity_chance must be in [0, 1].")
        if not 0 <= true_value_tie_chance <= 1:
            raise ValueError("true_value_tie_chance must be in [0, 1].")
        if not 0 < symmetry_factor <= 1:
            raise ValueError("symmetry_factor must be in (0, 1].")
        if not 0 <= symmetry_frequency <= 1:
            raise ValueError("symmetry_frequency must be in [0, 1].")
        if not 0 <= heuristic_depth_scaling <= 1:
            raise ValueError("heuristic_depth_scaling must be in [0, 1].")
        if not 0 <= heuristic_locality_scaling <= 1:
            raise ValueError("heuristic_locality_scaling must be in [0, 1].")
        
        self._RNG = RNGHasher(distribution=distribution, seed=seed)
        max_transposition_space = 2**(ID_BIT_SIZE - ID_TRUE_VALUE_BIT_SIZE - ID_PLAYER_BIT_SIZE - bit_size(max_depth)) - 1
        
        self.transposition_space_map: dict[int, int] = dict()
        def transposition_space_function_wrapper(
                randint: RandomIntFunction, randf: RandomFloatFunction, globals: GlobalVariables, depth: int) -> int:
            t_space = self.transposition_space_map.get(depth)
            if t_space is None:
                t_space = transposition_space_function(randint, randf, globals, depth)
                self.transposition_space_map[depth] = t_space
            if t_space > max_transposition_space:
                raise IdOverflow(f"Computed transposition space is {t_space} but the maximum is {max_transposition_space}.")
            if t_space <= 0:
                raise ValueError("Transposition space must be > 0.")
            return t_space
        
        global_vars = GlobalVariables(
            seed = seed,
            max_depth = max_depth,
            distribution = distribution,
            branching_factor_base = branching_factor_base,
            branching_factor_variance = branching_factor_variance,
            terminal_minimum_depth = terminal_minimum_depth,
            child_depth_minumum = child_depth_minumum,
            child_depth_maximum = child_depth_maximum,
            locality_grouping = locality_grouping,
            true_value_forced_ratio = true_value_forced_ratio,
            true_value_similarity_chance = true_value_similarity_chance,
            true_value_tie_chance = true_value_tie_chance,
            symmetry_factor = symmetry_factor,
            symmetry_frequency = symmetry_frequency,
            heuristic_accuracy_base = heuristic_accuracy_base,
            heuristic_depth_scaling = heuristic_depth_scaling,
            heuristic_locality_scaling = heuristic_locality_scaling,
            max_transposition_space_size = max_transposition_space
        )
        global_funcs = GlobalFunctions(
            branching_function = branching_function,
            child_true_value_function = child_value_function,
            child_depth_function = child_depth_function,
            transposition_space_function = transposition_space_function_wrapper,
            heuristic_value_function = heuristic_value_function
        )
        self.globals = GlobalParameters(
            global_vars,
            global_funcs,
            retain_graph
        )
        root_node = StateNode(
            stateid=0, globals=self.globals, true_value=0, 
            player=Player.MAX, depth=0, tspace_record=0, parent=None)
        self.set_root(root_node._encode_id( # type: ignore
            root_node.true_value,
            root_node.player,
            root_node.depth,
            root_node.tspace_record
        ))
    
    def __str__(self) -> str:
        return str(self._current)
    
    def __repr__(self) -> str:
        return self._current.__repr__()
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self._current.is_root()
    
    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self._current.is_terminal()
    
    def true_value(self) -> int:
        """Return the current state's true value. Value is in [-1, 1]"""
        return self._current.true_value
    
    def heuristic_value(self) -> float:
        """Return the estimated value of the current state using the heuristic evaluation function."""
        return self._current.heuristic_value()
    
    def player(self) -> Player:
        """Return the player associated with the current state."""
        return self._current.player
    
    def depth(self) -> int:
        """Return the depth of the current node."""
        return self._current.depth

    def id(self) -> int:
        """Return the id of the current state."""
        return self._current.id

    def actions(self) -> list[int]:
        """Return the current state's possible actions."""
        return self._current.actions()

    def make(self, action: int) -> Self:
        """Transition to the next state via action (represented as an index into the states children)."""
        if self.is_terminal():
            raise TerminalHasNoChildren
        actions = self._current.actions()
        if not action in actions:
            raise ValueError(f"No action {action} among available actions {actions}.")
        self._current = self._current.children[action]
        return self
    
    def make_random(self) -> Self:
        """Make a random action."""
        if self.is_terminal():
            raise TerminalHasNoChildren
        actions = self.actions()
        i = self._RNG.next_int(high=len(actions)-1)
        self.make(actions[i])
        return self

    def undo(self) -> Self:
        """Move back to previous state."""
        if self._current.parent is None:
            raise RootHasNoParent()
        self._current = self._current.parent
        if not self.globals.retain_graph:
            self._current.reset() # release memory as we climb back up the tree
        return self
    
    def set_root(self, state_id: int) -> Self:
        """Set the given state_id as the new root. Note that doing this with retain_graph=True 
        will destroy the previously retained graph."""
        true_value = extract_true_value_from_id(state_id)
        player = extract_player_from_id(state_id)
        depth = extract_depth_from_id(state_id, bit_size(self.globals.vars.max_depth))
        tspace_record = extract_tspace_record_from_id(state_id, 
                            bit_size(self.globals.vars.max_transposition_space_size))
        self._root = StateNode(
            stateid=state_id, globals=self.globals, true_value=true_value, 
            player=player, depth=depth, tspace_record=tspace_record, parent=None)
        self._current: StateNode = self._root
        return self

    def draw(self) -> None:
        """Draw the current node graph. Best used when retaining the tree."""
        visited: set[tuple[int, int]] = set()
        def draw_graph_recur(graph: Digraph, node: StateNode):
            graph.node(name=str(node.id), label=str(node))
            if node.is_terminal():
                return
            for child in node.children:
                edge = (node.id, child.id)
                if edge not in visited:
                    visited.add(edge)
                    graph.edge(str(node.id), str(child.id))
                draw_graph_recur(graph, child)
        
        graph = Digraph(format="png")
        draw_graph_recur(graph, self._root)
        graph.render(f"trees/tree_seed_{self.globals.vars.seed}" , view=True)
