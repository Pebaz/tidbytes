import math
from .mem_types import *
from enum import Enum, auto


class MemRgn:
    """
    Von Neumann root backing store type for bits. Language specific.

    Assumes bytes are always length of 8, filling empty spaces with None.
    """
    # TODO(pbz): Since all memory operations should assume the memory region is
    # TODO(pbz): mapped into the host CPU's universe, I should be able to
    # TODO(pbz): re-implement `MemRgn` using integers and bit masks.
    # TODO(pbz): Over-fetching partial bytes are well-defined so a bit mask will
    # TODO(pbz): ignore extra bits.
    def __init__(self):
        self.bytes: list[list[int]] = []


# ------------------------------------------------------------------------------
# Memory transformation operations to map memory from another universe into the
# universe of the host system of the running application or back the other way
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Host language specific meta operations for memory regions
# ------------------------------------------------------------------------------

def op_bit_length(mem: MemRgn) -> int:
    index_counter = 0
    for byte in mem.bytes:
        for bit in byte:
            if bit != None:
                index_counter += 1
    return index_counter


def op_byte_length(mem: MemRgn) -> int:
    "Relies on the assumption that `MemRgn` always stores a multiple of 8 bits."
    return len(mem.bytes)


# ------------------------------------------------------------------------------
# Fundamental memory read and write operations
# ------------------------------------------------------------------------------
def op_get_bit(mem: MemRgn, index: int) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    ensure(0 <= index < op_bit_length(mem), f'Index out of bounds: {index}')

    out = MemRgn()
    index_counter = 0
    for byte in mem.bytes:
        for bit in byte:
            if bit != None:
                if index_counter == index:
                    out.bytes = [[bit] + [None] * 7]
                    return out
                index_counter += 1
    assert False, 'Unreachable'


def op_get_byte(mem: MemRgn, index: int) -> MemRgn:
    """
    Invariant: input memory region must be mapped to the program's universe.

    Partial bytes are handled by returning them since the input memory is
    already in the host CPU's memory universe. This makes sense because the only
    way a partial byte would be undefined is if the bit or byte order was
    unknown.
    """
    ensure(0 <= index < op_byte_length(mem), f'Index out of bounds: {index}')

    out = MemRgn()
    out.bytes.append(mem.bytes[index][:])
    return out


def op_get_bits(mem: MemRgn, start: int, stop: int) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    ensure(0 <= start <= stop <= op_bit_length(mem), 'Index out of bounds')

    # TODO(pbz): left off here 😁
