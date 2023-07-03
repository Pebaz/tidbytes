import ctypes, sys, struct
from array import array
from typing import Union, List
from .mem_types import Order
from .idiomatic import Mem

u8 = ctypes.c_ubyte
u16 = ctypes.c_uint16
u32 = ctypes.c_uint32
u64 = ctypes.c_uint64
i8 = ctypes.c_byte
i16 = ctypes.c_int16
i32 = ctypes.c_int32
i64 = ctypes.c_int64
f32 = ctypes.c_float
f64 = ctypes.c_double

BitList = List[int]
ByteList = List[int | u8]
PrimitiveInt = int | u8 | u16 | u32 | u64 | i8 | i16 | i32 | i64
PrimitiveFloat = float | f32 | f64
Primitive = PrimitiveInt | PrimitiveFloat | BitList | ByteList




# From
from_arr = ...
from_u8 = ...
from_int = ...
from_str = ...
from_struct = ...

# Into
into_i8_list = ...
into_i8_arr = ...

# TODO(pbz): Both C language codec functions and also Python

# ! Codecs can never start with `op_` since that would mean they are part of an
# ! algebra. This is fine, but they are not compatible with the Von Neumann API.




class Int:
    u8 = ctypes.c_uint8
    u16 = ctypes.c_uint16
    u32 = ctypes.c_uint32
    u64 = ctypes.c_uint64
    i8 = ctypes.c_int8
    i16 = ctypes.c_int16
    i32 = ctypes.c_int32
    i64 = ctypes.c_int64

    @classmethod
    def variants(cls):
        return [
            cls.u8,
            cls.u16,
            cls.u32,
            cls.u64,
            cls.i8,
            cls.i16,
            cls.i32,
            cls.i64,
        ]

    @classmethod
    def bit_list(cls, instance, bit_order, byte_order):
        "Returns the given instance as a list of bits"
        match type(instance):
            case cls.u8:
                pass
            case cls.u16:
                pass
            case cls.u32:
                pass
            case cls.u64:
                pass
            case cls.i8:
                pass
            case cls.i16:
                pass
            case cls.i32:
                pass
            case cls.i64:
                pass


# TODO(pbz): Codec operations

def get_identity_bytes(value: Primitive) -> bytes:
    """
    Returns the bytes of the primitive value with left to right bit and byte
    order regardless of the system endianness. Treats the input value as a raw
    memory region rather than a numeric value.
    """
    # The slice of memory that the primitive resides in
    byte_slice = ctypes.string_at(
        ctypes.byref(value),
        ctypes.sizeof(type(value))
    )

    # Little endian is reverse for numeric data but not for raw memory
    if sys.byteorder == 'big':
        byte_slice = bytearray(byte_slice)
        byte_slice.reverse()
        byte_slice = bytes(byte_slice)

    return byte_slice


def get_identity_bytes_numeric(value: Primitive) -> bytes:
    """
    Returns the bytes of the primitive value with left to right bit and byte
    order regardless of the system endianness. Treats the input value as a
    numeric value rather than a raw memory region.
    """
    # The slice of memory that the primitive resides in
    byte_slice = ctypes.string_at(
        ctypes.byref(value),
        ctypes.sizeof(type(value))
    )

    # Big endian is reverse for raw memory but not for numeric data
    if sys.byteorder == 'little':
        byte_slice = bytearray(byte_slice)
        byte_slice.reverse()
        byte_slice = bytes(byte_slice)

    return byte_slice



# Can control the types passed into it

# Bytes are always identity order
# List[byte] are always identity order, if not, **transform the Mem after**
# List[bit] are always identity order, if not, **transform the Mem after**
# List[u32] are always identity order, if not, **transform the Mem after**


# TODO(pbz): Negative Python big integers will always have an extra 1 bit.

# TODO(pbz): int.bit_length() works on any integer negative or positive.
# TODO(pbz): The idiomatic interface needs to use this.

(3).bit_length()

# TODO(pbz): Use float.hex() and struct.pack/unpack for dealing with bit parsing
import struct

float.hex

value = []
# isinstance(value, list[int])
# isinstance(value, [u8, u16, u32, u64, i8, i16, i32, i64, f32, f64])
# isinstance(value, tuple)


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

def op_from_u8_bit_arr(): ...
def op_from_u8_byte_arr(): ...


def repr_byte(mem: Mem): ...
def repr_byte_in_universe(mem: Mem, bit_order: Order, byte_order: Order): ...

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! It's time to determine if op_bitwise_or is necessary given the above
# ! fundamental operations like get and set bit. I'm also curious if op_execute
# ! is a fundamental operation because if it is, compile time code is possible.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

