from utils import *
from RNGHasher import RNGHasher


class StateNode():
    def __init__(self, nodeid: int, globals: GlobalParameters,
                 node_type: NodeType=None, value: int=0, parent: "StateNode"=None, 
                 depth: int=None, player: Player=None):
        self.id = nodeid
        self.globals = globals
        self.node_type = node_type
        self.value = value
        self.parent = parent
        self.player = player
        
        if depth is None:
            self.depth = self.parent.depth + 1 if self.parent else 0
        if player is None:
            self.player = Player(-self.parent.player.value) if self.parent else Player.MAX
        
        self.children: list["StateNode"] = []
        self.hasher = RNGHasher(self.id, self.globals.seed)
        self.branching_factor = self.globals.branching_function(self.depth, self.hasher.next_uniform())
    
    def __repr__(self):
        return f"id:{self.id}, depth:{self.depth}, children:{len(self.children)}"

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth == self.globals.max_depth
    
    def is_root(self) -> bool:
        """Return true if the state is the root."""
        return self.depth == 0

    def actions(self) -> list[int]:
        """Return indices of children."""
        self.generate_children()
        return list(range(len(self.children)))
    
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
            child_id = self.hasher.next_int() % self.globals.max_states
            child_node_type = NodeType.CHOICE if \
                self.hasher.next_uniform() < self.globals.node_type_ratio else NodeType.FORCED
            child: StateNode = StateNode(child_id, self.globals, node_type=child_node_type, parent=self)
            if child.id not in [child.id for child in self.children]:
                new_children.append(child)
        
        if self.node_type == NodeType.FORCED:
            for child in new_children:
                child.value = self.value
        else:
            random_child_idx = int(self.hasher.next_uniform() * len(new_children))
            new_children[random_child_idx].value = self.value
            for i in range(self.branching_factor):
                if i == random_child_idx:
                    continue
                # assumes values have an even chance of being -1 or 1
                new_children[i].value = 1 if self.hasher.next_uniform() < 0.5 else -1
        self.children = new_children
        return self
