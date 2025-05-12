from custom_types import *
from constants import *

def bit_size(n: int) -> int:
    """Return the number of bits necessary to represent integer n in binary."""
    bits = 0
    while n:
        n >>= 1
        bits += 1
    return bits

def encode_true_value_to_bits(true_value: int) -> int:
    """Encode a true value in the range [-1, 1] to an appropriate bit representation."""
    if not -1 <= true_value <= 1:
        raise ValueError(f"Invalid value {true_value}. Value must be in [-1, 1].")
    return true_value + 1
        
def decode_true_value_bits(true_value_bits: int) -> int:
    """Inverse to the true value encoding function."""
    if not 0 <= true_value_bits <= 2:
        raise ValueError(f"Invalid bit representation {bin(true_value_bits)[2:]} of Value.")
    return true_value_bits - 1

def extract_information_from_id(state_id: int, msb_offset: int, bit_size: int) -> int:
    """Used to extract information encoded in a state_id using bit offsets. msb_position 
    is the number of bits that the value's msb is away from the id's msb."""
    bit_mask = (1 << bit_size) - 1
    shifted_value = state_id >> (ID_BIT_SIZE - msb_offset - bit_size)
    return shifted_value & bit_mask

def extract_true_value_from_id(state_id: int) -> int:
    """Extract and return the true_value from a state's id."""
    value_bits = extract_information_from_id(
        state_id, 
        0, 
        ID_TRUE_VALUE_BIT_SIZE)
    return decode_true_value_bits(value_bits)

def extract_player_from_id(state_id: int) -> Player:
    """Extract and return the player from a state's id."""
    return Player(extract_information_from_id(
        state_id, 
        ID_TRUE_VALUE_BIT_SIZE, 
        ID_PLAYER_BIT_SIZE))

def extract_depth_from_id(state_id: int, depth_bit_size: int) -> int:
    """Extract and return the depth from a state's id."""
    result = extract_information_from_id(
        state_id, 
        ID_TRUE_VALUE_BIT_SIZE + ID_PLAYER_BIT_SIZE, 
        depth_bit_size)
    return result

def extract_tspace_record_from_id(state_id: int, tspace_record_bit_size: int) -> int:
    """Extract and return the tspace_record from a state's id."""
    return extract_information_from_id(
        state_id,
        ID_BIT_SIZE - tspace_record_bit_size,
        tspace_record_bit_size)

def assign_child_true_value_information(
    child_true_value_information: ChildTrueValueInformation, player: Player, child_true_value: int):
    """Helper function to correctly increment values of child_true_value_information."""
    match child_true_value:
        case 0:
            child_true_value_information.total_child_ties += 1
        case 1:
            if player == Player.MAX:
                child_true_value_information.total_child_wins += 1
            else:
                child_true_value_information.total_child_losses += 1
        case -1:
            if player == Player.MIN:
                child_true_value_information.total_child_wins += 1
            else:
                child_true_value_information.total_child_losses += 1
        case _: # should never happen, but handles type error
            raise ValueError("Invalid child value.")
    