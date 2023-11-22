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

Design notes for this module:
- If the result of a Natural operation is directly returned, there's no need
    to validate the returned memory because all operations validate memory
    before returning.
- The "op" nomenclature always refers to algebraic operations with Natural
    inputs and Natural outputs (the Mem type). Think arithmetic: all ops take
    numbers and return numbers.


"""

import ctypes
import sys
import struct
from typing import TypeVar
from .mem_types import u8, u16, u32, u64, i8, i16, i32, i64, f32, f64, ensure
from .natural import (
    MemRgn, op_identity, op_reverse, contract_validate_memory,
    op_ensure_bit_length, group_bits_into_bytes, meta_op_bit_length,
    iterate_logical_bits
)

T = TypeVar('T')
X64_MANTISSA = 53
X32_MANTISSA = 23
PYTHON_X64_FLOATS = sys.float_info.mant_dig == X64_MANTISSA

# Prevents generators/iterators from being consumed without being processed
collect_iterator = list

# ! ----------------------------------------------------------------------------
# ! Codecs (From & Into)
# ! ----------------------------------------------------------------------------

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

# Deserialize MemRgn from primitive idiomatic types

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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<B', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<H', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<L', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<Q', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_ensure_bit_length(op_identity(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_ensure_bit_length(op_reverse(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_ensure_bit_length(op_reverse(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_ensure_bit_length(op_reverse(out), bit_length)


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
    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_ensure_bit_length(op_reverse(out), bit_length)


def from_natural_f32(value: f32, bit_length: int) -> MemRgn:
    "Treats an f32 like a sequence of bytes"
    if bit_length == 0:
        return MemRgn()

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

    out = MemRgn()
    for byte in byte_slice:
        bits = []
        for i in range(8):
            bits.append(int(bool(byte & (1 << i))))
        out.bytes.append(bits[:])
        bits.clear()

    # Only pad. Semantic error to truncate float.
    return op_ensure_bit_length(out, bit_length)


def from_natural_f64(value: f64, bit_length: int) -> MemRgn:
    "Treats an f64 like a sequence of bytes"
    if bit_length == 0:
        return MemRgn()

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

    out = MemRgn()
    for byte in byte_slice:
        bits = []
        for i in range(8):
            bits.append(int(bool(byte & (1 << i))))
        out.bytes.append(bits[:])
        bits.clear()

    return op_ensure_bit_length(out, bit_length)


def from_numeric_f32(value: f32, bit_length: int) -> MemRgn:
    return op_reverse(from_natural_f32(value, bit_length))


def from_numeric_f64(value: f64, bit_length: int) -> MemRgn:
    return op_reverse(from_natural_f64(value, bit_length))


def from_natural_big_integer(value: int, bit_length: int) -> MemRgn:
    """
    Initializes a memory region from a big integer, assuming a bit length for
    negative numbers to allow for twos-complement encoding. Since big integers
    are signed, `int.bit_length()` will return an unusable value because it
    won't be able to fit the number provided. For example, with a signed single
    bit number 1, this is not actually possible to store 1 because there's no
    room left for twos-complement encoding. If no bit length is given, an
    additional bit is used to store the twos-complement encoding. Treats the
    returned memory as identity bits and not numeric data.
    """
    if bit_length is None:
        # .bit_length() returns same value for positive as for negative so it can't
        # be used to tell how large the destination memory is for 2's complement
        bit_length = value.bit_length() + 1
    else:
        if bit_length == 0:
            return MemRgn()

        ensure(
            bit_length > 1,
            'Bit length of 1 is not enough for negative numbers using '
            'twos-complement encoding'
        )

    min_signed = -2 ** (bit_length - 1)
    max_signed = 2 ** (bit_length - 1) - 1

    ensure(
        min_signed <= value <= max_signed,
        f"Value {value} doesn't fit into signed range of bit length "
        f"{bit_length} from {min_signed} to {max_signed}"
    )

    bits = [
        int(bool(value & 1 << bit_index))
        for bit_index in range(bit_length)
    ]

    out = MemRgn()
    out.bytes = group_bits_into_bytes(bits)

    return contract_validate_memory(out)


def from_numeric_big_integer(value: int, bit_length: int) -> MemRgn:
    """
    Initializes a memory region from a big integer, assuming a bit length for
    negative numbers to allow for twos-complement encoding. Since big integers
    are signed, `int.bit_length()` will return an unusable value because it
    won't be able to fit the number provided. For example, with a signed single
    bit number 1, this is not actually possible to store 1 because there's no
    room left for twos-complement encoding. If no bit length is given, an
    additional bit is used to store the twos-complement encoding. Treats the
    returned memory as numeric data and not identity bits.
    """
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
    out = MemRgn()

    if bit_length == 0:
        return out

    out.bytes = [[1 if value else 0] + [None] * 7]
    return op_ensure_bit_length(out, bit_length)


def from_bit_list(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from flat array of ints being either 0 or 1"
    # Preserve iterator by collecting into list for ensure()
    value = collect_iterator(value)
    ensure(all(bit == 0 or bit == 1 for bit in value))

    bit_length = bit_length if bit_length is not None else 1
    out = MemRgn()

    if bit_length == 0:
        return out

    null = [None] * 8

    out.bytes = [
        (value[i:i + 8] + null)[:8]
        for i in range(0, len(value), 8)
    ]

    return contract_validate_memory(out)


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
    out = MemRgn()

    if bit_length == 0:
        return out

    null = [None] * 8
    out.bytes = [(byte[:] + null)[:8] for byte in value]

    return contract_validate_memory(out)


def from_bytes(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from list of unsigned integers in range 0x00 to 0xFF."
    ensure(all(0 <= byte <= 0xFF for byte in value))
    bit_length = bit_length if bit_length is not None else len(value) * 8
    bytes_ = [
        list(reversed(identity_bits_from_numeric_byte(byte)))
        for byte in value
    ]
    out = MemRgn()
    out.bytes = bytes_

    return op_ensure_bit_length(out, bit_length)


def from_bytes_utf8(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from list of unsigned integers in range 0x00 to 0xFF."
    ensure(all(0 <= byte <= 0xFF for byte in value))
    bit_length = bit_length if bit_length is not None else len(value) * 8
    bytes_ = [
        list(reversed(identity_bits_from_numeric_byte(byte)))
        for byte in value
    ]
    out = MemRgn()
    out.bytes = bytes_

    return op_ensure_bit_length(out, bit_length)

# TODO(pbz): Implement serialization
# Serialize MemRgn from primitive idiomatic types

def into_numeric_big_integer(mem: MemRgn) -> int:
    "Treats the memory region as a signed big integer."
    if not mem.bytes:
        return 0

    bits = ''.join(
        ''.join(
            str(bit) if bit is not None else ''  # ? '▫'
            for bit in byte
        )
        for byte in mem.bytes
    )

    if bits[0] == '1':  # Negative
        raw_integer_value = int(bits, base=2)
        ones_complement = bin(raw_integer_value - 1).lstrip('0b')

        # Preserve bit length for invert
        if len(ones_complement) < meta_op_bit_length(mem):
            ones_complement = '0' + ones_complement

        inverted_bits = ''.join('10'[int(i)] for i in ones_complement)
        return -int(inverted_bits, base=2)

    else:
        return int(bits, base=2)


def into_natural_big_integer(mem: MemRgn) -> int:
    out = 0
    for i, bit in enumerate(reversed(list(iterate_logical_bits(mem.bytes)))):
        if bit:
            out |= 1 << i
    return out




def into_u8_bit_arr(): ...
def into_u8_byte_arr(): ...
def into_u32_arr(): ...
def into_u8(): ...
def into_u16(): ...
def into_u32(): ...
def into_u64(): ...

def into_i8_arr(): ...
def into_i32_arr(): ...
def into_i8(): ...
def into_i16(): ...
def into_i32(): ...
def into_i64(): ...
def into_i8_list(): ...
def into_i8_arr_(): ...
def into_int(): ...  # Examine host endianness, use struct.unpack
def into_byte_u8(value) -> u8: ...
