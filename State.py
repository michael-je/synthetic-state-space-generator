from graphviz import Digraph
from typing import Self

from StateNode import StateNode
from RNGHasher import RNGHasher
from utils import bit_size
from constants import ID_BITS_SIZE
from custom_types import *
from custom_types import RandomnessDistribution as Dist
from exceptions import IdOverflow, RootHasNoParent
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
                 value_minimum: int=0,
                 value_maximum: int=1,
                 child_depth_minumum: int=1,
                 child_depth_maximum: int=1,
                 cycle_chance: float=0,
                 balanced_tree: bool=True,
                 min_branch_depth: int = 1,
                 max_branch_depth: int = 2**8-1,

                 branching_function: BranchingFunction=default_branching_function, 
                 child_value_function: ChildValueFunction=default_child_value_function, 
                 child_depth_function: ChildDepthFunction=default_child_depth_function,
                 transposition_space_function: TranspositionSpaceFunction=default_transposition_space_function,
                 heuristic_value_function: HeuristicValueFunction=default_heuristic_value_function,
                 branch_depth_function: BranchDepthFunction=default_branch_depth_func):

        
        self._RNG = RNGHasher(distribution=distribution, seed=seed)
        id_depth_bits_size = bit_size(max_depth)
        transposition_space_map = transposition_space_function(
            self._RNG.next_int, self._RNG.next_float, max_depth)
        # TODO: test
        for depth in transposition_space_map:
            if bit_size(transposition_space_map[depth]) > (ID_BITS_SIZE - id_depth_bits_size):
                raise IdOverflow(f"Transposition space value {transposition_space_map[depth]} at depth {depth} too large.")
        
        global_vars = GlobalVariables(
            root_value = root_value,
            seed = seed,
            max_depth = max_depth,
            distribution = distribution,
            branching_factor_base = branching_factor_base,
            branching_factor_variance = branching_factor_variance,
            terminal_minimum_depth = terminal_minimum_depth,
            value_minimum = value_minimum,
            value_maximum = value_maximum,
            child_depth_minumum = child_depth_minumum,
            child_depth_maximum = child_depth_maximum,
            cycle_chance=cycle_chance,
            id_depth_bits_size = id_depth_bits_size,
            balanced_tree = balanced_tree,
            min_branch_depth=min_branch_depth,
            max_branch_depth=max_branch_depth
        )
        global_funcs = GlobalFunctions(
            branching_function = branching_function,
            child_value_function = child_value_function,
            child_depth_function = child_depth_function,
            transposition_space_map = transposition_space_map,
            heuristic_value_function = heuristic_value_function,
            branch_depth_function=branch_depth_function
        )
        self.globals = GlobalParameters(
            global_vars,
            global_funcs,
            retain_tree
        )

        self._root: StateNode = StateNode(
            stateid=0, value=root_value, depth=0, globals=self.globals, parent=None, branch_max_depth=max_depth)
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
        return self._current.depth

    def id(self) -> int:
        """Return the id of the current state."""
        return self._current.id

    def actions(self) -> list[int]:
        """Return the current state's possible actions."""
        return self._current.actions()
    
    def value(self) -> int:
        """Return the current state's true value."""
        return self._current.value
    
    def heuristic_value(self) -> int:
        """Return the estimated value of the current state using the heuristic evaluation function."""
        return self._current.heuristic_value()

    def make(self, action: int) -> Self:
        """Transition to the next state via action (represented as an index into the states children)."""
        self._current.generate_children()
        self._current = self._current.children[action]
        if not self.globals.retain_tree:
            if self._current.parent is None:
                raise RootHasNoParent() # can't happen, but suppresses type warning
            self._current.parent.kill_siblings()
        return self
    
    def make_random(self) -> Self:
        """Make a random action."""
        actions = self.actions()
        i = int(self._RNG.next_float() * len(actions))
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
    
    # TODO: add draw whole tree function
