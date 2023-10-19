import indexed_meta
from typing import Any, Generic, TypeVar
from .mem_types import (
    ensure, MemException, Order, u8, u16, u32, u64, i8, i16, i32, i64, f32, f64
)
from .von_neumann import (
    MemRgn, op_transform, op_set_bit, meta_op_bit_length, op_concatenate,
    op_truncate, contract_validate_memory, group_bits_into_bytes,
    iterate_logical_bits, op_get_bit
)
from .codec import (
    from_natural_u8, from_natural_u16, from_natural_u32, from_natural_u64,
    from_numeric_u8, from_numeric_u16, from_numeric_u32, from_numeric_u64,
    from_natural_i8, from_natural_i16, from_natural_i32, from_natural_i64,
    from_numeric_i8, from_numeric_i16, from_numeric_i32, from_numeric_i64,
    from_natural_f32, from_natural_f64, from_numeric_f32, from_numeric_f64,
    from_natural_big_integer, from_numeric_big_integer, from_natural_float,
    from_numeric_float, from_bool, from_bit_list, from_grouped_bits, from_bytes,
    from_bytes_utf8, into_byte_u8
)

T = TypeVar('T')

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

# ! These are solutions for handling codecs that take parameters. Codecs are
# ! like twos-complement. Without a destination bit length, they are undefined.
'''
# Factory Pattern:
class MemFactory:
    def __call__(self, *args, **kwargs):
        pass

    def register_codec(self, codec):
        pass

Mem = MemFactory()
Mem.register_codec(...)

# Parameterized Constructor:
Mem(123)
Mem('asdf', ascii=True)

# Builder Pattern:
class MemBuilder:
    def __call__(self, *args, **kwargs):
        pass

    def __getattribute__(self, attribute: str):
        return lambda: self

Mem = MemBuilder().foo().bar().baz()
'''

"""
class Mem: ...         # Assumes non-numeric bytes data
class Num(Mem): ...    # Assumes numeric data, indexing is reversed
class Struct: ...      # Allows free and structured indexing
class Float(Mem): ...  # Actually a type of struct. Indexing should work.
class I32(Num): ...    # From/Into codecs are different (int value is negative)
class U32(Num): ...    # From/Into codecs are different
"""



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# There may be a problem: does Num convert to identity, perform op, and then go
# back? If all operations assume identity, how was this going to work?






# TODO(pbz): 8/4/23
class Mem(metaclass=indexed_meta.IndexedMetaclass):
    """
    "Pure" memory. Can work with any kind of input data and can perform the most
    operations because it has no semantic restrictions on the input or output
    data. Maps all input memory to identity so all bits and bytes are left to
    right.

    The associated indexed meta parameter for Mem is a limit describing the
    desired size of the memory region. If initializer values are smaller than
    the requested size, the excess is padded with zeros. If they are larger than
    would fit in the requested size, they are truncated or an error is thrown if
    that would violate a logical/semantic contract/validation boundary.

    Said another way: bit_length is metadata about the memory region itself, not
    metadata from the codec like `len(str)`.
    """
    def __init__(
        self,
        init: T = None,
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
        self.rgn = self.from_(init, bit_length=indexed_meta.get_param(self))
        self.validate()

        # All codec methods treat input values as left to right big and byte
        # order so transforming according to the input bit and byte order always
        # results in left to right bit and byte order.
        op_transform(self.rgn, bit_order=in_bit_order, byte_order=in_byte_order)

    def __setitem__(self, key, value):
        payload = MemRgn()
        payload.bytes = [[value] + [None] * 7]
        op_set_bit(self.rgn, key, payload)

    def __iter__(self):
        "Iterator over integer bits containing 0 or 1."
        return iterate_logical_bits(self.rgn.bytes)

    def __reversed__(self):
        "This might cause more harm than good as the bits will also be reversed"

    def __str__(self):  # Display
        """
        Displays all bits up to bit length 64, then displays bit length.
        """
        return ' '.join(
            ''.join(
                str(bit) if bit is not None else ''  # ? '▫'
                for bit in byte
            )
            for byte in self.rgn.bytes
        )

    def __repr__(self):  # Debug
        bits = str(self)

        # More than 8 bytes is getting long
        if bits.count(' ') > 7:
            bits = hex(int(''.join(bits.split()), base=2))[2:]

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

    def __eq__(self, that):
        return self.rgn.bytes == that.rgn.bytes

    def __len__(self):
        return meta_op_bit_length(self.rgn)

    def __bool__(self):
        "False if Mem is null else True"
        return bool(self.rgn.bytes)

    def __int__(self):
        "Treats the memory region as an unsigned integer."
        out = 0
        for i, bit in enumerate(reversed(list(self))):
            if bit:
                out |= 1 << i
        return out

    def __add__(self, other):
        mem = Mem()
        mem.rgn = op_concatenate(self.rgn, other.rgn)
        return mem.validate()

    def __getitem__(self, index: slice) -> Any:
        # TODO(pbz): Implement indexing operations
        print('here')

    def validate(self):
        if self.rgn.bytes:
            contract_validate_memory(self.rgn)
        return self

    def truncate(self, bit_length: int):
        "Useful for setting values in structs that are shorter than a byte."
        self.rgn = op_truncate(self.rgn, bit_length)

    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Mem':
        if bit_length == 0:
            return MemRgn()

        elif isinstance(init, type(None)):
            if bit_length is None:
                return MemRgn()
            else:
                rgn = MemRgn()
                rgn.bytes = group_bits_into_bytes([0] * bit_length)
                return rgn
        elif isinstance(init, MemRgn):
            return init

        elif isinstance(init, bool):  # isinstance(True, int) == True
            return from_bool(init, bit_length)
        elif isinstance(init, int):
            return from_natural_big_integer(init, bit_length)
        elif isinstance(init, float):
            return from_natural_float(init, bit_length)

        elif isinstance(init, u8):
            return from_natural_u8(init, bit_length)
        elif isinstance(init, u16):
            return from_natural_u16(init, bit_length)
        elif isinstance(init, u32):
            return from_natural_u32(init, bit_length)
        elif isinstance(init, u64):
            return from_natural_u64(init, bit_length)

        elif isinstance(init, i8):
            return from_natural_i8(init, bit_length)
        elif isinstance(init, i16):
            return from_natural_i16(init, bit_length)
        elif isinstance(init, i32):
            return from_natural_i32(init, bit_length)
        elif isinstance(init, i64):
            return from_natural_i64(init, bit_length)

        elif isinstance(init, f32):
            return from_natural_f32(init, bit_length)
        elif isinstance(init, f64):
            return from_natural_f64(init, bit_length)

        elif isinstance(init, list):
            if not init:
                return MemRgn()
            elif init and isinstance(init[0], (list, tuple)):
                return from_grouped_bits(init, bit_length)
            elif init and isinstance(init[0], int):
                return from_bit_list(init, bit_length)
            else:
                raise MemException("Invalid initializer: Can't deduce codec")

        elif isinstance(init, str):
            # TODO(pbz): from_hex_str('0xFF')
            # TODO(pbz): from_bin_str('0b11101001101101101')
            return from_bytes(init.encode(), bit_length)
        elif isinstance(init, bytes):
            return from_bytes(init, bit_length)
        elif isinstance(init, bytearray):
            return from_bytes(bytes(init), bit_length)

        else:
            raise MemException('Invalid initializer')

    # ! -> Mem::into <-
    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_byte_u8(self.rgn)
        if target_type == str:
            "return into_utf8(self.rgn)"
        else:
            raise MemException('Invalid type')


NullMem = Mem()



# TODO(pbz): Indexing is backwards
class Signed(Mem): ...
class Number(Mem): ...
class Integer(Mem): ...
class Num(Mem):
    """
    Semantically meaningful data representing numeric information. Input types
    are constrained since the output concept is a quantity and not raw memory.
    Supports positive and negative integers. At least one bit of the memory
    region must be given to support differentiation of positive and negative
    values stored in two's-complement encoding. This means the smallest bit
    length that is supported is 2.

    With bit length of 3:
        000 = 0
        001 = 1
        010 = 2
        011 = 3
        100 = -4
        101 = -3
        110 = -2
        111 = -1

    With bit length of 2:
        00 = 0
        01 = 1
        10 = -2
        11 = -1
    """

    def __iter__(self):
        "Iterator over integer bits containing 0 or 1."
        return reversed(list(iterate_logical_bits(self.rgn.bytes)))

    def __bool__(self):
        "False if Num is null or 0 else True for any non-null, non-zero value."
        return bool(int(self))

    def __int__(self):
        # TODO(pbz): Use into_numeric_big_integer()

        # TODO(pbz): have to validate that NUM() checks bit length is big enough to store 3: 2 bits is not enough!

        if not self.rgn.bytes:
            return 0

        # TODO(pbz): Rename von_neumann to natural
        bits = ''.join(str(self).split())

        if bits[0] == '1':  # Negative
            raw_integer_value = int(bits, base=2)
            ones_complement = bin(raw_integer_value - 1).lstrip('0b')

            # Preserve bit length for invert
            if len(ones_complement) < len(self):
                ones_complement = '0' + ones_complement

            inverted_bits = ''.join('10'[int(i)] for i in ones_complement)
            return -int(inverted_bits, base=2)

        else:
            return int(bits, base=2)

    # ! -> Num::from <-
    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Num':
        ensure(
            bit_length in (None, 0) or bit_length >= 2,
            f"Not enough bits to encode both positive and negative numbers: "
            f"{bit_length}. Two's complement encoding requires at least 2 bits"
        )

        if isinstance(init, type(None)):
            return MemRgn()
        elif isinstance(init, int):
            return from_numeric_big_integer(init, bit_length)
        elif isinstance(init, float):
            return from_numeric_float(init, bit_length)
        elif isinstance(init, bool):
            return from_bool(init)
        elif isinstance(init, list):
            if not init:
                return MemRgn()
            elif init and isinstance(init[0], (list, tuple)):
                return from_grouped_bits(init)
            elif init and isinstance(init[0], int):
                return from_bit_list(init)
            else:
                raise MemException("Invalid initializer: Can't deduce codec")
        elif isinstance(init, tuple):
            return from_bytes(init)

        elif isinstance(init, u8):
            return from_numeric_u8(init, bit_length)
        elif isinstance(init, u16):
            return from_numeric_u16(init, bit_length)
        elif isinstance(init, u32):
            return from_numeric_u32(init, bit_length)
        elif isinstance(init, u64):
            return from_numeric_u64(init, bit_length)

        elif isinstance(init, i8):
            return from_numeric_i8(init, bit_length)
        elif isinstance(init, i16):
            return from_numeric_i16(init, bit_length)
        elif isinstance(init, i32):
            return from_numeric_i32(init, bit_length)
        elif isinstance(init, i64):
            return from_numeric_i64(init, bit_length)

        elif isinstance(init, f32):
            return from_numeric_f32(init, bit_length)
        elif isinstance(init, f64):
            return from_numeric_f64(init, bit_length)

        else:
            raise MemException('Invalid initializer')

    # ! -> Num::into <-
    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_byte_u8(self.rgn)


class Str(Mem):
    """
    Semantically meaningful data representing a array of UTF8 code points. Not
    distinct from an array of unsigned 8 bit integers. Input types are
    constrained since the output concept is the logical notion of string rather
    than raw memory.
    """

    # ! -> Str::from <-
    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Str':
        if isinstance(init, type(None)):
            return MemRgn()
        elif isinstance(init, str):
            return from_bytes_utf8(init.encode(), bit_length)
        elif isinstance(init, list):
            if not init:
                return MemRgn()
            elif init and isinstance(init[0], int) and 0 <= init[0] <= 255:
                return from_bytes_utf8(bytearray(init))
            else:
                raise MemException("Invalid initializer: Can't deduce codec")
        else:
            raise MemException('Invalid initializer')

    # ! -> Str::into <-
    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_byte_u8(self.rgn)

    def __str__(self):
        chars = (int(byte, base=2) for byte in Mem.__str__(self).split())
        return bytearray(chars).decode()


'''

# class U32(Num[32]):
#     "Does not support signed"



# TODO(pbz): Do NOT implement __add__ and other common ops. Is not the purpose.
class I32(Num):
    "Specializes even further with From & Into. Twos-complement for signed"


# TODO(pbz): Should probably subclass Struct to have [sign, exp, mantissa] but
# TODO(pbz): should fully support indexing like Mem
class F32(Mem):
    pass



# TODO(pbz): What would make this project complete?
# TODO(pbz): A Mem type that can support indexing and all other operations.



# ! Pass bits as init value to set each inner type
class Struct:
    """
    foo: Num
    bar: I32
    baz: F32
    pbz: 'Struct'
    """
    # TODO(pzb): Support nested types
    # TODO(pzb): Support offset
    # TODO(pzb): Support padding
    # TODO(pzb): Support alignment

    def __init__(self):
        self.regions = {}  # Tracks multiple regions or nested Structs

        bit_ranges = self.__annotations__
        default_values = {
            i: getattr(type(self), i)
            for i in self.__annotations__
            if hasattr(type(self), i)
        }

        print('ℹ️', bit_ranges)
        print('ℹ️', default_values)

        self.bit_ranges = {i: Mem() for i in self.__annotations__}

    def __getattr__(self, name):
        pass

    def __setattr__(self, name, value):
        "Call the appropriate set() method on the memory region"
        assert type(value) in Int.variants(), (
            f'Invalid data type for assignment: {type(value)}'
        )

    def __getattribute__(self, attribute: str) -> Any:
        # TODO(pbz): Access nested attributes
        return super().__getattribute__(attribute)


class addi32le(Struct):
    sign: Mem[1]
    exponent: Num[12] = 123
    mantissa: Num[19]
'''
