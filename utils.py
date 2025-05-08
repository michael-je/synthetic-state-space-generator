from custom_types import *

def bit_size(n: int) -> int:
    """Return the number of bits necessary to represent integer n in binary."""
    bits = 0
    while n:
        n >>= 1
        bits += 1
    return bits

def encode_value_to_bits(value: int) -> int:
    if not -1 <= value <= 1:
        raise ValueError(f"Invalid value {value}. Value must be in [-1, 1].")
    return value + 1
        
def decode_value_bits(value_bits: int) -> int:
    if not 0 <= value_bits <= 2:
        raise ValueError(f"Invalid bit representation {bin(value_bits)[2:]} of Value.")
    return value_bits - 1