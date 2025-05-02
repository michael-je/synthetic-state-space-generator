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
                 root_value: int=1,
                 seed: int=0, 
                 max_depth: int=2**8-1,
                 distribution: RandomnessDistribution=Dist.UNIFORM,
                 retain_tree: bool=False,
                 
                 branching_factor_base: int=2,
                 branching_factor_variance: int=0,
                 terminal_minimum_depth: int=0,
                 child_depth_minumum: int=1,
                 child_depth_maximum: int=1,

                 branching_function: BranchingFunction=default_branching_function, 
                 value_function: ValueFunction=default_value_function, 
                 child_depth_function: ChildDepthFunction=default_child_depth_function,
                 transposition_space_function: TranspositionSpaceFunction=default_transposition_space_function,
                 heuristic_value_function: HeuristicValueFunction=default_heuristic_value_function):
        
        if max_depth <= 0:
            raise ValueError("max_depth must be > 0.")
        if bit_size(max_depth) >= ID_BIT_SIZE:
            raise ValueError("max_depth too large.")
        if child_depth_minumum > child_depth_maximum:
            raise ValueError("child_depth_minimum must be > child_depth_maximum.")
        if terminal_minimum_depth < 0:
            raise ValueError("terminal_minimum_depth must be > 0.")
        if branching_factor_base < 0:
            raise ValueError("branching_factor_base must be >= 0.")
        if branching_factor_variance < 0:
            raise ValueError("branching_factor_variance must be >= 0.")
        
        self._RNG = RNGHasher(distribution=distribution, seed=seed)
        max_transposition_space = 2**(ID_BIT_SIZE - bit_size(max_depth))
        
        self.transposition_space_map: dict[int, int] = dict()
        def transposition_space_function_wrapper(
                randint: RandomIntFunction, 
                randf: RandomFloatFunction, 
                globals: GlobalVariables, 
                depth: int) -> int:
            t_space = self.transposition_space_map.get(depth)
            if t_space is None:
                t_space = transposition_space_function(randint, randf, globals, depth)
                self.transposition_space_map[depth] = t_space
            if t_space > max_transposition_space:
                # TODO: test
                raise IdOverflow(f"Computed transposition space is {t_space} but the maximum is {max_transposition_space}.")
            if t_space < 1:
                # TODO: test
                raise ValueError("Transposition space must be > 0.")
            return t_space
        
        global_vars = GlobalVariables(
            root_value = root_value,
            seed = seed,
            max_depth = max_depth,
            distribution = distribution,
            branching_factor_base = branching_factor_base,
            branching_factor_variance = branching_factor_variance,
            terminal_minimum_depth = terminal_minimum_depth,
            child_depth_minumum = child_depth_minumum,
            child_depth_maximum = child_depth_maximum,
            max_transposition_space_size = max_transposition_space
        )
        global_funcs = GlobalFunctions(
            branching_function = branching_function,
            value_function = value_function,
            child_depth_function = child_depth_function,
            transposition_space_function = transposition_space_function_wrapper,
            heuristic_value_function = heuristic_value_function
        )
        self.globals = GlobalParameters(
            global_vars,
            global_funcs,
            retain_tree
        )

        self._root: StateNode = StateNode(
            stateid=0, globals=self.globals, parent=None)
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
    
    def depth(self) -> int:
        """Return the depth of the current node."""
        return self._current.depth()

    def id(self) -> int:
        """Return the id of the current state."""
        return self._current.id

    def actions(self) -> list[int]:
        """Return the current state's possible actions."""
        return self._current.actions()
    
    def value(self) -> int:
        """Return the current state's true value."""
        return self._current.value()
    
    def heuristic_value(self) -> int:
        """Return the estimated value of the current state using the heuristic evaluation function."""
        return self._current.heuristic_value()

    def make(self, action: int) -> Self:
        """Transition to the next state via action (represented as an index into the states children)."""
        if self.is_terminal():
            raise TerminalHasNoChildren
        self._current.generate_children()
        if not 0 <= action < len(self._current.children):
            raise ValueError(f"No action {action} among children {self._current.children}.")
        self._current = self._current.children[action]
        if not self.globals.retain_tree:
            if self._current.parent is None:
                raise RootHasNoParent() # can't happen, but suppresses type warning
            self._current.parent.kill_siblings()
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
        if not self.globals.retain_tree:
            self._current.reset() # release memory as we climb back up the tree
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
