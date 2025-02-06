from utils import *
import mmh3


class StateNode():
    def __init__(self, branching_factor: int, max_depth: int,
                 node_type_ratio: float=0.5, seed: int=0):
        # globals
        self.branching_factor: int = branching_factor
        self.max_depth: int = max_depth
        self.seed = seed
        self.node_type_ratio = node_type_ratio # choice / forced

        # locals
        self.parent: "StateNode" = None
        self.value: int = None
        self.id: str = None
        self.depth: int = None
        self.player: Player = None
        self.node_type: NodeType = None
        
        self.children: list["StateNode"] | None = None 
        self._times_hashed = 0 # used to ensure the state will not regnerate hash values

    def is_terminal(self) -> bool:
        """Return true if the state is a terminal."""
        return self.depth == self.max_depth

    def actions(self) -> list[int]:
        """Return values of children."""
        if self.children is None:
            self.generate_children()
        return [child.value for child in self.children]
    
    def reset(self):
        """Reset state to before an action on it was taken."""
        self.children = None
        self._times_hashed = 0

    def set_id(self, sibling_id: int):
        """Generate unique id for the state."""
        self.id = f"{self.parent.id}.{sibling_id}"

    def _uniform_hash(self, input: str) -> float:
        """Return a uniformly distributed value based on the input string and global 
        seed."""
        hash_32bit = mmh3.hash(input, seed=self.seed, signed=False)
        return hash_32bit / TMAX_32BIT
    
    def _get_next_random(self):
        """Uniform pseudo-randomness function that retains determinism."""
        hash_input = f"{self.id}+{self._times_hashed}"
        self._times_hashed += 1
        return self._uniform_hash(hash_input)

    def generate_children(self) -> None:
        """Generate child states."""
        new_children: list["StateNode"] = []
        if self.depth >= self.max_depth:
            self.children = new_children
            return
        
        for i in range(self.branching_factor):
            child: StateNode = StateNode(
                self.branching_factor, self.max_depth, self.node_type_ratio, self.seed
            )
            child.parent = self
            child.set_id(i)
            child.depth = self.depth + 1
            child.player = Player(-self.player.value)
            child.node_type = NodeType.CHOICE if \
                self._get_next_random() < self.node_type_ratio else NodeType.FORCED
            new_children.append(child)
        
        if self.node_type == NodeType.FORCED:
            for child in new_children:
                child.value = self.value
        else:
            random_child_idx = int(self._get_next_random() * self.branching_factor)
            new_children[random_child_idx].value = self.value
            for i in range(self.branching_factor):
                if i == random_child_idx:
                    continue
                # assumes values have an even chance of being -1 or 1
                new_children[i].value = 1 if self._get_next_random() < 0.5 else -1
        self.children = new_children
