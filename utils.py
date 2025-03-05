from enum import Enum
from dataclasses import dataclass

TMAX_32BIT = 2**32 - 1

class NodeType(Enum):
    CHOICE = 0
    FORCED = 1

class Player(Enum):
    MAX = 1
    MIN = -1

@dataclass
class GlobalParameters:
    branching_factor: int
    max_depth: int
    max_states: int
    node_type_ratio: float
    seed: int
    retain_tree: bool
