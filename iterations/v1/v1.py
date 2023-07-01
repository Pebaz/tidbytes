"""
Great bytes libraries for Python:

- Operations: https://pypi.org/project/bytesfunc/
- Theory: https://pypi.org/project/bytesize/
- Display Units & Theory: https://pypi.org/project/justbytes/

Desired Features:1
- mem.py (mem_py Pypi, pronounced "mem dot pie")
- Describe exact bit layout for a data type
- Type layout with default values
- Types with templates that can be filled in later (default values?)
- Set slice of bits to integer
- Set slice of bits to memory value
- Set slice of bits to string
- Set slice of bits to `bytes` built-in type
- Slice bits into own mem type
- Convert bits to `bytes` built-in type
- Convert bits to integer built-in type (negatives!)
- Proper display (repr for bits, str for hex or vice versa)
- Sizeof & alignof
- Bit length of memory (bit_length)
- Byte length of memory (byte_length)
- Mem type from integer, lowest possible bytes
- Mem type from byte length and integer value
- Mem type from byte length and Mem type
- Mem type from byte length and list of bytes
- Mem type from byte length and list of integers
- Bit-level Cursor API for parsing data structures
- Cursor API bit-level read ahead and skip for reading small integers like u3
- File-like bit-level write API for assembling (write(bits=4, value=3))
- Clear expectations on left-to-right memory and right-to-left bytes
- Clear expectations on integer endianness
- Equality of same-sized bit regions
- Equality of same-sized byte regions
- Equality of bits to bits of possibly different lengths if zero
- Implement ops like XOR and stuff from the operations link above
- Match bit patterns like masks and interleaved bits

I need:
    Bit indexing since structs can have bit-fields
    Bit indexing order since numbers are right-to-left ordered!
    Byte indexing since bytes are the smallest addressable unit of memory
    Byte index order since numbers are stored in little or big endian order

    Basically I need both L2R and R2L for both bits and bytes.
    "Set the first bit" is ambiguous without more info.

@classmethod
def from_ile(cls, ile):
    "From little-endian integer, signedness ignored, treated as bit region."

--------------------------------------------------------------------------------

New Thoughts:

When packed, a 3 bit field can be stuffed into the leftmost bits of a byte since
that would be the first bits of a file for example. However, once the codec
decodes that field, it will load that bit slice into any desired bit length that
makes sense for that type. For integers, a 3 bit int would become an 8 bit char
with the rightmost 3 bits being the 3 bits from the file. This makes sense for
signed, two's complement encoded numeric values, but this might not make sense
in all cases. For instance, perhaps the leftmost 3 bits should be set for a type
or perhaps the leftmost bit of 3 consecutive bytes should be equal to the 3 bits
of the front of the file. When talking about bit fields or parsing files, bits
have a different meaning until the packed bits are decoded into memory.

So basically it's a problem of packed vs in-memory representation. Codecs come
to mind here. I think there's an opportunity to couple these concepts into the
API surface of this memory library.

! If a value is encoded in a file, the bits are left-aligned with padding on the
! right. If a value is decoded into memory, the bits are right-aligned with
! padding on the left.

vv  These are not bit-fields. They are the packed representation of a struct  vv

class addi32le:
    sign: BoolCodec = 1
    exponent: TwosComplementNumericCodec = 12
    mantissa: UnsignedNumericCodec = 123

             |
             |
             |
             V
"""

class Codec:
    """
    A codec works with a number of bytes that is greater than or equal to the
    number of bits in a bit slice. It then parses out relevant information into
    the desired in-memory type.
    """
    def decode(self, bytes_: ...) -> ...:
        ...
    def encode(self) -> ...:
        ...

class IntCodec(Codec):
    ...: ...

import math
import ctypes
# Pushes Python requirement to 3.11, not available in 3.9
# from typing import Self
from typing import Union
from enum import Enum, auto
from dataclasses import dataclass


def bytes_needed(bit_length: int) -> int:
    return math.ceil(bit_length / 8)

# TODO(pbz): Would natural indexing be useful? Natural, Constant, Bit offset?
class Indexing(Enum):
    RBY = auto()
    LBY = auto()
    RBT = auto()
    LBT = auto()

class Order(Enum):
    LeftToRight = auto()  # Big endian if bytes, byte-index if bits
    RightToLeft = auto()  # Little endian if bytes, bit-index if bits

# TODO(pbz): Use enum.Flag here? It would allow ORing them like LBT = BIT | L2R
class Granularity(Enum):
    Bits = auto()
    Bytes = auto()

@dataclass
class Index:
    base: int
    offset: int
    order: Order = Order.LeftToRight
    granularity: Granularity = Granularity.Bits

@dataclass
class NaturalIndex:
    natural_units: int
    constant_bytes: int
    constant_bits: int = 0

class Int(Enum):
    u8 = ctypes.c_uint8
    u16 = ctypes.c_uint16
    u32 = ctypes.c_uint32
    u64 = ctypes.c_uint64
    i8 = ctypes.c_int8
    i16 = ctypes.c_int16
    i32 = ctypes.c_int32
    i64 = ctypes.c_int64
    # bigint = int  # TODO(pbz): Support big ints from Python?

class Mem:
    def __init__(self):
        self.bits: list[int] = []

    def __bytes__(self) -> bytes:
        "Always handled from left to right."
        return self.to_bytes(Order.LeftToRight)

    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    [0xFF, 0xFA]  # Byte integers
    [0xFFFFFF, 0xFFFFFF]  # Bigger integers
    # Only work with ctypes?

    def extend(self, bits: int = 0, bytes_: int = 0) -> None:
        self.bits += [0] * bits + [0] * 8 * bytes_

    def to_bytes(self, bit_order: Order = Order.RightToLeft, byte_order: Order = Order.LeftToRight) -> bytes:
        bits = self.bits

        if len(bits) % 8 != 0:
            padding = [0] * (8 - len(self.bits) % 8)

            if byte_order == Order.LeftToRight:
                bits = self.bits + padding
            else:
                bits = padding + self.bits

        iter_order = iter if byte_order == Order.LeftToRight else reversed
        result = b''

        for byte_index in iter_order(range(0, len(bits), 8)):
            byte_slice = bits[byte_index:byte_index + 8]
            byte = 0

            # TODO(pbz): I don't think this is right. Check it, test it.
            for bit_index in range(8):
                if byte_slice[bit_index] == 1:
                    byte |= 1 << bit_index

            result += bytes([byte])

        return result

    def __str__(self) -> str:
        return ''.join(str(bit) for bit in self.bits)

    def __list__(self) -> list[int]:
        return self.bits

    def index(self, index: Index) -> Union[int, 'Mem']:
        pass

    def signed_index(self):
        pass  # TODO(pbz): Set a slice of bits with a signed integer value

    @property
    def bit_length(self) -> int:
        return len(self.bits)

    @property
    def byte_length(self) -> int:
        return bytes_needed(self.bit_length)

    def __getitem__(self, index: slice) -> Union['Mem', int]:
        """
        Index from left to right or right to left using bytes or bits.

        The index is a slice type but the `step` field is used as the memory
        order and granularity (left to right or right to left, bits or bytes).
        If no order/granularity is given in place of the step, left to right
        with bits is assumed. When `start` and `stop` fields are not provided,
        they are filled with zero and bit or byte length, depending on memory
        granularity, which is by bits by default.

        Examples:

        >>> mem = Mem.from_bit_length(1024)
        >>> mem[0]  # First bit from left to right
        >>> mem[-1]  # Last bit from left to right
        >>> mem[0:RBT]  # First bit from right to left
        >>> mem[-1:RBT]  # Last bit from left to right
        >>> mem[:3]  # First 3 bits from left to right
        >>> mem[:3:LBT]  # First 3 bits from left to right
        >>> mem[:3:RBT]  # First 3 bits from right to left
        >>> mem[::RBT]  # All bits from right to left
        >>> mem[::LBY]  # All bytes from left to right
        >>> mem[0:4]  # First 3 bits from left to right
        >>> mem[4:0]  # Null memory returned

        >>> mem = Mem.from_bit_length(4, byte_length=0)
        >>> assert str(mem) == '0000'
        >>> mem[0:LBT]  # Error: bit length is 4, byte length is 0

        """
        # TODO(pbz): Do not support negative numbers, byte length might not be
        # TODO(pbz): set in stone. Also, do you wrap from byte or bit bounds?

        print(index)

        return

        order_and_granularity = index.step or Indexing.LBT

        # assert order_and_granularity in (LBR, LBT, RBY, RBT), (
        #     'Invalid order/granularity'
        # )

        start = 0 if index.start == None else index.start
        stop = index.stop
        stop = 0 if index.stop == None else index.stop

        # ! Set the start/stop/step and do the index
        # ? Perhaps table/shelf/pin this for now
        # TODO(pbz): Perhaps split into indexing methods for testability?

        if order_and_granularity == LBT:
            stop = index.stop or len(self.bits)
        if order_and_granularity == RBT:
            stop = index.stop or 0


        # TODO(pbz): Return null or throw here?
        if not (stop >= start):  # Written for clarity. Don't reverse logic
            return NULLMEM
        assert stop >= start, 'Stop index must be greater than/equal to start'



        # TODO(pbz): Validate that requested bit/byte lays in bounds

        return 0

    def is_null(self):
        return self.bits == []

    @classmethod
    def from_bit_length(cls, bit_length: int) -> 'Mem':
        mem = cls()
        mem.bits = [0] * bit_length
        return mem

    @classmethod
    def from_byte_length(cls, byte_length: int) -> 'Mem':
        mem = cls()
        mem.bits = [0] * 8 * byte_length
        return mem

    @classmethod
    def from_bits(cls, bits: list[int] | str, byte_length: int = None) -> 'Mem':
        if not bits:
            return Mem.from_byte_length(byte_length or 0)

        if byte_length == None:
            bit_length = len(bits)
        else:
            bit_length = byte_length * 8

        assert bit_length > 0, 'Provided byte length must be positive'
        assert len(bits) <= bit_length, 'Provided byte length not large enough'

        mem = cls.from_bit_length(bit_length)

        for i, bit in enumerate(map(int, bits)):
            mem.bits[i] = bit

        return mem

    @classmethod
    def from_bytes(
        cls,
        bytes_: bytes | list[int],
        byte_type: Int,
        byte_order: Order = Order.LeftToRight
    ) -> 'Mem':
        """
        No matter what is passed in (bits, u8, i64, etc.), they are read in the
        provided byte order and the memory is filled from left to right.

        [0x12, 0x34, 0x56, 0x78], Order.RightToLeft
        [0x78, 0x56, 0x34, 0x12]
        """
        if not bytes_:
            return Mem.from_bit_length(0)

        match byte_type, byte_order:
            case Int.u8, Order.LeftToRight:
                [0x12, 0x34, 0x56, 0x78] == [0x78, 0x56, 0x34, 0x12]


NULLMEM = Mem()
