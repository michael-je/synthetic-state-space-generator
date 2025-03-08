import mmh3
from utils import TMAX_32BIT


class RNGHasher():
    """Deterministic random number generator. Outputs uniform values from given input"""
    def __init__(self, nodeid: int=0, seed_int: int=0):
        self.nodeid = nodeid
        self.seed_int = seed_int
        self._times_hashed: int = 0
    
    def hash(self) -> int:
        """Return a pseudo random integer value based on the nodeid and global seed."""
        hash_input = f"{self.nodeid}+{self._times_hashed}"
        hash_32bit = mmh3.hash(hash_input, seed=self.seed_int, signed=False)
        self._times_hashed += 1
        return hash_32bit
    
    def next_uniform(self) -> float:
        """Return a uniform pseudo-random value."""
        return self.hash() / TMAX_32BIT
    
    def next_int(self) -> int:
        """Return a pseudo-random integer."""
        return self.hash()
    
    def reset(self) -> None:
        """Reset the RNG."""
        self._times_hashed = 0