import ctypes
from enum import Enum, auto


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
