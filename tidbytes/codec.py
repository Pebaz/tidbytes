"""

The job of a codec is to efficiently bring idiomatic types into the algebraic
system of MemRgn. They are exactly analogous to Rust's From & Into traits.

All integers coming from Python will be logical values. They assume numeric data
and so bit order is right to left. To successfully treat a number as a memory
region, they need to be transformed to identity order (bit & byte order being
left to right). Semantically, this is the same because numbers go from right to
left logically since the least significant bit is on the right. The reason any
of this is important is the answer to the question: "what is the second bit?".
For numbers this is the rightmost bit less one. For raw memory, this is the
leftmost bit plus one.

Identity bytes operations always assume the input number is raw memory and not
numeric data. Transformation operations can be performed after initialization if
numeric logic is relevant.
"""

import ctypes, sys, struct
from array import array
from typing import List, Generic, TypeVar
from .mem_types import *
from .von_neumann import *

T = TypeVar('T')























# From
from_arr = ...
from_u8 = ...
from_int = ...
from_str = ...
from_struct = ...


# TODO(pbz): Both C language codec functions and also Python

# ! Codecs can never start with `op_` since that would mean they are part of an
# ! algebra. This is fine, but they are not compatible with the Von Neumann API.




# TODO(pbz): 7/28/23 -> Current:
# TODO(pbz): Need from_float, from_int, from_bool, from_etc because those are
# TODO(pbz): the actual idiomatic types. All the other ones are from C. In the
# TODO(pbz): `Mem` constructor, just match the type and call the correct
# TODO(pbz): initializer.

# TODO(pbz): What would make this project complete?
# TODO(pbz): A Mem type that can support indexing and all other operations.
# TODO(pbz): A Struct type that could support nested types, offset, and
# TODO(pbz): alignment.


def get_identity_bytes_float(value: float) -> bytearray:
    return bytearray(struct.unpack('d', value))


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


# def repr_byte(mem: Mem): ...
# def repr_byte_in_universe(mem: Mem, bit_order: Order, byte_order: Order): ...

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! It's time to determine if op_bitwise_or is necessary given the above
# ! fundamental operations like get and set bit. I'm also curious if op_execute
# ! is a fundamental operation because if it is, compile time code is possible.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!







# TODO(pbz): 7/28/23
# TODO(pbz): These definitions are good just convert them to codecs

def from_bytes(cls, value):
    """
    Treats a memory region as if it had identity bit and byte order (left
    to right for both). To transform into another memory universe, use the
    transformation operations:
        - identity()
        - reverse()
        - reverse_bytes()
        - reverse_bits()
    """
    mem = Mem()
    for byte in value:
        mem_byte = cls.from_numeric_u8(byte)
        mem = mem + mem_byte if mem else mem_byte
    return mem

def __from_big_integer_bytes(
    value: int,
    bit_length: int
) -> list[list[int]]:
    """
    Helper function to convert a Python big integer to a list of lists of
    bits.
    """
    # TODO(pbz): This is a bug!
    assert False, 'THIS IS A BUG. THIS SHOULD RETURN BYTES NOT BITS!'

    bytes = []
    byte = []

    for i in range(bit_length):
        bit = int(bool(value & (1 << i)))
        byte.append(bit)

        if len(byte) == 8:
            bytes.append(byte[:])
            byte.clear()

    if byte:
        bytes.append((byte + [None] * 8)[:8])

    return bytes

def from_numeric_u8(cls, value, bit_length=8):
    """
    This is different from `from_byte_u8()` because it assumes the provided
    u8 value is numeric data with the least significant bit on the right.
    This means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.
    """
    ensure(bit_length <= 8, 'Only 8 bits in a u8')
    ensure(value >= 0, 'Positive values only')

    mem = cls.from_byte_u8(value, bit_length)
    mem.rgn = op_reverse(mem.rgn)

    return mem.validate()

# TODO(pbz): Could probably parametrize this over enum of u8, u16 with len()
def from_bytes_u16(cls, value, bit_length=16):
    """
    Non-numeric bit order is always left to right. Treat a u16 value as a
    memory region with padding bits on the right and the resulting region
    will have identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    The bits of the number will be exactly reversed from how they are
    written.

    Treat the bytes of a number as a memory region, not a numeric value.

    For instance, 0b1_00010011 will be turned into: [11001000 10000000]. It
    appears backwards because it is treated as a memory region not a numeric
    value.
    """
    ensure(bit_length <= 16, 'Only 16 bits in a u16')
    ensure(value >= 0, 'Positive values only')

    mem = cls()
    mem.rgn.bytes = cls.__from_big_integer_bytes(value, bit_length)

    return mem.validate()

def from_numeric_u16(cls, value, bit_length=16):
    """
    Numeric bit order is always right to left. Treat a u16 value as a memory
    region with padding bits on the left but the resulting region will have
    identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    For instance, 0b1_00010011 will be turned into: [00000001 00010011]. It
    appears the same as written because it is treated as a numeric value.
    """
    ensure(bit_length <= 16, 'Only 16 bits in a u16')
    ensure(value >= 0, 'Positive values only')

    mem = cls.from_bytes_u16(value, bit_length)
    mem.rgn = op_reverse(mem.rgn)

    return mem.validate()

def from_bytes_u32(cls, value, bit_length=32):
    """
    Non-numeric bit order is always left to right. Treat a u32 value as a
    memory region with padding bits on the right and the resulting region
    will have identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    The bits of the number will be exactly reversed from how they are
    written.

    Treat the bytes of a number as a memory region, not a numeric value.

    For instance, 0b1_00010011 will be turned into:
    [11001000 10000000 00000000 00000000]. It appears backwards because it
    is treated as a memory region not a numeric value.
    """
    ensure(bit_length <= 32, 'Only 32 bits in a u32')
    ensure(value >= 0, 'Positive values only')

    mem = cls()
    mem.rgn.bytes = cls.__from_big_integer_bytes(value, bit_length)

    return mem.validate()

def from_numeric_u32(cls, value, bit_length=32):
    """
    Numeric bit order is always right to left. Treat a u32 value as a memory
    region with padding bits on the left but the resulting region will have
    identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    For instance, 0b1_00010011 will be turned into:
    [00000000 00000000 00000001 00010011]. It appears the same as written
    because it is treated as a numeric value.
    """
    ensure(bit_length <= 32, 'Only 32 bits in a u32')
    ensure(value >= 0, 'Positive values only')

    mem = cls.from_bytes_u32(value, bit_length)
    mem.rgn = op_reverse(mem.rgn)

    return mem.validate()

def from_bytes_u64(cls, value, bit_length=64):
    """
    Non-numeric bit order is always left to right. Treat a u64 value as a
    memory region with padding bits on the right and the resulting region
    will have identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    The bits of the number will be exactly reversed from how they are
    written.

    Treat the bytes of a number as a memory region, not a numeric value.

    For instance, 0b1_00010011 will be turned into:

        11001000 10000000 00000000 00000000
        00000000 00000000 00000000 00000000

    It appears backwards because it is treated as a memory region not a
    numeric value.
    """
    ensure(bit_length <= 64, 'Only 64 bits in a u64')
    ensure(value >= 0, 'Positive values only')

    mem = cls()
    mem.rgn.bytes = cls.__from_big_integer_bytes(value, bit_length)

    return mem.validate()

def from_numeric_u64(cls, value, bit_length=64):
    """
    Numeric bit order is always right to left. Treat a u64 value as a memory
    region with padding bits on the left but the resulting region will have
    identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    For instance, 0b1_00010011 will be turned into:

        00000000 00000000 00000000 00000000
        00000000 00000000 00000001 00010011

    It appears the same as written because it is treated as a numeric value.
    """
    ensure(bit_length <= 64, 'Only 64 bits in a u64')
    ensure(value >= 0, 'Positive values only')

    mem = cls.from_bytes_u64(value, bit_length)
    mem.rgn = op_reverse(mem.rgn)

    return mem.validate()


# TODO(pbz): 7/28/23
# TODO(pbz): These are not codecs because "bit/byte length" is not a type?
@classmethod
def from_bit_length(cls, bit_length: int):
    mem = cls()

    bytes = []
    byte = []

    for i in range(bit_length):
        byte.append(0)
        if len(byte) == 8:
            bytes.append(byte[:])
            byte.clear()

    if byte:
        bytes.append(byte)

    mem.rgn.bytes = bytes
    return mem


# TODO(pbz): 7/28/23
# TODO(pbz): There should be `Into` codecs as well


# Into
into_i8_list = ...
into_i8_arr = ...

into_int = ...  # TODO(pbz): Examine host endianness, use struct.unpack




def memory(init):
    if hasattr(init, '__mem__'):
        return init.__mem__()

    elif isinstance(init, int):
        return from_numeric_u64(u64(init))






# ! ----------------------------------------------------------------------------
# ! Codecs (From & Into)
# ! ----------------------------------------------------------------------------

# def reverse_byte(byte: int) -> int:
#     "Reverses the bits of an 8-bit unsigned integer"
#     ensure(0 <= byte <= 255, 'Only values from 0-255 inclusive supported')

#     new_byte = 0
#     for bit_index in range(8):  # Iterate from right to left
#         bit = bool(byte & (1 << bit_index))
#         if bit:  # Set the opposite bit from left to right
#             new_byte |= 1 << (8 - bit_index - 1)
#     return new_byte


# TODO(pbz): Is this a good idea?
'''
def identity_bytes(value: Primitive, struct_descriptor: str) -> list[int]:
    little_endian_bytes = struct.pack(struct_descriptor, value.value)

    # At this point bytes are in correct numeric right-to-left order but the
    # bits are in left to right order. Whether or not they are numeric is
    # another story. Return the bits in identity order
    return [reverse_byte(byte) for byte in little_endian_bytes]
'''


# Identity bits & bytes

def identity_bits_from_numeric_byte(byte: int) -> list[int]:
    "Returns all bits of a byte holding numeric data going from right to left"
    ensure(0 <= byte <= 255, 'Not a byte')
    return [
        int(bool(byte & 1 << bit_index))
        for bit_index in range(8)
    ]


def identity_bytes_u8(value: u8) -> list[int]:
    "Get the raw memory of a u8 in bit & byte order left-to-right"
    little_endian_u8 = '<B'
    little_endian_bytes = struct.pack(little_endian_u8, value.value)

    # At this point bytes are in correct numeric right-to-left order but the
    # bits are in left to right order. Whether or not they are numeric is
    # another story. Return the bits in identity order
    return [
        identity_bits_from_numeric_byte(byte)
        for byte in little_endian_bytes
    ]


def identity_bytes_u16(value: u16) -> list[int]:
    "Get the raw memory of a u16 in bit & byte order left-to-right"
    little_endian_u16 = '<H'
    little_endian_bytes = struct.pack(little_endian_u16, value.value)
    return [
        identity_bits_from_numeric_byte(byte)
        for byte in little_endian_bytes
    ]


# MemRgn from primitive idiomatic types

# TODO(pbz): Rename "bytes" to "logical" or "natural"?

def from_byte_u8(value: u8) -> MemRgn:
    """
    This is different from `from_numeric_u8()` because it assumes that the provided
    u8 value is not numeric data but a slice of memory 1-byte long. This
    means bit order is left to right always.

    Providing a lower bit length lets fewer than 8 bits to be stored.

    For instance, 0b00010011 will be turned into: [11001000]. It appears
    backwards because it is treated as a memory region not a numeric value.
    """
    mem = MemRgn()
    mem.bytes = identity_bytes_u8(value)
    return op_identity(mem)


def from_bytes_u16(value: u16) -> MemRgn:
    mem = MemRgn()
    mem.bytes = identity_bytes_u16(value)
    return op_identity(mem)


def from_numeric_u8(value: u8) -> MemRgn:
    mem = MemRgn()
    mem.bytes = identity_bytes_u8(value)
    return op_reverse(mem)


def from_numeric_u16(value: u16) -> MemRgn:
    mem = MemRgn()
    mem.bytes = identity_bytes_u16(value)
    return op_reverse(mem)





def from_big_integer(value, bit_length=8) -> MemRgn:

    ensure(bit_length <= 8, 'Only 8 bits in a u8')
    ensure(value >= 0, 'Positive values only')

    mem = MemRgn()
    mem.rgn.bytes = __from_big_integer_bytes(value, bit_length)

    return mem.validate()


def from_numeric_big_integer(value, bit_length=8) -> MemRgn:

    ensure(bit_length <= 8, 'Only 8 bits in a u8')
    ensure(value >= 0, 'Positive values only')

    mem = MemRgn()
    mem.rgn.bytes = __from_big_integer_bytes(value, bit_length)

    return mem.validate()


def into_byte_u8(value) -> u8:
    pass


