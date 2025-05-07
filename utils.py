from custom_types import *

def bit_size(n: int) -> int:
    """Return the number of bits necessary to represent integer n in binary."""
    bits = 0
    while n:
        n >>= 1
        bits += 1
    return bits

def encode_value_to_bits(value: int) -> int:
    match value:
        case -1:
            return 0
        case 0:
            return 1
        case 1:
            return 2
        case _:
            raise ValueError(f"Invalid value {value}. Value must be in [-1, 1].")
        
def decode_value_bits(value_bits: int) -> int:
    match value_bits:
        case 0:
            return -1
        case 1:
            return 0
        case 2:
            return 1
        case _:
            raise ValueError(f"Invalid bit representation {bin(value_bits)[2:]} of Value.")