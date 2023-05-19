import math
from .mem_types import *
from enum import Enum, auto


class MemRgn:
    """
    Von Neumann root backing store type for bits. Language specific.

    Assumes bytes are always length of 8, filling empty spaces with None.
    """
    def __init__(self):
        self.bytes = []  # List of lists of integer bits


def op_transform(mem: MemRgn, bit_order: Order, byte_order: Order):
    byte_direction = iter if byte_order == Order.LeftToRight else reversed
    bit_direction = iter if bit_order == Order.LeftToRight else reversed

    return [
        [bit for bit in bit_direction(byte)]
        for byte in byte_direction(mem.bytes)
    ]


def op_reverse(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.RightToLeft)


def op_reverse_bytes(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.LeftToRight)


def op_reverse_bits(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.RightToLeft)


def op_identity(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.LeftToRight)
