from enum import Enum
import mmh3

TMAX_32BIT = 2**32 - 1
class NodeType(Enum):
    CHOICE = 0
    FORCED = 1
class Player(Enum):
    MAX = 1
    MIN = -1

root_params = {
    "parent": None,
    "value": 1,
    "_id_arr": [0],
    "depth": 0,
    "player": Player.MAX,
    "node_type": NodeType.CHOICE,
}


class State():
    def __init__(self, branching_factor: int, max_depth: int,
                 node_type_ratio: float=0.5, seed: int=0):
        # globals
        self.branching_factor: int = branching_factor
        self.max_depth: int = max_depth
        self.seed = seed
        self.node_type_ratio = node_type_ratio # choice / forced

        # locals
        self.parent: "State" = None
        self.value: int = None
        self._id_arr: int = None
        self.depth: int = None
        self.player: Player = None
        self.node_type: NodeType = None
        if self.parent is None:
            self.__dict__.update(root_params)
        
        self.children: list["State"] = None 
        self._times_hashed = 0 # used to ensure the state will not regnerate hash values

    def actions(self) -> list["State"]:
        """Return values of all children."""
        if self.children is None:
            self._generate_children()
        return [child.value for child in self.children]

    def make(self, i: int) -> "State":
        """Take action i."""
        self = self.children[i]
        return self

    def is_terminal(self) -> bool:
        """Return whether the current state is terminal."""
        if self.children is None:
            self._generate_children()
        if self.children == []:
            return True
        return False
    
    def undo(self):
        """Walk back up the tree."""
        # if not self.globals["store_traversed"]:
        #     self.children = []
        self = self.parent
        return self
    
    def generate_id(self, parent_id_arr: list[int], sibling_id: int):
        """Generate unique id for the state."""
        self._id_arr = parent_id_arr + [sibling_id]
    
    def id(self):
        return '.'.join(str(n) for n in self._id_arr)
    
    def __str__(self):
        return f"{self.id()=}, {self.depth=}, {self.is_terminal()=}, {self.player.name=}, {self.node_type.name=}, {self.actions()=}"

    def __repr__(self):
        return str(self)

    def _uniform_hash(self, input: str) -> float:
        """Return a uniformly distributed value based on the input string and global 
        seed."""
        hash_32bit = mmh3.hash(input, seed=self.seed, signed=False)
        return hash_32bit / TMAX_32BIT
    
    def _get_next_random(self):
        hash_input = f"{self.id()} {self._times_hashed}"
        self._times_hashed += 1
        return self._uniform_hash(hash_input)

    def _generate_children(self) -> None:
        """Generate child states."""
        new_children: list["State"] = []
        if self.depth >= self.max_depth:
            self.children = new_children
            return
        
        for i in range(self.branching_factor):
            child: State = State(
                self.branching_factor, self.max_depth, self.node_type_ratio, self.seed
            )
            child.parent = self
            child.generate_id(self._id_arr, i)
            child.depth = self.depth + 1
            child.player = Player(-self.player.value)
            child.node_type = NodeType.CHOICE if self._get_next_random() < self.node_type_ratio else NodeType.FORCED
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

                
        

