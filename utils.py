from enum import Enum

TMAX_32BIT = 2**32 - 1

class NodeType(Enum):
    CHOICE = 0
    FORCED = 1

class Player(Enum):
    MAX = 1
    MIN = -1
