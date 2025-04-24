import mmh3
from constants import HASH_OUTPUT_TMAX
from custom_types import RandomnessDistribution


class RNGHasher():
    """Deterministic random number generator. Outputs uniform values from given input"""
    def __init__(self, distribution: RandomnessDistribution, nodeid: int=0, seed: int=0):
        self.distribution = distribution
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
    
    def next_float(self) -> float:
        """Return a pseudo-random float between 0 and 1."""
        if self.distribution == RandomnessDistribution.UNIFORM:
            return self.hash() / HASH_OUTPUT_TMAX
        if self.distribution == RandomnessDistribution.GAUSSIAN:
            # TODO add gaussian logic
            pass
        return 0.0
    
    def next_int(self) -> int:
        """Return a pseudo-random integer."""
        if self.distribution == RandomnessDistribution.UNIFORM:
            return self.hash()
        if self.distribution == RandomnessDistribution.GAUSSIAN:
            # TODO: add gaussian logic
            pass
        return 0
    
    def reset(self) -> None:
        """Reset the RNG."""
        self._times_hashed = 0
