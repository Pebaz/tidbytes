import math
from .mem_types import *
from enum import Enum, auto

# ! ----------------------------------------------------------------------------
# ! Von Neumann API
# ! ----------------------------------------------------------------------------

# * Getting Bits/Bytes

# TODO(pbz): Should this support "slice out" directions also? Like dest_byte_ord


"""
[5/6/23] Ok, gotta do another redesign but I don't have the time to make this
more official:

All bit and byte operations are memory transformations.
They map memory from one universe into another universe.
For this reason, both an input bit & byte order and an output bit & byte order
are necessary in order to work with memory precisely. Furthermore, in the
previous design, `op_get_bytes()` accidentally assumed an output bit & byte
order of left to right! This is highly significant because that might not even
match the bit and byte order of the system the code is running on! This means
that both an input and an output bit & byte order are semantically required.
I think this expresses it: "transformation" means "change formation".
"""


REV = slice(None, None, -1)  # Usage: iterable[REV] == [*reversed(iterable)]


def rslice(start: int, stop: int, length: int) -> slice:
    "Reverse slice with exclusive stop index."
    return slice(length - stop, length - start)


def op_get_bit(
    mem: Mem,
    index: int,
    bit_order: Order,
    byte_order: Order
) -> Mem:
    """
    Create a copy of the bits of a memory slice as a new slice.

    Negative indices not allowed (how would wrapping at byte boundaries work?).

    Needs to care about byte order because numeric data reads from right to left
    for bits and can be either left or right for bytes depending on endianness.
    """
    ensure(0 <= index < op_bit_length(mem), 'Index out of bounds')

    # TODO(pbz): Yeah no gotta have a standard way of doing this per operation
    each_byte = []
    indices = range(op_byte_length(mem))
    indices = reversed(indices) if byte_order == Order.RightToLeft else indices

    for i in indices:
        if byte_order == Order.LeftToRight:
            bit_slice = slice(i * 8, (i + 1) * 8)
        else:
            bit_slice = rslice(i * 8, (i + 1) * 8, op_bit_length(mem))

        if bit_order == Order.LeftToRight:
            byte = mem.bits[bit_slice]
        else:
            byte = mem.bits[bit_slice][REV]

        each_byte.append(byte)

    bits = []
    for byte in each_byte:
        bits.extend(byte)
    bits = [bits[index]]

    new = Mem()
    new.bits = bits
    return new


def op_get_byte(
    mem: Mem,
    index: int,
    bit_order: Order,
    byte_order: Order
) -> Mem:
    """
    Create a copy of the bytes of a memory slice as a new slice.

    Negative indices not allowed (how would wrapping at byte boundaries work?).
    """
    # * Doesn't need to care about byte order since bytes are bytes in both dirs
    ensure(0 <= index < op_byte_length(mem), 'Index out of bounds')

    bits = []
    for i in range(min(op_bit_length(mem) - index * 8, 8)):
        bits.extend(op_get_bit(mem, index * 8 + i, bit_order, byte_order).bits)

    # base = mem.bits if bit_order == Order.LeftToRight else [*reversed(mem.bits)]
    # bits = base[index * 8:index * 8 + 8]

    new = Mem()
    new.bits = bits
    return new


def op_get_bits(mem: Mem, start: int, stop: int, bit_order: Order) -> Mem:
    """
    Create a copy of the bits of a memory slice as a new slice.

    Negative indices not allowed (how would wrapping at byte boundaries work?).

    The stop index is exclusive.
    """
    # * Doesn't need to care about byte order since bits are bits in both dirs
    ensure(0 <= start <= stop <= op_bit_length(mem), 'Index out of bounds')

    index = slice(start, stop)
    base = mem.bits if bit_order == Order.LeftToRight else [*reversed(mem.bits)]
    bits = base[index]

    new = Mem()
    new.bits = bits
    return new


def op_get_bytes(mem: Mem, start: int, stop: int, byte_order: Order) -> Mem:
    """
    Create a copy of the bytes of a memory slice as a new slice.

    Negative indices not allowed to be consistent with bit indexing.

    Note that if the memory uses 13 bits and 2 bytes worth of data are sliced,
    no extra padding bits are added to the output slice. Conversion functions
    can implement this per output type (u32, array of u8, etc.).

    The stop index is exclusive.
    """
    # * Doesn't need to care about bit order since bytes are bytes in both dirs
    ensure(0 <= start <= stop <= op_byte_length(mem), 'Index out of bounds')

    index = slice(start * 8, stop * 8)

    if byte_order == Order.LeftToRight:
        base = mem.bits
    else:
        base = [*reversed(mem.bits)]

    bits = base[index]

    new = Mem()
    new.bits = bits
    return new


# * Setting Bits/Bytes

def op_set_bit(mem: Mem, offset: int, payload: Mem, bit_order: Order):
    ensure(op_bit_length(payload) == 1, 'More than one bit supplied')
    ensure(0 <= offset < op_bit_length(mem), 'Offset out of bounds')

    if bit_order == Order.LeftToRight:
        mem.bits[offset] = payload.bits[0]
    else:
        bits = [*reversed(mem.bits)]
        bits[offset] = payload.bits[0]
        mem.bits = [*reversed(bits)]


def op_set_byte(mem: Mem, offset: int, payload: Mem, byte_order: Order):
    """
    The byte order refers to the destination memory, not the payload.
    """
    bit_count = op_bit_length(payload)
    ensure(bit_count == 8, f'Bit count differed from 8: {bit_count}')
    op_set_bits(mem, offset * 8, payload, byte_order)


def op_set_bits(mem: Mem, offset: int, payload: Mem, bit_order: Order):
    "Set bits by reference."
    mem_len = op_bit_length(mem)
    ensure(0 <= offset < mem_len, 'Offset out of bounds')

    # TODO(pbz): I don't this this test case is getting hit
    ending_index = offset + op_bit_length(payload)

    ensure(
        ending_index <= mem_len,
        f"Payload can't fit: bit offset ({offset}) with length "
        f"({op_bit_length(payload)}) is too big for space left after offset "
        f"({mem_len - offset})"
    )

    index = slice(offset, ending_index)

    if bit_order == Order.LeftToRight:
        base = mem.bits
        base[index] = payload.bits
    else:
        base = [*reversed(mem.bits)]
        base[index] = payload.bits
        mem.bits = [*reversed(base)]


def op_set_bytes(mem: Mem, offset: int, payload: Mem, byte_order: Order):
    "Set bytes by reference."
    # ? Is this worth keeping separate?
    """
    byte_offset = offset * 8
    mem_len = op_bit_length(mem)
    ensure(0 <= byte_offset < mem_len, 'Offset out of bounds')

    ending_index = byte_offset + op_bit_length(payload)

    ensure(
        ending_index <= mem_len,
        f"Payload can't fit: bit offset ({byte_offset}) with length "
        f"({op_bit_length(payload)}) is too big for space left after offset "
        f"({mem_len - byte_offset})"
    )

    index = slice(byte_offset, ending_index)

    if byte_order == Order.LeftToRight:
        base = mem.bits
        base[index] = payload.bits
    else:
        base = [*reversed(mem.bits)]
        base[index] = payload.bits
        mem.bits = [*reversed(base)]
    """
    bit_count = op_bit_length(payload)
    ensure(bit_count % 8 == 0, f'Bit count not multiple of 2: {bit_count}')
    op_set_bits(mem, offset * 8, payload, byte_order)


# * Management Operations

# TODO(pbz): Test these too

def op_bit_length(mem: Mem) -> int:
    return len(mem.bits)

def op_byte_length(mem: Mem) -> int:
    "The number of bytes necessary to contain the bits in the memory region."
    return math.ceil(op_bit_length(mem) / 8)

def op_extend(mem: Mem, amount: int, direction: Order, fill: int) -> None:
    "Fill the left or right side with the following bit value of 0 or 1."
