import math
import mmh3
from constants import HASH_OUTPUT_TMAX
from custom_types import RandomnessDistribution as Dist
from custom_exceptions import *


GAUSSIAN_MAX_DIST_FROM_MEAN = 3.4 # not a true maximum, but we don't care about extreme outliers

# Acklam's Algorithm for computing the normal quantile function (inverse normal)
def inverse_normal(p: float) -> float:
    # coefficients in rational approximations
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]
    # break-points
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    elif p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                 ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    else:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
               (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)


class RNGHasher():
    """Deterministic random number generator. Outputs uniform values from given input"""
    def __init__(self, distribution: Dist, nodeid: int=0, seed: int=0):
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
    
    def next_float(self, low: float=0, high: float=1, distribution: Dist|None=None) -> float:
        """Return a pseudo-random float in [low, high]."""
        dist_range = high - low
        if low > high:
            raise ValueError("low must be <= high.")
        if distribution is None:
            distribution = self.distribution
        
        match distribution:
            case Dist.UNIFORM:
                return (self.hash() / HASH_OUTPUT_TMAX) * dist_range + low
            case Dist.GAUSSIAN:
                normal = inverse_normal(self.next_float(distribution=Dist.UNIFORM))
                result = (normal + GAUSSIAN_MAX_DIST_FROM_MEAN) / (2*GAUSSIAN_MAX_DIST_FROM_MEAN) # scale to [0, 1]
                result = result * dist_range + low # scale to [low, high]
                result = min(high, max(low, result)) # simply cut off the outliers
                return result
    
    def next_int(self, low: int=0, high: int=HASH_OUTPUT_TMAX, distribution: Dist|None=None) -> int:
        """Return a pseudo-random integer in [low, high]."""
        dist_range = high - low
        if dist_range > HASH_OUTPUT_TMAX:
            raise ValueError(f"Range {low}-{high} is out of bounds.")
        if low > high:
            raise ValueError("low must be <= high.")
        if not (isinstance(low, int) and isinstance(high, int)): # type: ignore
            raise ValueError("low and high must be integers.")
        if distribution is None:
            distribution = self.distribution
        
        match distribution:
            case Dist.UNIFORM:
                return self.hash() % (dist_range + 1) + low
            case Dist.GAUSSIAN:
                return round(self.next_float(low=low, high=high, distribution=Dist.GAUSSIAN))
    
    def reset(self) -> None:
        """Reset the RNG."""
        self._times_hashed = 0
