import ctypes
from enum import Enum, auto


class MemException(Exception):
    "Used instead of assertion failures to give better error messages"


# TODO(pbz): Create exception heirarchy after analyzing codebase
class UnderOverFlowException(MemException):
    def __init__(self, in_type: type, out_type: type, value, lo, hi):
        super().__init__(self)
        self.msg = (
            f'{in_type.__name__} type casted to {out_type.__name__} would under/overflow: '
            f'{value} not in {lo} .. {hi}'
        )
    def __str__(self):
        return self.msg


def ensure(condition: bool, message=''):
    if not condition:
        raise MemException(message)


class Order(Enum):
    LeftToRight = auto()  # First element is on far left
    RightToLeft = auto()  # First element is on far right


L2R = Order.LeftToRight
R2L = Order.RightToLeft


def def_class(type_name, superclass, low, hi):
    """
    Ensures that ctypes cannot be created with values that will be interpreted
    as a numeric range underflow or overflow.
    """
    return type(
        type_name,
        (superclass,),
        dict(
            __init__=lambda self, value: (
                ensure(value >= low, f'{type_name} underflow: {value} < {low}'),
                ensure(value <= hi, f'{type_name} overflow: {value} > {hi}'),
                superclass.__init__(self, value),
            )[-1],
            __repr__=lambda self: f'{superclass.__name__}({self.value})',
            __str__=lambda self: str(self.value),
            lo=low,
            hi=hi,
        )
    )

u8 = def_class('u8', ctypes.c_ubyte, 0, 255)
u16 = def_class('u16', ctypes.c_uint16, 0, 65535)
u32 = def_class('u32', ctypes.c_uint32, 0, 4294967295)
u64 = def_class('u64', ctypes.c_uint64, 0, 18446744073709551615)
i8 = def_class('i8', ctypes.c_byte, -128, 127)
i16 = def_class('i16', ctypes.c_int16, -32768, 32767)
i32 = def_class('i32', ctypes.c_int32, -2147483648, 2147483647)
i64 = def_class(
    *('i64', ctypes.c_int64, -9223372036854775808, 9223372036854775807)
)
f32 = ctypes.c_float
f64 = ctypes.c_double
