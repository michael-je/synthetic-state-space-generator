import mmh3
from utils import HASH_OUTPUT_TMAX


class RNGHasher():
    """Deterministic random number generator. Outputs uniform values from given input"""
    def __init__(self, nodeid: int=0, seed: int=0):
        self.nodeid = nodeid
        self.seed = seed
        self._times_hashed: int = 0
    
    def hash(self) -> int:
        """Return a pseudo random integer value based on the nodeid and global seed."""
        hash_input = f"{self.nodeid}.{self._times_hashed}"
        hash_input_bytes = hash_input.encode()
        hash_64bit, _ = mmh3.mmh3_x64_128_utupledigest(hash_input_bytes, self.seed)
        self._times_hashed += 1
        return hash_64bit
    
    def next_uniform(self) -> float:
        """Return a uniform pseudo-random value."""
        return self.hash() / HASH_OUTPUT_TMAX
    
    def next_int(self) -> int:
        """Return a pseudo-random integer."""
        return self.hash()
    
    def reset(self) -> None:
        """Reset the RNG."""
        self._times_hashed = 0