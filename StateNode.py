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
        self._info_dump: InfoDump|None = None
        
        self.children: list[StateNode] = []
        self._RNG: RNGHasher = RNGHasher(self.id, self.globals.seed)
    
    def __str__(self) -> str:
        random_id_bits_mask = (1 << (ID_BITS_SIZE - self.globals.id_depth_bits_size)) - 1
        return f"{self.depth}-{self.id & random_id_bits_mask}"

    def __repr__(self) -> str:
        return str(self)
    
    def info_dump(self) -> InfoDump:
        if self._info_dump is None:
            if self.parent is not None:
                info_dump_parent = InfoDumpParent(
                    id=self.parent.id,
                    value=self.parent.value,
                    depth=self.parent.depth,
                    branching_factor=self.parent.branching_factor()
                )
                info_dump_siblings = InfoDumpSiblings(
                    id=[child.id for child in self.parent.children],
                    value=[child.value for child in self.parent.children],
                    depth=[child.depth for child in self.parent.children],
                    branching_factor=lambda : [child.branching_factor() for child in self.parent.children] if self.parent else []
                )
            else:
                info_dump_parent = None
                info_dump_siblings = None
            info_dump_self = InfoDumpSelf(
                id=self.id,
                value=self.value,
                depth=self.depth,
                branching_factor=self._branching_factor
            )
            self._info_dump = InfoDump(
                parent=info_dump_parent,
                self=info_dump_self,
                siblings=info_dump_siblings,
                max_depth=self.globals.max_depth
            )
        return self._info_dump
    
    def _calculate_child_depth(self) -> int:
        child_depth = self.globals.child_depth_function(
            self._RNG.next_int, self._RNG.next_uniform, self.info_dump())
        if child_depth >= (1 << self.globals.id_depth_bits_size):
            raise IdOverflow(f"Depth {self.depth} too large for {self.globals.id_depth_bits_size} bits")
        if child_depth < 0:
            raise IdOverflow(f"Depth can not be negative.")
        return child_depth
    
    def _generate_child_id(self, child_depth: int) -> int:
        """Generate a child id using values for depth and random bits."""
        depth_bits = child_depth << (ID_BITS_SIZE - self.globals.id_depth_bits_size)
        random_bits = self._RNG.next_int() % self.globals.transposition_space_map[child_depth]
        return depth_bits | random_bits
    
    def kill_siblings(self) -> None:
        """Deallocate sibling memory."""
        if self.parent is None:
            return # in case we are root
        self.parent.children = [self]

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth >= self.globals.max_depth - 1 or self.branching_factor() < 1
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.parent is None

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
            self._branching_factor = self.globals.branching_function(
                self._RNG.next_int, self._RNG.next_uniform, self.info_dump())
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
            child_value = self.globals.child_value_function(
                self._RNG.next_int, self._RNG.next_uniform, self.info_dump())
            new_child = StateNode(
                stateid=child_id, value=child_value, depth=child_depth, globals=self.globals, parent=self)
            new_children.append(new_child)
        self.children = new_children
        return self
