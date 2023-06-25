import sys
from typing import Any
from .mem_types import *
from .von_neumann import *

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

class Mem:
    def __init__(self):
        self.rgn = MemRgn()

    def __setitem__(self, key, value):
        payload = MemRgn()
        payload.bytes = [[value] + [None] * 7]
        op_set_bit(self.rgn, key, payload)

    def __str__(self):  # Display
        """
        Displays all bits up to bit length 64, then displays bit length.
        """
        return ' '.join(
            ''.join(
                str(bit) if bit != None else ''  # ? '▫'
                for bit in byte
            )
            for byte in self.rgn.bytes
        )

    def __repr__(self):  # Debug
        bits = str(self)

        # More than 8 bytes is getting long
        if bits.count(' ') > 7:
            bits = f'{len(self)} bits'

            # TODO(pbz): Use __int__(self)
            # hex_bits = hex(int(''.join(bits.split()), base=2))[2:]

            # length_of_8_bytes = 71
            # if len(hex_bits) > length_of_8_bytes:
            #     pass
            # else:
            #     pass

        return f'<Mem [{bits}]>'

    def __format__(self, specifier: str) -> str:
        match specifier:
            case 'bits':
                return str(self)
            case 'hex' | 'x':
                return hex(int(''.join(str(self).split()), base=2))[2:]
            case 'X':
                return format(self, 'x').upper()
            case _:
                return str(self)

    def __len__(self):
        return op_bit_length(self.rgn)

    def __bool__(self):
        "False if Mem is null else True"
        return bool(self.rgn.bytes)

    def __add__(self, other):
        mem = Mem()
        mem.rgn = op_concatenate(self.rgn, other.rgn)
        return mem.validate()

    def __getitem__(self, index: slice) -> Any:
        print('here')

    def validate(self):
        validate_memory(self.rgn)
        return self

    @classmethod
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

    @staticmethod
    def __from_big_integer_bytes(
        value: int,
        bit_length: int
    ) -> list[list[int]]:
        """
        Helper function to convert a Python big integer to a list of lists of
        bits.
        """
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

    @classmethod
    def from_byte_u8(cls, value, bit_length=8):
        """
        This is different from `from_numeric_u8()` because it assumes that the provided
        u8 value is not numeric data but a slice of memory 1-byte long. This
        means bit order is left to right always.

        Providing a lower bit length lets fewer than 8 bits to be stored.

        For instance, 0b00010011 will be turned into: [11001000]. It appears
        backwards because it is treated as a memory region not a numeric value.
        """
        ensure(bit_length <= 8, 'Only 8 bits in a u8')
        ensure(value >= 0, 'Positive values only')

        mem = cls()
        mem.rgn.bytes = cls.__from_big_integer_bytes(value, bit_length)

        return mem.validate()

    @classmethod
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
    @classmethod
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

    @classmethod
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

    @classmethod
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

    @classmethod
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

    @classmethod
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

    @classmethod
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


# TODO(pbz): Codec operations

import ctypes

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


# TODO(pbz): int.bit_length() works on any integer negative or positive.
# TODO(pbz): The idiomatic interface needs to use this.

(3).bit_length()

# TODO(pbz): Use float.hex() and struct.pack/unpack for dealing with bit parsing
import struct

float.hex

value = []
isinstance(value, list[int])
isinstance(value, [u8, u16, u32, u64, i8, i16, i32, i64, f32, f64])
isinstance(value, tuple)


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


def repr_byte(mem: MemRgn): ...
def repr_byte_in_universe(mem: MemRgn, bit_order: Order, byte_order: Order): ...

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! It's time to determine if op_bitwise_or is necessary given the above
# ! fundamental operations like get and set bit. I'm also curious if op_execute
# ! is a fundamental operation because if it is, compile time code is possible.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
