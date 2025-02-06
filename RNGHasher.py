import mmh3
from utils import TMAX_32BIT


class RNGHasher():
    def __init__(self, seed_str: str='', seed_int: int=0):
        self.seed_str = seed_str
        self.seed_int = seed_int
        self._times_hashed: int = 0
    
    def uniform_hash(self, input: str) -> float:
        """Return a uniformly distributed value based on the input string and global 
        seed."""
        hash_32bit = mmh3.hash(input, seed=self.seed_int, signed=False)
        return hash_32bit / TMAX_32BIT
    
    def next_random(self):
        """Uniform pseudo-RNG function that retains determinism."""
        hash_input = f"{self.seed_str}+{self._times_hashed}"
        self._times_hashed += 1
        return self.uniform_hash(hash_input)
    
    def reset(self):
        """Reset the RNG."""
        self._times_hashed = 0