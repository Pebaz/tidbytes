import sys
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
        return ' '.join(
            ''.join(
                str(bit) if bit != None else ''  # ? '▫'
                for bit in byte
            )
            for byte in self.rgn.bytes
        )

    def __repr__(self):  # Debug
        bits = str(self)
        return f'<Mem [{bits}]>'

    __format__ = __str__

    def __add__(self, other):
        mem = Mem()
        mem.rgn = op_concatenate(self.rgn, other.rgn)
        return mem.validate()

    def validate(self):
        validate_memory(self.rgn)
        return self

    # TODO(pbz): What about byte order?
    @classmethod
    def from_u8(cls, value, bit_length=8):
        """
        This is different from `from_u8_as_byte()` because it assumes the provided
        u8 value is numeric data with the least significant bit on the right.
        This means bit order is from right to left always.

        For instance, 0b00010011 will be turned into: [00010011]. It appears
        the same as written because it is treated as a numeric value.
        """
        ensure(bit_length <= 8, 'Only 8 bits in a u8')
        ensure(value >= 0, 'Positive values only')

        mem = cls()
        byte = []

        for i in range(bit_length):
            bit = int(bool(value & (1 << i)))
            sys.byteorder == 'little'
            byte.insert(0, bit)

        mem.rgn.bytes.append((byte + [None] * 8)[:8])

        return mem.validate()

    # TODO(pbz): What about byte order?
    @classmethod
    def from_u8_as_byte(cls, value, bit_length=8):
        """
        This is different from `from_u8()` because it assumes that the provided
        u8 value is not numeric data but a slice of memory 1-byte long. This
        means bit order is left to right always.

        Providing a lower bit length lets fewer than 8 bits to be stored.

        For instance, 0b00010011 will be turned into: [11001000]. It appears
        backwards because it is treated as a memory region not a numeric value.
        """
        ensure(bit_length <= 8, 'Only 8 bits in a u8')
        ensure(value >= 0, 'Positive values only')

        mem = cls()
        byte = []

        for i in range(bit_length):
            bit = int(bool(value & (1 << i)))
            sys.byteorder == 'little'
            byte.append(bit)

        mem.rgn.bytes.append((byte + [None] * 8)[:8])

        return mem.validate()

    # TODO(pbz): Could probably parametrize this over enum of u8, u16 with len()
    # TODO(pbz): What about byte order?
    @classmethod
    def from_u16_as_bytes(cls, value, bit_length=16):
        """
        The bits of the number will be exactly reversed from how they are
        written.

        Treat the bytes of a number as a memory region, not a numeric value.

        Note: Byte order is system byte order.
        Note: Bit order is left to right.

        For instance, 0b1_00010011 will be turned into: [11001000 10000000]. It
        appears backwards because it is treated as a memory region not a numeric
        value.
        """
        ensure(bit_length <= 16, 'Only 16 bits in a u16')
        ensure(value >= 0, 'Positive values only')

        mem = cls.from_u16(value, bit_length)

        if sys.byteorder == 'big':
            mem.rgn = op_reverse(mem.rgn)

        return mem.validate()

    @classmethod
    def from_u16(cls, value, bit_length=16):
        """
        There's no need to assume the byte order. It will always match the order
        of the system. To load an integer from another memory universe, use the
        memory transformation operations such as reverse_bytes, etc.

        Note: Byte order is system byte order.
        Note: Bit order is right to left.

        For instance, 0b1_00010011 will be turned into: [00000001 00010011]. It
        appears the same as written because it is treated as a numeric value.
        """
        ensure(bit_length <= 16, 'Only 16 bits in a u16')
        ensure(value >= 0, 'Positive values only')

        # mem = cls()
        # byte = []

        # for i in range(bit_length):
        #     bit = int(bool(value & (1 << i)))

        #     byte.insert(0, bit)

        #     if len(byte) == 8:
        #         if sys.byteorder == 'little':
        #             mem.rgn.bytes.append(byte[:])
        #         else:
        #             mem.rgn.bytes.insert(0, byte[:])

        #         byte.clear()

        # if byte:
        #     mem.rgn.bytes.append((byte + [None] * 8)[:8])

        # return mem.validate()

        mem = cls()
        byte = []

        for i in range(bit_length):
            bit = int(bool(value & (1 << i)))
            sys.byteorder == 'little'
            byte.append(bit)

            if len(byte) == 8:
                mem.rgn.bytes.append(byte[:])
                byte.clear()

        if byte:
            mem.rgn.bytes.append((byte + [None] * 8)[:8])

        return mem.validate()


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
