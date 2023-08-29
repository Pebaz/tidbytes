import ctypes
from enum import Enum, auto
from typing import Union, List


class MemException(Exception):
    "Used instead of assertion failures to give better error messages"


def ensure(condition: bool, message=''):
    # TODO(pbz): In the same way that Vulkan has valid usage checks, it would be
    # TODO(pbz): amazing to do the same by registering the function name and the
    # TODO(pbz): check in a table and displaying it in docs. I think this can
    # TODO(pbz): make sense because the fundamental operations are the system.
    # TODO(pbz): The higher level layer is just built on top of it.
    # https://registry.khronos.org/vulkan/specs/1.2-extensions/html/chap12.html#VUID-VkBufferCreateInfo-size-00912

    if not condition:
        raise MemException(message)


class Order(Enum):
    LeftToRight = auto()  # First element is on far left
    RightToLeft = auto()  # First element is on far right


L2R = Order.LeftToRight
R2L = Order.RightToLeft


u8 = ctypes.c_ubyte
u16 = ctypes.c_uint16
u32 = ctypes.c_uint32
u64 = ctypes.c_uint64
i8 = ctypes.c_byte
i16 = ctypes.c_int16
i32 = ctypes.c_int32
i64 = ctypes.c_int64
f32 = ctypes.c_float
f64 = ctypes.c_double

BitList = List[int]
ByteList = List[int | u8]
PrimitiveInt = int | u8 | u16 | u32 | u64 | i8 | i16 | i32 | i64
PrimitiveFloat = float | f32 | f64
Primitive = PrimitiveInt | PrimitiveFloat | BitList | ByteList
