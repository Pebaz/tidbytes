import ctypes
from enum import Enum, auto


class Order(Enum):
    LeftToRight = auto()  # First element is on far left
    RightToLeft = auto()  # First element is on far right


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


class Sized(type):
    "Metaclass that allows index syntax to add integer size attribute per class"

    # For every class that has Sized as a metaclass, the base classes and dict
    # definition are stored here by class name so that a `size` static field can
    # be added onto it
    tracked_types: dict[str, tuple[list[type]], dict[str, object]] = {}

    # To prevent many same-sized duck types from being created, track each new
    # sized types by name and size
    tracked_sized_types: dict[tuple[type, int], type] = {}

    def __new__(cls, name, bases, dict_):
        cls.tracked_types[name] = bases, dict_

        # Returns exactly 1 unique type without a static `size` field so that
        # it can be used along with subscript syntax `[]` to produce any number
        # of subclasses that customize that size type
        return super().__new__(cls, name, bases, dict_)

    def __getitem__(self, size):
        """
        Create unique class (not instance) with custom size.

        If this method is called several times with the same size input, it will
        produce that many new classes.
        """

        lookup = self.__name__, size

        if lookup in self.tracked_sized_types:
            return self.tracked_sized_types[lookup]

        bases, dict_ = self.tracked_types[self.__name__]

        # This can return any number of new classes that are exact duck types of
        # the class originally stored in `tracked_types`. The difference is the
        # static field `size` that is customized in this method
        new_class = super().__new__(
            self.__class__,
            self.__name__,
            bases,

            # Make sure to add the static field here to prevent always having
            # the last known value being stored on the type
            dict(size=size, **dict_)
        )

        self.tracked_sized_types[lookup] = new_class

        return new_class

    def __str__(self):
        return f'{self.__name__}[{getattr(self, "size", "")}]'

    def __repr__(self):
        return str(self)

    def __format__(self, _format):
        return str(self)


class Mem(metaclass=Sized):
    def __init__(self):
        self.bits = [0] * getattr(self, 'size', 0)
        self.bit_order = Order.LeftToRight
        self.byte_order = Order.LeftToRight

    def __getitem__(self, index: slice):
        return self.index(index)

    def __setitem__(self, index, value):
        self.set_bits(index, value)

    def index(self, index: slice):
        "Bit and byte order is controlled per class, per instance"
        "Sub classes don't have to write bit/byte order indexing"
        assert index.step is None, 'Cannot index using step'

    def set_bits(self, index: slice, value: Int):
        assert type(value) in Int.variants(), (
            f'Invalid data type for assignment: {type(value)}'
        )

        self.bits[index] = Int.bit_list(value, self.bit_order, self.byte_order)

    @classmethod
    def from_bits(cls, bits):
        # Since the heirarchy of Mem types are able to customize a static size
        # via subscript notation `[]`, there usually is a size static field to
        # read from. However, this is not the case when the Mem constructor is
        # called directly without having used `[]` first. Set the size to itself
        # or the number of bits passed in.
        if getattr(cls, 'size'):
            assert len(bits) <= cls.size
        else:
            cls.size = len(bits)

    # TODO(pbz): Use ctypes to control signedness, etc.
    def set_le_signed_byte(self, byte):
        "Checks to make sure int is within byte range"

    def __str__(self):
        # TODO(pbz): Take into account bit and byte order
        bits = ''.join(str(i) for i in self.bits)
        return f'<{type(self).__name__}[{getattr(self, "size", "")}] {bits}>'

    def __repr__(self):
        return str(self)

    def __format__(self, _format):
        return str(self)


class Num(Mem):
    "Unsigned numbers"

    def __init__(self, endianness=Order.LeftToRight):
        super().__init__()
        self.bit_order = Order.RightToLeft
        self.byte_order = endianness

    def be() -> 'Num':
        return Num(endianness=Order.LeftToRight)

    def le() -> 'Num':
        return Num(endianness=Order.RightToLeft)


class Signed(Num):
    "Twos-complement to store sign."


class Struct:
    def __init__(self):
        bit_ranges = self.__annotations__
        default_values = {
            i: getattr(type(self), i)
            for i in self.__annotations__
            if hasattr(type(self), i)
        }

        print('ℹ️', bit_ranges)
        print('ℹ️', default_values)

        #self.bit_ranges = {i: Mem() for i in self.__annotations__}

    def __getattr__(self, name):
        pass

    def __setattr__(self, name, value):
        "Call the appropriate set() method on the memory region"
        assert type(value) in Int.variants(), (
            f'Invalid data type for assignment: {type(value)}'
        )


class addi32le(Struct):
    sign: Mem[1]
    exponent: Num[12] = 123
    mantissa: Num[19]

a = Mem[1]()
print('➡️', a)
a[0] = Int.u8(1)
print('➡️', a)

addi32le()

# * Two Ideas:
# * Define C API functions for each of the index/assign operations
# * Progressively build Python API methods as needed for real use case
