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

The nomenclature in this file was meticulously chosen to reflect the boundary
between the logical universe of the program (host language) and the physical
universe of the computer. "Natural" in this context refers to what is natural to
the computer: bytes. "Numeric" in this context refers to the base of all data in
a program: numbers. It's literally not possible for there to be non-numeric data
in a program. All data is numeric, even if it is structured because the nested
data will always eventually come down to primitive numbers.

When transforming a numeric value into a memory region of a given size, there
are two ways to go about it. The value can be treated as numeric data or raw
memory. There are multitudinous applications of both such as logical data such
as strings or physical data such as the contents of one memory page. Being able
to effectively slice and transform each is useful and Tidbytes can do them all.
"""

import ctypes, sys, struct
from array import array
from typing import List, Generic, TypeVar
from .mem_types import *
from .von_neumann import *

T = TypeVar('T')
X64_MANTISSA = 53
X32_MANTISSA = 23
PYTHON_X64_FLOATS = sys.float_info.mant_dig == X64_MANTISSA

# TODO(pbz): From
from_arr = ...
from_u8 = ...
from_int = ...
from_str = ...
from_struct = ...
from_hex_string = ...

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

# value = []
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

def __from_natural_big_integer_bytes(
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



# TODO(pbz): Could probably parametrize this over enum of u8, u16 with len()

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














# !!!!!!!!!!!!!!!!! Mem[3](u8(2)) should truncate to 3 bits.

# TODO(pbz): Rework the rest of the codecs to take a bit length even if
# TODO(pbz): they don't use it. Strings need to truncate. Floats need to
# TODO(pbz): fail, etc.

# TODO(pbz): Rework the rest of the codecs to take a bit length even if
# TODO(pbz): they don't use it. Strings need to truncate. Floats need to
# TODO(pbz): fail, etc.

# TODO(pbz): Rework the rest of the codecs to take a bit length even if
# TODO(pbz): they don't use it. Strings need to truncate. Floats need to
# TODO(pbz): fail, etc.

# TODO(pbz): Rework the rest of the codecs to take a bit length even if
# TODO(pbz): they don't use it. Strings need to truncate. Floats need to
# TODO(pbz): fail, etc.

# TODO(pbz): Rework the rest of the codecs to take a bit length even if
# TODO(pbz): they don't use it. Strings need to truncate. Floats need to
# TODO(pbz): fail, etc.





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

def identity_bits_from_struct_field(specifier: str, value: int) -> list[int]:
    "Get the raw memory of an C type with bit & byte order left-to-right"
    little_endian_bytes = struct.pack(specifier, value)

    # At this point bytes are in correct numeric right-to-left order but the
    # bits are in left to right order. Whether or not they are numeric is
    # another story. Return the bits in identity order
    return [
        identity_bits_from_numeric_byte(byte)
        for byte in little_endian_bytes
    ]

# MemRgn from primitive idiomatic types

# TODO(pbz): Rename "bytes" to "logical" or "natural"?
def from_natural_u8(value: u8, bit_length: int) -> MemRgn:
    """
    This is different from `from_numeric_u8()` because it assumes that the
    provided u8 value is not numeric data but a slice of memory 1-byte long.
    This means bit order is left to right always.

    Providing a lower bit length lets fewer than 8 bits to be stored.

    For instance, 0b00010011 will be turned into: [11001000]. It appears
    backwards because it is treated as a memory region not a numeric value.
    """
    bit_length = 8 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<B', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_u16(value: u16, bit_length: int) -> MemRgn:
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
    bit_length = 16 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<H', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_u32(value: u32, bit_length: int) -> MemRgn:
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
    bit_length = 32 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<L', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_u64(value: u64, bit_length: int) -> MemRgn:
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
    bit_length = 64 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<Q', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_numeric_u8(value: u8, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_u8()` because it assumes the provided
    u8 value is numeric data with the least significant bit on the right.
    This means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.
    """
    bit_length = 8 if bit_length is None else bit_length
    return op_ensure_bit_length(
        op_reverse(from_natural_u8(value, bit_length)),
        bit_length
    )


def from_numeric_u16(value: u16, bit_length: int) -> MemRgn:
    """
    Numeric bit order is always right to left. Treat a u16 value as a memory
    region with padding bits on the left but the resulting region will have
    identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    For instance, 0b1_00010011 will be turned into: [00000001 00010011]. It
    appears the same as written because it is treated as a numeric value.
    """
    bit_length = 16 if bit_length is None else bit_length
    return op_ensure_bit_length(
        op_reverse(from_natural_u16(value, bit_length)),
        bit_length
    )


def from_numeric_u32(value: u32, bit_length: int) -> MemRgn:
    """
    Numeric bit order is always right to left. Treat a u32 value as a memory
    region with padding bits on the left but the resulting region will have
    identity bit and byte order (left to right for both).

    Host endianness is irrelevant as bits are read from right to left.

    For instance, 0b1_00010011 will be turned into:
    [00000000 00000000 00000001 00010011]. It appears the same as written
    because it is treated as a numeric value.
    """
    bit_length = 32 if bit_length is None else bit_length
    return op_ensure_bit_length(
        op_reverse(from_natural_u32(value, bit_length)),
        bit_length
    )


def from_numeric_u64(value: u64, bit_length: int) -> MemRgn:
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
    bit_length = 64 if bit_length is None else bit_length
    return op_ensure_bit_length(
        op_reverse(from_natural_u64(value, bit_length)),
        bit_length
    )


def from_natural_i8(value: i8, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i8()` because it assumes the provided i8
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded:

        -1 turns into [11111111]
        -2 turns into [11111110]
        -10 turns into [11110110]
    """
    bit_length = 8 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_i16(value: i16, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i16()` because it assumes the provided i16
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 16 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_i32(value: i32, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i32()` because it assumes the provided i32
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 32 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_natural_i64(value: i64, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i64()` because it assumes the provided i64
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 64 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_ensure_bit_length(op_identity(mem), bit_length)


def from_numeric_i8(value: i8, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i8()` because it assumes the provided i8
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded:

        -1 turns into [11111111]
        -2 turns into [11111110]
        -10 turns into [11110110]
    """
    bit_length = 8 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_ensure_bit_length(op_reverse(mem), bit_length)


def from_numeric_i16(value: i16, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i16()` because it assumes the provided i16
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 16 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_ensure_bit_length(op_reverse(mem), bit_length)


def from_numeric_i32(value: i32, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i32()` because it assumes the provided i32
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 32 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_ensure_bit_length(op_reverse(mem), bit_length)


def from_numeric_i64(value: i64, bit_length: int) -> MemRgn:
    """
    This is different from `from_byte_i64()` because it assumes the provided i64
    value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 64 if bit_length is None else bit_length
    mem = MemRgn()
    mem.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_ensure_bit_length(op_reverse(mem), bit_length)


def from_natural_f32(value: f32, bit_length: int) -> MemRgn:
    "Treats an f32 like a sequence of bytes"
    bit_length = 32 if bit_length is None else bit_length

    ensure(
        bit_length >= 32 if bit_length is not None else True,
        "Can't truncate floats meaningfully"
    )
    byte_slice = ctypes.string_at(
        ctypes.byref(value),
        ctypes.sizeof(type(value))
    )

    assert len(byte_slice) == 32 // 8, 'Not 32 bits long'

    mem = MemRgn()
    for byte in byte_slice:
        bits = []
        for i in range(8):
            bits.append(int(bool(byte & (1 << i))))
        mem.bytes.append(bits[:])
        bits.clear()

    # Only pad. Semantic error to truncate float.
    return op_ensure_bit_length(mem, bit_length)


def from_natural_f64(value: f64, bit_length: int) -> MemRgn:
    "Treats an f64 like a sequence of bytes"
    bit_length = 64 if bit_length is None else bit_length

    ensure(
        bit_length >= 64 if bit_length is not None else True,
        "Can't truncate floats meaningfully"
    )
    byte_slice = ctypes.string_at(
        ctypes.byref(value),
        ctypes.sizeof(type(value))
    )

    assert len(byte_slice) == 64 // 8, 'Not 64 bits long'

    mem = MemRgn()
    for byte in byte_slice:
        bits = []
        for i in range(8):
            bits.append(int(bool(byte & (1 << i))))
        mem.bytes.append(bits[:])
        bits.clear()

    return op_ensure_bit_length(mem, bit_length)


def from_numeric_f32(value: f32, bit_length: int) -> MemRgn:
    return op_reverse(from_natural_f32(value, bit_length))


def from_numeric_f64(value: f64, bit_length: int) -> MemRgn:
    return op_reverse(from_natural_f64(value, bit_length))


def from_natural_big_integer(value: int, bit_length: int) -> MemRgn:
    """
    Initializes a memory region from a big integer, assuming a bit length for
    negative numbers to allow for twos-complement encoding. Big integers that
    are positive are allowed to be larger than the provided bit length. Negative
    numbers must fit into the provided bit length because they are stored with
    their bits flipped which means all available bits are flipped. That wouldn't
    work if there wasn't a max storage size, resulting in infinite bits flipped.
    """
    ensure(
        bit_length is not None if value < 0 else True,
        'Must provide bit length for negative numbers due to '
        'twos-complement encoding'
    )

    # .bit_length() returns same value for positive as for negative so it can't
    # be used to tell how large the destination memory is for 2's complement
    bit_length = bit_length if bit_length is not None else value.bit_length()

    # TODO(pbz): Keep this around for the tests
    #   0000000000001010  10
    #   1111111111110101  flip all bits
    # + 0000000000000001  add 1
    #   ----------------
    #   1111111111110110  -10

    ensure(
        value.bit_length() <= bit_length,
        f'Big integers must fit in destination bit length: {bit_length}'
    )

    bits = [
        int(bool(value & 1 << bit_index))
        for bit_index in range(bit_length)
    ]

    mem = MemRgn()
    mem.bytes = group_bits_into_bytes(bits)

    # TODO(pbz): return contract_validate_memory(mem)
    return mem


def from_numeric_big_integer(value: int, bit_length: int) -> MemRgn:
    mem = from_natural_big_integer(value, bit_length)
    return op_reverse(mem)


def from_natural_float(value: float, bit_length: int) -> MemRgn:
    """
    Converts a float value to 32 or 64 identity bits depending on host CPU.
    Treats it as a numeric value rather than sequence of bytes.
    """
    # Possibly useful: https://evanw.github.io/float-toy/
    assert sys.float_info.mant_dig in (X64_MANTISSA, X32_MANTISSA)

    if PYTHON_X64_FLOATS:
        return from_natural_f64(f64(value), bit_length)
    else:
        return from_natural_f32(f32(value), bit_length)


def from_numeric_float(value: float, bit_length: int) -> MemRgn:
    """
    Converts a float value to 32 or 64 bits depending on host CPU while exactly
    matching in-memory representation. Not identity.
    """
    mem = from_natural_float(value, bit_length)
    return op_reverse(mem)


def from_bool(value: bool, bit_length: int) -> MemRgn:
    "Converts a boolean value to a single bit"
    bit_length = bit_length if bit_length is not None else 1
    mem = MemRgn()

    if bit_length == 0:
        return mem

    mem.bytes = [[1 if value else 0] + [None] * 7]
    return op_ensure_bit_length(mem, bit_length)


# TODO(pbz): Audit the code and remove iterators being consumed in ensure()
def from_bit_list(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from flat array of ints being either 0 or 1"
    # Preserve iterator by collecting into list for ensure()
    value = list(value)
    ensure(all(bit == 0 or bit == 1 for bit in value))

    bit_length = bit_length if bit_length is not None else 1
    mem = MemRgn()

    if bit_length == 0:
        return mem

    null = [None] * 8

    mem.bytes = [
        (value[i:i + 8] + null)[:8]
        for i in range(0, len(value), 8)
    ]

    return mem


def from_grouped_bits(value: list[list[int]], bit_length: int) -> MemRgn:
    "Memory region from list of list of 8 bits being either 0 or 1"
    # Preserve iterator by collecting into list for ensure()
    value = list(list(byte) for byte in value)

    ensure(all(len(byte) <= 8 for byte in value), 'Byte not long enough')
    ensure(
        all(all(bit == 0 or bit == 1 for bit in byte) for byte in value),
        'Malformed byte'
    )

    bit_length = bit_length if bit_length is not None else 1
    mem = MemRgn()

    if bit_length == 0:
        return mem

    null = [None] * 8
    mem.bytes = [(byte[:] + null)[:8] for byte in value]
    return mem


def from_bytes(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from list of unsigned integers in range 0x00 to 0xFF."
    ensure(all(0 <= byte <= 0xFF for byte in value))
    bit_length = bit_length if bit_length is not None else len(value) * 8
    bytes_ = [
        list(reversed(identity_bits_from_numeric_byte(byte)))
        for byte in value
    ]
    mem = MemRgn()
    mem.bytes = bytes_
    return op_ensure_bit_length(mem, bit_length)


def from_bytes_utf8(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from list of unsigned integers in range 0x00 to 0xFF."
    ensure(all(0 <= byte <= 0xFF for byte in value))
    bit_length = bit_length if bit_length is not None else len(value) * 8
    bytes_ = [
        list(reversed(identity_bits_from_numeric_byte(byte)))
        for byte in value
    ]
    mem = MemRgn()
    mem.bytes = bytes_
    a = op_ensure_bit_length(mem, bit_length)
    return a





def into_byte_u8(value) -> u8:
    pass


# TODO(pbz): Interface boundaries have configuration:
# twos_complement(bit_length)
# allow_negative
# Mem[bit_length]
#
# Mem[...](-123, twos_complement=True)  !! error: can't fit inside `...` unsized

# If bit_length was always a parameter, would this solve everything?
# Mem("asdf")  <- Is this ASCII or unicode? Does it matter?


# meta, intra, extra, pub, pri, extern, intern
