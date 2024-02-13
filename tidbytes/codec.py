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

def range_unsigned(bit_length: int) -> (int, int):
    "u8 range is 0 ..= 255"
    return 0, 2 ** bit_length - 1


def range_signed(bit_length: int) -> (int, int):
    "i8 range is -128 ..= 127"
    if bit_length == 0:
        return 0, 0
    return -2 ** (bit_length - 1), 2 ** (bit_length - 1) - 1


def is_in_range_unsigned(value: int, bit_length: int) -> bool:
    "u8 range is 0 ..= 255"
    lo, hi = range_unsigned(bit_length)
    return lo <= value <= hi


def is_in_range_signed(value: int, bit_length: int) -> bool:
    "i8 range is -128 ..= 127"
    lo, hi = range_signed(bit_length)
    return lo <= value <= hi


def check_range_unsigned(val, bit_length: int) -> None:
    lo, hi = range_unsigned(bit_length)
    ensure(
        lo <= val <= hi,
        f"Value {val} doesn't fit into range of bit length {bit_length} from "
        f"{lo} to {hi}"
    )


def check_range_signed(val, bit_length: int) -> None:
    lo, hi = range_signed(bit_length)
    ensure(
        lo <= val <= hi,
        f"Value {val} doesn't fit into range of bit length {bit_length} from "
        f"{lo} to {hi}"
    )


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

    check_range_unsigned(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<B', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


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

    check_range_unsigned(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<H', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


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

    check_range_unsigned(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<L', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


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

    check_range_unsigned(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<Q', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


def from_numeric_u8(value: u8, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_u8()` because it assumes the provided
    u8 value is numeric data with the least significant bit on the right.
    This means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.
    """
    bit_length = 8 if bit_length is None else bit_length

    check_range_unsigned(value.value, bit_length)

    return op_reverse(
        op_ensure_bit_length(from_natural_u8(value, bit_length), bit_length)
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

    check_range_unsigned(value.value, bit_length)

    return op_reverse(
        op_ensure_bit_length(from_natural_u16(value, bit_length), bit_length)
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

    check_range_unsigned(value.value, bit_length)

    return op_reverse(
        op_ensure_bit_length(from_natural_u32(value, bit_length), bit_length)
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

    check_range_unsigned(value.value, bit_length)

    return op_reverse(
        op_ensure_bit_length(from_natural_u64(value, bit_length), bit_length)
    )


def from_natural_i8(value: i8, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i8()` because it assumes the provided
    i8 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded:

        -1 turns into [11111111]
        -2 turns into [11111110]
        -10 turns into [11110110]
    """
    bit_length = 8 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


def from_natural_i16(value: i16, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i16()` because it assumes the provided
    i16 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 16 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


def from_natural_i32(value: i32, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i32()` because it assumes the provided
    i32 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 32 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


def from_natural_i64(value: i64, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i64()` because it assumes the provided
    i64 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 64 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_identity(op_ensure_bit_length(out, bit_length))


def from_numeric_i8(value: i8, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i8()` because it assumes the provided
    i8 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded:

        -1 turns into [11111111]
        -2 turns into [11111110]
        -10 turns into [11110110]
    """
    bit_length = 8 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<b', value.value)
    return op_reverse(op_ensure_bit_length(out, bit_length))


def from_numeric_i16(value: i16, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i16()` because it assumes the provided
    i16 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 16 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<h', value.value)
    return op_reverse(op_ensure_bit_length(out, bit_length))


def from_numeric_i32(value: i32, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i32()` because it assumes the provided
    i32 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 32 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<l', value.value)
    return op_reverse(op_ensure_bit_length(out, bit_length))


def from_numeric_i64(value: i64, bit_length: int) -> MemRgn:
    """
    This is different from `from_natural_i64()` because it assumes the provided
    i64 value is numeric data with the least significant bit on the right. This
    means bit order is from right to left always.

    For instance, 0b00010011 will be turned into: [00010011]. It appears
    the same as written because it is treated as a numeric value.

    Negative numbers are twos-complement encoded.
    """
    bit_length = 64 if bit_length is None else bit_length

    check_range_signed(value.value, bit_length)

    out = MemRgn()
    out.bytes = identity_bits_from_struct_field('<q', value.value)
    return op_reverse(op_ensure_bit_length(out, bit_length))


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


def from_natural_big_integer_signed(value: int, bit_length: int) -> MemRgn:
    """
    - Two's-complement encoded for negative values
    - When no bit length given, adds an extra bit for signedness
    - Uses optional bit length to determine integer range and validate input
    - Has half the range of `from_natural_big_integer_unsigned`
    - Treats the returned memory as identity bits and not numeric data
    """
    if bit_length is None:
        twos_complement_space = 1
        bit_length = value.bit_length() + twos_complement_space

    check_range_signed(value, bit_length)

    bits = [
        int(bool(value & 1 << bit_index))
        for bit_index in range(bit_length)
    ]

    out = MemRgn()
    out.bytes = group_bits_into_bytes(bits or [0])  # Value may have been zero

    return contract_validate_memory(out)

def from_natural_big_integer_unsigned(value: int, bit_length: int) -> MemRgn:
    """
    - Uses optional bit length to determine integer range and validate input
    - When no bit length given, stores exactly enough bits to hold the number
    - Treats the returned memory as identity bits and not numeric data.
    """
    ensure(value >= 0, 'Implicit conversion from signed to unsigned')

    if bit_length is None:
        bit_length = value.bit_length()

    check_range_unsigned(value, bit_length)

    bits = [
        int(bool(value & 1 << bit_index))
        for bit_index in range(bit_length)
    ]

    out = MemRgn()
    out.bytes = group_bits_into_bytes(bits or [0])  # Value may have been zero

    return contract_validate_memory(out)


def from_numeric_big_integer_signed(value: int, bit_length: int) -> MemRgn:
    """
    - Two's-complement encoded for negative values
    - When no bit length given, adds an extra bit for signedness
    - Uses optional bit length to determine integer range and validate input
    - Has half the range of `from_numeric_big_integer_unsigned`
    """
    return op_reverse(from_natural_big_integer_signed(value, bit_length))


def from_numeric_big_integer_unsigned(value: int, bit_length: int) -> MemRgn:
    """
    - Uses optional bit length to determine integer range and validate input
    - Takes the absolute value of negative values and stores them unsigned
    - When no bit length given, stores exactly enough bits to hold the number
    """
    return op_reverse(from_natural_big_integer_unsigned(value, bit_length))


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
    ensure(bit_length > 0, 'Cannot store bool in zero-sized memory region')
    out.bytes = [[1 if value else 0] + [None] * 7]
    return op_ensure_bit_length(out, bit_length)


def from_bit_list(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from flat array of ints being either 0 or 1"
    ensure(
        bit_length != 0 if bool(value) else True,
        f'Loss of data via truncation: {bit_length=}'
    )
    print(f'{bit_length != 0 if bool(value) else True}, {bit_length=}')

    # Preserve iterator by collecting into list for ensure()
    value = collect_iterator(value)
    ensure(all(bit == 0 or bit == 1 for bit in value))

    bit_length = bit_length if bit_length is not None else len(value)
    out = MemRgn()

    ensure(
        0 <= len(value) <= bit_length,
        f'Region of size {bit_length} not big enough to store {len(value)} bits'
    )

    null = [None] * 8

    out.bytes = [
        (value[i:i + 8] + null)[:8]
        for i in range(0, len(value), 8)
    ]

    out = op_ensure_bit_length(out, bit_length)

    return contract_validate_memory(out)


def from_grouped_bits(value: list[list[int]], bit_length: int) -> MemRgn:
    "Memory region from list of list of 8 bits being either 0 or 1"
    # Preserve iterator by collecting into list for ensure()
    value = list(list(byte) for byte in value)

    ensure(all(len(byte) <= 8 for byte in value), 'Malformed byte')
    ensure(
        all(all(bit == 0 or bit == 1 for bit in byte) for byte in value),
        'Malformed byte'
    )

    value_len = sum(len(b) for b in value)
    bit_length = bit_length if bit_length is not None else value_len
    out = MemRgn()

    ensure(
        0 <= value_len <= bit_length,
        f'Region of size {bit_length} not big enough to store {value_len} bits'
    )

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


def into_numeric_big_integer(mem: MemRgn) -> int:
    "Treats the memory region as a signed big integer."
    if not mem.bytes:
        return 0

    bits = ''.join(str(i) for i in iterate_logical_bits(mem.bytes))

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
    "Always assumes destination is signed since Python's big integer type is."
    out = 0
    for i, bit in enumerate(reversed(list(iterate_logical_bits(mem.bytes)))):
        if bit:
            out |= 1 << i
    return out
