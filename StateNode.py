from utils import *
from RNGHasher import RNGHasher


class StateNode():
    def __init__(self, nodeid: int, branching_factor: int, max_depth: int, max_states: int,
                 node_type_ratio: float=0.5, seed: int=0, retain_tree: int=False):
        # globals
        self.id: int = nodeid
        self.branching_factor: int = branching_factor
        self.max_depth: int = max_depth
        self.max_states = max_states
        self.seed = seed
        self.node_type_ratio = node_type_ratio # choice / forced
        self.retain_tree = retain_tree

        # locals
        self.parent: "StateNode" = None
        self.value: int = None
        self.depth: int = None
        self.player: Player = None
        self.node_type: NodeType = None
        
        self.children: list["StateNode"] = []
        self.hasher = RNGHasher(self.id, self.seed)
    
    def __repr__(self):
        return f"id:{self.id}, depth:{self.depth}, children:{len(self.children)}"

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth == self.max_depth
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.depth == 0

    def actions(self) -> list[int]:
        """Return values of children."""
        self.generate_children()
        return [child.value for child in self.children]
    
    def reset(self):
        """Reset state to before an action on it was taken."""
        self.children = []
        self.hasher.reset()
        return self

    def generate_children(self) -> None:
        """Generate child states."""
        if self.is_terminal():
            return
        if self.children:
            return
        new_children: list["StateNode"] = []
        for i in range(self.branching_factor):
            child_id = self.hasher.next_int() % self.max_states
            child: StateNode = StateNode(
                child_id, self.branching_factor, self.max_depth, self.max_states, self.node_type_ratio, self.seed
            )
            child.parent = self
            child.depth = self.depth + 1
            child.player = Player(-self.player.value)
            child.node_type = NodeType.CHOICE if \
                self.hasher.next_uniform() < self.node_type_ratio else NodeType.FORCED
            if child.id not in [child.id for child in self.children]:
                new_children.append(child)
        
        if self.node_type == NodeType.FORCED:
            for child in new_children:
                child.value = self.value
        else:
            random_child_idx = int(self.hasher.next_uniform() * self.branching_factor)
            new_children[random_child_idx].value = self.value
            for i in range(self.branching_factor):
                if i == random_child_idx:
                    continue
                # assumes values have an even chance of being -1 or 1
                new_children[i].value = 1 if self.hasher.next_uniform() < 0.5 else -1
        self.children = new_children
        return self
