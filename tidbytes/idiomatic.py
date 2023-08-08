from typing import Any, Generic, TypeVar
from .mem_types import *
from .von_neumann import *
from .codec import *

T = TypeVar('T')

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

# TODO(pbz): 7/28/23
# TODO(pbz): Remove all the Mem.from_x() and just use decentralized codec funcs


# TODO(pbz): 8/2/23
# TODO(pbz): Is it truly that there cannot be one data entry point since there
# TODO(pbz): are things like `is_numeric`, `ascii`, and other metadata?


# class MemFactory:
#     def __call__(self, *args, **kwargs):
#         pass

#     def register_codec(self, codec):
#         pass

# Mem = MemFactory()
# Mem.register_codec(...)

# Mem(123)
# Mem('asdf', ascii=True)


# class MemBuilder:
#     def __call__(self, *args, **kwargs):
#         pass

#     def __getattribute__(self, attribute: str):
#         return lambda: self

# Mem = MemBuilder().foo().bar().baz()






# Mem.from_x()
# Mem.from_y()
# Mem.from_z()

# Flip on it's head!
# MemX()
# MemY()
# MemZ()


"""
Mem assumes non-numeric bytes data
Num assumes numeric data
F32 assumes non-numeric bytes data or floats

Mem.from & Mem.into
Num.from & Num.into are different
F32.from & F32.into are different
"""


# class Mem: ...
# class Num(Mem): ...  # Indexing is different
# class Float(Mem): ...  # Indexing is same, but contains Num exp and mantissa
# class I32(Num): ...  # Operations are different
# class U32(Num): ...  # Operations are different


# ! Mem is for memory regions. NumericMem is for numeric memory


# ! A::from<B> is the same as B::into<A>


# TODO(pbz): Assume numeric and allow users to call free-floating codecs:
# TODO(pbz): Assume numeric and allow users to call free-floating codecs:
# TODO(pbz): Assume numeric and allow users to call free-floating codecs:
# TODO(pbz):
# TODO(pbz):
# TODO(pbz):
# TODO(pbz): mem = Mem(123)
# TODO(pbz): mem = tidbytes.codecs.from_ascii("Hello World!")
# TODO(pbz):
# TODO(pbz): But what about legit memory regions?
# TODO(pbz): mem = Mem("Hello World!".encode())
# TODO(pbz):
# TODO(pbz): Assume numeric and allow users to call free-floating codecs:
# TODO(pbz): Assume numeric and allow users to call free-floating codecs:

# It's not common to use an integer as a memory region.
# Sensible defaults: assume literals are numeric data not memory.


# TODO(pbz): 8/4/23
class Mem:
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
        self.rgn = self.from_(init)
        self.validate()

        # All codec methods treat input values as left to right big and byte
        # order so transforming according to the input bit and byte order always
        # results in left to right bit and byte order.
        op_transform(self.rgn, in_bit_order, in_byte_order)

    def __setitem__(self, key, value):
        payload = MemRgn()
        payload.bytes = [[value] + [None] * 7]
        op_set_bit(self.rgn, key, payload)

    def __iter__(self):
        "TODO(pbz): Should this iter bits or bytes?"

    def __reversed__(self):
        "This might cause more harm than good as the bits will also be reversed"

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
        # TODO(pbz): It seems like most of these built-ins work with bits...?
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

    def truncate(self, bit_length: int):
        "Useful for setting values in structs that are shorter than a byte."
        self.rgn = op_truncate(self.rgn, bit_length)

    # ! -> Mem::from <-
    @classmethod
    def from_(cls, init: T) -> 'Mem':
        # ? ctypes
        # ? strings are always UTF8
        # ? bytes (str.encode('ascii'), hash())
        # ? bytearray

        '''
        match type(init):
            case MemRgn():
                return init
            case int():
                return from_big_integer(init)
            case u8():
                return from_byte_u8(init)
            case u16():
                return from_bytes_u16(init)
            case _:
                raise MemException('Invalid initializer')
        '''

        if isinstance(init, MemRgn):
            return init
        elif isinstance(init, int):
            return from_big_integer(init)
        elif isinstance(init, u8):
            return from_byte_u8(init)
        elif isinstance(init, u16):
            return from_bytes_u16(init)
        elif isinstance(init, u32):
            return from_bytes_u32(init)
        elif isinstance(init, u64):
            return from_bytes_u64(init)
        elif isinstance(init, f32):
            return from_f32(init)
        elif isinstance(init, f64):
            return from_f64(init)

        elif isinstance(init, str):
            return from_utf8(init.encode())
        elif isinstance(init, bytes):
            return from_bytes(init)
        elif isinstance(init, bytearray):
            return from_bytes(bytes(init))

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



class Num(Mem):
    "Assumes numeric data"

    # ! -> Num::from <-
    @classmethod
    def from_(cls, init: T) -> 'Num':
        if isinstance(init, u8):
            return from_numeric_u8(init)
        elif isinstance(init, u16):
            return from_numeric_u16(init)
        else:
            raise MemException('Invalid initializer')

    # ! -> Num::into <-
    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_byte_u8(self.rgn)


class I32(Num):
    "Specializes even further with From & Into"

class F32(Mem):
    pass


class Struct:
    foo: Num
    bar: I32
    baz: F32
    pbz: 'Struct'

    def __init__(self):
        self.regions = {}  # Tracks multiple regions or nested Structs

    def __getattribute__(self, attribute: str) -> Any:
        # TODO(pbz): Access nested attributes
        return super().__getattribute__(attribute)
