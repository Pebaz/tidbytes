from .mem_types import *
from .von_neumann import *

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

class Mem:
    def __init__(self):
        self.rgn = MemRgn()


# * Getting

def op_get_bits_u8_bit_arr(): ...
def op_get_bits_u8_byte_arr(): ...

# * Setting

def op_set_bits_u8_bit_arr(): ...
def op_set_bits_u8_byte_arr(): ...
def op_set_bits_u16_arr(): ...
def op_set_bits_u32_arr(): ...
def op_set_bits_u64_arr(): ...

def op_set_bits_u8(): ...
def op_set_bits_u16(): ...
def op_set_bits_u32(): ...
def op_set_bits_u64(): ...
def op_set_bits_i8(): ...
def op_set_bits_i16(): ...
def op_set_bits_i32(): ...
def op_set_bits_i64(): ...
def op_set_bytes_u8(): ...
def op_set_bytes_u16(): ...
def op_set_bytes_u32(): ...
def op_set_bytes_u64(): ...
def op_set_bytes_i8(): ...
def op_set_bytes_i16(): ...
def op_set_bytes_i32(): ...
def op_set_bytes_i64(): ...

# * Conversion Operations
# TODO(pbz): I'd like to point out that I think it would be possible to not
# TODO(pbz): include these C-ABI-inspired conversion operations but I don't want
# TODO(pbz): to reduce this API surface as far as possible since it can be seen
# TODO(pbz): from outside mathematics that doing so is not best for the user.

def op_into_u8_bit_arr(): ...
def op_into_u8_byte_arr(): ...
def op_into_u32_arr(): ...
def op_into_u8(): ...
def op_into_u16(): ...
def op_into_u32(): ...
def op_into_u64(): ...

def op_into_i8_arr(): ...
def op_into_i32_arr(): ...
def op_into_i8(): ...
def op_into_i16(): ...
def op_into_i32(): ...
def op_into_i64(): ...

# Conversion functions also go the other way
def op_from_bit_length(bit_length: int) -> Mem:
    mem = Mem()
    mem.bits = [0] * bit_length

def op_from_byte_length(byte_length: int) -> Mem:
    mem = Mem()
    mem.bits = [0] * 8 * byte_length

def op_from_u8_bit_arr(): ...
def op_from_u8_byte_arr(): ...
