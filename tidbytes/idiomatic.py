"""
Design decisions:
    - Operator overloads for idiomatic types return new copies of themselves
        since there should be no side-effects.
"""

import copy
import indexed_meta
from typing import Any, Generic, TypeVar, Union
from .mem_types import (
    ensure, MemException, Order, u8, u16, u32, u64, i8, i16, i32, i64, f32, f64,
    UnderOverflowException
)
from .natural import (
    MemRgn, meta_op_bit_length, contract_validate_memory, group_bits_into_bytes,
    iterate_logical_bits, op_transform, op_identity, op_reverse,
    op_reverse_bytes, op_reverse_bits, op_get_bit, op_get_byte, op_get_bits,
    op_get_bytes, op_set_bit, op_set_bits, op_set_byte, op_set_bytes,
    op_truncate, op_extend, op_ensure_bit_length, op_ensure_byte_length,
    op_concatenate
)
from .codec import (
    from_natural_u8, from_natural_u16, from_natural_u32, from_natural_u64,
    from_numeric_u8, from_numeric_u16, from_numeric_u32, from_numeric_u64,
    from_natural_i8, from_natural_i16, from_natural_i32, from_natural_i64,
    from_numeric_i8, from_numeric_i16, from_numeric_i32, from_numeric_i64,
    from_natural_f32, from_natural_f64, from_numeric_f32, from_numeric_f64,
    from_natural_float, from_numeric_float, from_bool, from_bit_list,
    from_grouped_bits, from_bytes, into_numeric_big_integer,
    into_natural_big_integer, from_bytes_utf8, from_numeric_big_integer_signed,
    from_numeric_big_integer_unsigned, from_natural_big_integer_unsigned,
    range_signed
)

T = TypeVar('T')

# ! ----------------------------------------------------------------------------
# ! Idiomatic API
# ! ----------------------------------------------------------------------------

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

        # All codec methods treat input values as left to right bit and byte
        # order so transforming according to the input bit and byte order always
        # results in left to right bit and byte order.
        self.rgn = op_transform(
            self.rgn,
            bit_order=in_bit_order,
            byte_order=in_byte_order
        )

    def __iter__(self):
        "Iterator over integer bits containing 0 or 1."
        return iterate_logical_bits(self.rgn.bytes)

    def __reversed__(self):
        "Iterator over integer bits containing 0 or 1 in reverse order."
        return reversed(list(iterate_logical_bits(self.rgn.bytes)))

    # TODO(pbz): Name shadowing but I don't want to remove this unless it's good
    def identity(self):
        "Returns a new region with identity memory order (unchanged)."
        return type(self)(self, Order.LeftToRight, Order.LeftToRight)

    clone = identity

    def reverse(self):
        "Returns a new region with all bits and bytes reversed."
        return type(self)(self, Order.RightToLeft, Order.RightToLeft)

    def reverse_bits(self):
        "Returns a new region with all bytes in place with reversed bits."
        return type(self)(self, Order.RightToLeft, Order.LeftToRight)

    def reverse_bytes(self):
        "Returns a new region with all bits in place but reversed bytes."
        return type(self)(self, Order.LeftToRight, Order.RightToLeft)

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
            bits = hex(int(''.join(bits.split()), base=2))

        return f'<{type(self).__name__} [{bits}]>'

    def __format__(self, specifier: str) -> str:
        match specifier:
            case 'bits':
                return str(self)
            case 'hex' | 'x':
                return hex(int(''.join(str(self).split()), base=2))
            case 'X':
                return format(self, 'x').upper()
            case _:
                return str(self)

    def __eq__(self, that):
        ensure(
            isinstance(that, type(self)),
            f'Cannot compare unlike types: {type(self)} and {type(that)}'
        )
        return self.rgn.bytes == that.rgn.bytes

    def __len__(self):
        return meta_op_bit_length(self.rgn)

    def __bool__(self):
        "False if Mem is null or all zeroes else True"
        return any(iterate_logical_bits(self.rgn.bytes))

    def __int__(self):
        "Treats the memory region as an unsigned integer."
        return into_natural_big_integer(self.rgn)

    def __add__(self, other):
        out = Mem()
        out.rgn = op_concatenate(self.rgn, other.rgn)
        return out.validate()

    def __getitem__(self, index: slice) -> Any:
        "Exclusive end index."

        # TODO(pbz): It might be amazing to support negative indexes only here

        if isinstance(index, int):  # Simple bit index
            out = type(self)()
            out.rgn = op_get_bit(self.rgn, index)
            return out

        ensure(isinstance(index, slice), f'Invalid index: {type(index)}')

        start, stop, step = index.start, index.stop, index.step

        if start is stop is step is None:
            return type(self)(self)

        ensure(step in (None, 1, 8), 'Can only index by bit or byte')

        out = type(self)()

        match (start, stop, step):  # Bit or byte slices from here on out
            # mem[::1]
            case [None, None, int()]:
                return type(self)(self)

            # mem[1::1]
            case [int(), None, 1]:
                out.rgn = op_get_bits(self.rgn, start, len(self))

            # mem[1::8]
            case [int(), None, 8]:
                from .natural import meta_op_byte_length
                out.rgn = op_get_bytes(
                    self.rgn,
                    start,
                    meta_op_byte_length(self.rgn)
                )

            # mem[:1]
            # mem[:1:1]
            case [None, int(), None] | [None, int(), 1]:
                out.rgn = op_get_bits(self.rgn, 0, stop)

            # mem[:1:8]
            case [None, int(), 8]:
                out.rgn = op_get_byte(self.rgn, stop // 8)

            # mem[0:1]
            # mem[0:1:]
            # mem[0:1:1]
            case [int(), int(), None] | [int(), int(), 1]:
                out.rgn = op_get_bits(self.rgn, start, stop)

            # mem[0:1:8]
            case [int(), int(), 8]:
                out.rgn = op_get_bytes(self.rgn, start, stop)

            case _:
                ensure(False, f'Invalid index: [{start}:{stop}:{step}]')

        return out.validate()

    def __setitem__(self, index, payload):
        """
        Sets a range of bits with the given payload.

        The payload must be a valid initializer for Mem in order to pass
        validation and support indexing or be a Mem subclass directly.
        """
        payload = Mem(payload)  # Many payload types are supported in entrypoint

        if isinstance(index, int):
            self.rgn = op_set_bits(self.rgn, index, payload.rgn)

    def validate(self) -> 'Mem':
        if self.rgn.bytes:
            contract_validate_memory(self.rgn)
        return self

    def truncate(self, bit_length: int):
        "Useful for setting values in structs that are shorter than a byte."
        self.rgn = op_truncate(self.rgn, bit_length)

    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Mem':
        if isinstance(init, cls):  # Copy constructor
            out = MemRgn()
            out.bytes = copy.copy(init.rgn.bytes)
            return out

        elif bit_length == 0:
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
            if init < 0:
                raise MemException(
                    'Cannot interpret negative big integer as slice of raw '
                    'memory since raw bytes are unsigned. Use `Signed` instead'
                )
            return from_natural_big_integer_unsigned(init, bit_length)

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
            if init and init.startswith(('0x', '0X')):
                return from_natural_big_integer_unsigned(
                    int(init, base=16),
                    bit_length
                )
            elif init and init.startswith(('0b', '0B')):
                return from_natural_big_integer_unsigned(
                    int(init, base=2),
                    bit_length
                )
            return from_bytes(init.encode(), bit_length)

        elif isinstance(init, bytes):
            return from_bytes(init, bit_length)

        elif isinstance(init, bytearray):
            return from_bytes(bytes(init), bit_length)

        else:
            raise MemException('Invalid initializer')

    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_natural_big_integer(self.rgn)
        if target_type == str:
            "return into_utf8(self.rgn)"
        else:
            raise MemException('Invalid type')

    # Passthrough methods

    # passthrough = lambda op: locals()[op]

    import tidbytes.natural as nat
    for name, op in filter(lambda o: 'op_' in o[0], nat.__dict__.items()):
        def closure(op):
            def operation(self, *args, **kwargs):
                return type(self)(op(self.rgn, *args, **kwargs))
            return operation
        locals()[name.lstrip('op_')] = closure(op)

    # TODO(pbz): Although this works, payload args only support MemRgn so redo
    # TODO them all to call constructor on any type of payload.

    def transform(self, *, bit_order: Order, byte_order: Order) -> 'Mem':
        "See docs for `tidbytes.natural.op_transform`"
        self.rgn = op_transform(
            self.rgn,
            bit_order=bit_order,
            byte_order=byte_order
        )
        return self

    def identity(self) -> 'Mem':
        "See docs for `tidbytes.natural.op_identity`"
        self.rgn = op_identity(self.rgn)
        return self

    def reverse(self) -> 'Mem':
        "See docs for `tidbytes.natural.op_reverse`"
        self.rgn = op_reverse(self.rgn)
        return self

    def reverse_bytes(self) -> 'Mem':
        "See docs for `tidbytes.natural.op_reverse_bytes`"
        self.rgn = op_reverse_bytes(self.rgn)
        return self

    def reverse_bits(self) -> 'Mem':
        "See docs for `tidbytes.natural.op_reverse_bits`"
        self.rgn = op_reverse_bits(self.rgn)
        return self

    def get_bit(self, index: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_get_bit`"
        return type(self)[None](op_get_bit(self.rgn, index))

    def get_byte(self, index: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_get_byte`"
        return type(self)[None](op_get_byte(self.rgn, index))

    def get_bits(self, start: int, stop: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_get_bits`"
        return type(self)[None](op_get_bits(self.rgn, int(start), int(stop)))

    def get_bytes(self, start: int, stop: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_get_bytes`"
        return type(self)[None](op_get_bytes(self.rgn, int(start), int(stop)))

    def set_bit(self, offset: int, payload: T) -> 'Mem':
        "See docs for `tidbytes.natural.op_set_bit`"
        d = type(self)[None](payload).rgn
        import ipdb; ipdb.set_trace()
        self.rgn = op_set_bit(
            *(self.rgn, int(offset), d)
        )
        return self

    def set_bits(self, offset: int, payload: T) -> 'Mem':
        "See docs for `tidbytes.natural.op_set_bits`"
        self.rgn = op_set_bits(
            *(self.rgn, int(offset), type(self)[None](payload).rgn)
        )
        return self

    def set_byte(self, offset: int, payload: T) -> 'Mem':
        "See docs for `tidbytes.natural.op_set_byte`"
        self.rgn = op_set_byte(
            *(self.rgn, int(offset), type(self)[None](payload).rgn)
        )
        return self

    def set_bytes(self, offset: int, payload: T) -> 'Mem':
        "See docs for `tidbytes.natural.op_set_bytes`"
        self.rgn = op_set_bytes(
            *(self.rgn, int(offset), type(self)[None](payload).rgn)
        )
        return self

    def truncate(self, length: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_truncate`"
        self.rgn = op_truncate(self.rgn, int(length))
        return self

    def extend(self, amount: int, fill: T) -> 'Mem':
        "See docs for `tidbytes.natural.op_extend`"
        self.rgn = op_extend(self.rgn, int(amount), type(self)[None](fill))
        return self

    def ensure_bit_length(self, length: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_ensure_bit_length`"
        self.rgn = op_ensure_bit_length(self.rgn, int(length))
        return self

    def op_ensure_byte_length(self, length: int) -> 'Mem':
        "See docs for `tidbytes.natural.op_op_ensure_byte_length`"
        self.rgn = op_ensure_byte_length(self.rgn, int(length))
        return self

    def concatenate(self, mem_right: Union['Mem', MemRgn]) -> 'Mem':
        "See docs for `tidbytes.natural.op_concatenate`"
        self.rgn = op_concatenate(self.rgn, type(self)[None](mem_right).rgn)
        return self


NullMem = Mem()


class Unsigned(Mem):
    """
    Semantically meaningful data representing numeric information. Input types
    are constrained since the output concept is a quantity and not raw memory.
    Supports positive integers. Unsigned memory inheriting from Mem is a natural
    progression because unsigned numeric data can be fed to an arithmetic logic
    unit but is otherwise indistinct from raw bytes.
    """

    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Unsigned':
        if isinstance(init, cls):  # Copy constructors
            out = MemRgn()
            out.bytes = copy.copy(init.rgn.bytes)
            return out

        elif isinstance(init, type(None)):
            if bit_length is None:
                return MemRgn()
            else:
                rgn = MemRgn()
                rgn.bytes = group_bits_into_bytes([0] * bit_length)
                return rgn

        elif isinstance(init, int):
            return from_numeric_big_integer_unsigned(init, bit_length)

        elif isinstance(init, float):
            return from_numeric_float(init, bit_length)

        elif isinstance(init, bool):
            return from_bool(init)

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
            if init and init.startswith(('0x', '0X')):
                return from_numeric_big_integer_unsigned(
                    int(init, base=16),
                    bit_length
                )
            elif init and init.startswith(('0b', '0B')):
                return from_numeric_big_integer_unsigned(
                    int(init, base=2),
                    bit_length
                )
            return from_bytes(init.encode(), bit_length)

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
            ensure(
                init.value >= 0,
                'Implicit conversion from signed to unsigned'
            )
            return from_numeric_u8(u8(init.value), bit_length)

        elif isinstance(init, i16):
            ensure(
                init.value >= 0,
                'Implicit conversion from signed to unsigned'
            )
            return from_numeric_u16(u16(init.value), bit_length)

        elif isinstance(init, i32):
            ensure(
                init.value >= 0,
                'Implicit conversion from signed to unsigned'
            )
            return from_numeric_u32(u32(init.value), bit_length)

        elif isinstance(init, i64):
            ensure(
                init.value >= 0,
                'Implicit conversion from signed to unsigned'
            )
            return from_numeric_u64(u64(init.value), bit_length)

        elif isinstance(init, f32):
            return from_numeric_f32(init, bit_length)

        elif isinstance(init, f64):
            return from_numeric_f64(init, bit_length)

        else:
            raise MemException('Invalid initializer')

    def __eq__(self, that):
        "Can compare against integers and anything else that converts to int()."
        if isinstance(that, type(self)):
            return self.rgn.bytes == that.rgn.bytes
        elif hasattr(that, '__int__'):
            return int(self) == int(that)
        else:
            raise MemException(
                f'Cannot compare unlike types: {type(self)} and {type(that)}'
            )

    def __add__(self, other: Union[int, 'Signed']) -> 'Signed':
        """
        Converts self and other to signed integers, sums them, and returns it.

        Memory region is interpreted as a semantically meaningful numeric
        quantity. Concatenation is no longer the most intuitive operation to
        perform when dealing with signed numbers, especially with twos
        complement encoding. Raises an exception if the new quantity can't fit
        in self's bit length.
        """
        a, b = int(self), int(other)
        res = int(a + b)
        try:
            return type(self)(res)
        except MemException as e:
            msg = f'Overflow/Underflow with {a} + {b} = {res}: {e}'
            raise MemException(msg) from e

    def __sub__(self, other: Union[int, 'Signed']) -> 'Signed':
        """
        Converts self and other to signed integers, subtracts them, and returns
        the result.

        Memory region is interpreted as a semantically meaningful numeric
        quantity. Raises an exception if the new quantity can't fit
        in self's bit length.
        """
        a, b = int(self), int(other)
        res = int(a - b)
        try:
            return type(self)(res)
        except MemException as e:
            msg = f'Overflow/Underflow with {a} - {b} = {res}: {e}'
            raise MemException(msg) from e

    def __mul__(self, other: Union[int, 'Signed']) -> 'Signed':
        """
        Converts self and other to signed integers, multiplies them, and returns
        the result.

        Memory region is interpreted as a semantically meaningful numeric
        quantity. Raises an exception if the new quantity can't fit
        in self's bit length.
        """
        a, b = int(self), int(other)
        res = int(a * b)
        try:
            return type(self)(res)
        except MemException as e:
            msg = f'Overflow/Underflow with {a} * {b} = {res}: {e}'
            raise MemException(msg) from e

    def __truediv__(self, other: Union[int, 'Signed']) -> 'Signed':
        """
        Converts self and other to signed integers, divides them, and returns
        the result.

        Memory region is interpreted as a semantically meaningful numeric
        quantity. Raises an exception if the new quantity can't fit
        in self's bit length.
        """
        a, b = int(self), int(other)
        res = int(a / b)
        return type(self)(res)


class Signed(Unsigned):
    """
    Semantically meaningful data representing numeric information. Input types
    are constrained since the output concept is a quantity and not raw memory.
    Supports positive and negative integers.

    The overall process for negative numbers is:
        - Interpret the entire memory region as an unsigned integer (it's
            the negative number stored in two's complement encoding)
        - Subtract 1 from that value but left-pad with zeroes (to preserve
            bit length) to get the one's complement
        - Invert all those bits to get the positive number
        - Negate that value and return it

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

    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Signed':
        if isinstance(init, cls):  # Copy constructors
            out = MemRgn()
            init.validate()
            out.bytes = copy.copy(init.rgn.bytes)
            return out

        elif isinstance(init, type(None)):
            if bit_length is None:
                return MemRgn()
            else:
                rgn = MemRgn()
                rgn.bytes = group_bits_into_bytes([0] * bit_length)
                return rgn

        elif isinstance(init, int):
            return from_numeric_big_integer_signed(init, bit_length)

        elif isinstance(init, float):
            return from_numeric_float(init, bit_length)

        elif isinstance(init, bool):
            return from_bool(init)

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
            codec = from_numeric_big_integer_signed
            if init and init.startswith(('0x', '0X')):
                return codec(int(init, base=16), bit_length)
            elif init and init.startswith(('0b', '0B')):
                return codec(int(init, base=2), bit_length)
            return from_bytes(init.encode(), bit_length)

        elif isinstance(init, tuple):
            return from_bytes(init)

        elif isinstance(init, u8):
            try:
                return from_numeric_i8(i8(init.value), bit_length)
            except MemException as e:
                lo, hi = range_signed(bit_length)
                # err = MemException(
                #     f'{type(init).__name__} type casted to i8 would under/'
                #     f'overflow: {init.value} not in {lo} .. {hi} ({e})'
                # )
                # raise err.with_traceback(e.__traceback__)
                err = UnderOverflowException(type(init), i8, init.value, lo, hi)
                raise err from e

        elif isinstance(init, u16):
            try:
                return from_numeric_i16(i16(init.value), bit_length)
            except MemException as e:
                lo, hi = range_signed(bit_length)
                # err = MemException(
                #     f'{type(init).__name__} type casted to i16 would under/'
                #     f'overflow: {init.value} not in {lo} .. {hi} ({e})'
                # )
                # raise err.with_traceback(e.__traceback__)
                err = UnderOverflowException(
                    *(type(init), i16, init.value, lo, hi)
                )
                raise err from e

        elif isinstance(init, u32):
            try:
                return from_numeric_i32(i32(init.value), bit_length)
            except MemException as e:
                lo, hi = range_signed(bit_length)
                # err = MemException(
                #     f'{type(init).__name__} type casted to i32 would under/'
                #     f'overflow: {init.value} not in {lo} .. {hi} ({e})'
                # )
                # raise err.with_traceback(e.__traceback__)
                err = UnderOverflowException(
                    *(type(init), i32, init.value, lo, hi)
                )
                raise err from e

        elif isinstance(init, u64):
            try:
                return from_numeric_i64(i64(init.value), bit_length)
            except MemException as e:
                lo, hi = range_signed(bit_length)
                # err = MemException(
                #     f'{type(init).__name__} type casted to i64 would under/'
                #     f'overflow: {init.value} not in {lo} .. {hi} ({e})'
                # )
                # raise err.with_traceback(e.__traceback__)
                err = UnderOverflowException(
                    *(type(init), i64, init.value, lo, hi)
                )
                raise err from e

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

    def __eq__(self, that):
        "Can compare against integers and anything else that converts to int()."
        if isinstance(that, type(self)):
            return self.rgn.bytes == that.rgn.bytes
        elif hasattr(that, '__int__'):
            return int(self) == int(that)
        else:
            raise MemException(
                f'Cannot compare unlike types: {type(self)} and {type(that)}'
            )

    def __int__(self):
        return into_numeric_big_integer(self.rgn)


class Str(Mem):
    """
    Semantically meaningful data representing a array of UTF8 code points. Not
    distinct from an array of unsigned 8 bit integers. Input types are
    constrained since the output concept is the logical notion of string rather
    than raw memory.
    """

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

    def into(self, target_type: type) -> Generic[T]:
        if target_type == u8:
            return into_natural_big_integer(self.rgn)

    def __str__(self):
        chars = (int(byte, base=2) for byte in Mem.__str__(self).split())
        return bytearray(chars).decode()
