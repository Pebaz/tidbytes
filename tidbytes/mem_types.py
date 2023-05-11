import ctypes
from enum import Enum, auto


class MemException(Exception):
    "Used instead of assertion failures to give better error messages"


def ensure(condition: bool, message=''):
    if not condition:
        raise MemException(message)


class Mem:
    "Von Neumann root backing store type for bits. Language specific."
    def __init__(self):
        self.bits = []


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
