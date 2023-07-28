from typing import Any
from .mem_types import *
from .von_neumann import *
from .codec import *

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

# TODO(pbz): 7/28/23
# TODO(pbz): Remove all the Mem.from_x() and just use decentralized codec funcs

class Mem:
    # !-------------------------------------------------------------------------
    # TODO(pbz): 7/28/23
    # TODO(pbz): This is the most important function in the whole library. It
    # TODO(pbz): allows any Python primitive type to be converted into Mem.
    # TODO(pbz): In Rust, From & Into traits allow this (sometimes
    # TODO(pbz): automatically). Here, the Constructor acts like an entrypoint
    # TODO(pbz): to the data by initializing it appropriately using codecs.
    # TODO(pbz): Since most users will want precise semantics, they will use the
    # TODO(pbz): types from C/Rust (u8, f64). However, idiomatic types work too.
    # !-------------------------------------------------------------------------
    def __init__(
        self,
        init: int = None,
        in_bit_order=Order.LeftToRight,
        in_byte_order=Order.LeftToRight
    ):
        """
        This is by far the most versatile constructor. It inspects the init
        value and calls the right codec method to initialize the memory region.
        Since it's up to the user to know the input memory origin universe, the
        appropriate memory transformation operation must be called directly
        after initialization to remain valid. To assist with this and to prevent
        errors, an input bit and byte order may be specified so that the right
        transformation operation can be called automatically. This is the funnel
        by which most users will initialize memory regions. However, for more
        explicit control, the other codec methods are a solid choice. The output
        bit and byte order is always left to right.
        """
        self.rgn = MemRgn()

        supported_codecs = {
            int: None,
            float: None,
            str: None,
            bytes: None,
            bytearray: None,
            list: None,
            u8: None,
            u16: None,
            u32: None,
            u64: None,
            i8: None,
            i16: None,
            i32: None,
            i64: None,
            f32: None,
            f64: None,
        }

        # TODO(pbz): Inspect `init` and call the right codec method
        if type(init) in supported_codecs:
            self.rgn = supported_codecs[type(init)](init)
        else:
            raise MemException(f'Ambiguous memory initializer: {type(init)}')

        # All codec methods treat input values as left to right big and byte
        # order so transforming according to the input bit and byte order always
        # results in left to right bit and byte order.
        op_transform(self.rgn, in_bit_order, in_byte_order)

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

    def __reversed__(self):
        "This might cause more harm than good as the bits will also be reversed"

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






    # TODO(pbz): 7/28/23
    # TODO(pbz): These are not codecs because "bit/byte length" is not a type.
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
    # TODO(pbz): These definitions are good just convert them to codecs

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
