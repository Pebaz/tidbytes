# From

# Into

# TODO(pbz): Both C language codec functions and also Python

# ! Codecs can never start with `op_` since that would mean they are part of an
# ! algebra. This is fine, but they are not compatible with the Von Neumann API.


from_u8 = ...
from_int = ...
from_str = ...
from_struct = ...


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
