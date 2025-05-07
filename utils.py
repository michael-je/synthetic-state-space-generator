from custom_types import *

def bit_size(n: int) -> int:
    """Return the number of bits necessary to represent integer n in binary."""
    bits = 0
    while n:
        n >>= 1
        bits += 1
    return bits

def encode_value_to_bits(value: Value) -> int:
    match value:
        case Value.TIE:
            return 0
        case Value.WIN:
            return 1
        case value.LOSS:
            return 2
        
def decode_value_bits(value_bits: int) -> Value:
    match value_bits:
        case 0:
            return Value.TIE
        case 1:
            return Value.WIN
        case 2:
            return Value.LOSS
        case _:
            raise ValueError("Invalid bit representation of Value.")