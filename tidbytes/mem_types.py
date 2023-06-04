import ctypes
from enum import Enum, auto


class MemException(Exception):
    "Used instead of assertion failures to give better error messages"


def ensure(condition: bool, message=''):
    if not condition:
        raise MemException(message)


class Order(Enum):
    LeftToRight = auto()  # First element is on far left
    RightToLeft = auto()  # First element is on far right
