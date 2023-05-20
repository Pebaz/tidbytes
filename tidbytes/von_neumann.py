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


def op_ensure_bit_length(): ...
def op_ensure_byte_length(): ...
def op_concatenate(): ...
def op_extend(mem: MemRgn, amount: int, direction: Order, fill: int) -> None:
    "Fill the left or right side with the following bit value of 0 or 1."

# TODO(pbz): Idiomatic interface:
def repr_byte(mem: MemRgn): ...
def repr_byte_in_universe(mem: MemRgn, bit_order: Order, byte_order: Order): ...


# ------------------------------------------------------------------------------
# Memory transformation operations to map memory from another universe into the
# universe of the host system of the running application or back the other way.
# They are generally used as transitions between memory universe boundaries.
# This bit and byte order system is scalable in that mixed-endian byte order can
# also be added as a universe boundary. All memory is eventually mapped to
# identity order which is left to right bit and byte order.
# ------------------------------------------------------------------------------
# TODO(pbz): Call validate_memory() each time?
def op_transform(mem: MemRgn, bit_order: Order, byte_order: Order):
    byte_direction = iter if byte_order == Order.LeftToRight else reversed
    bit_direction = iter if bit_order == Order.LeftToRight else reversed

    return [
        [bit for bit in bit_direction(byte)]
        for byte in byte_direction(mem.bytes)
    ]


# TODO(pbz): Call validate_memory() each time?
def op_reverse(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.RightToLeft)


# TODO(pbz): Call validate_memory() each time?
def op_reverse_bytes(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.LeftToRight)


# TODO(pbz): Call validate_memory() each time?
def op_reverse_bits(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.RightToLeft)


# TODO(pbz): Call validate_memory() each time?
def op_identity(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.LeftToRight)


# ------------------------------------------------------------------------------
# Host language specific meta operations for memory regions
# ------------------------------------------------------------------------------

# TODO(pbz): Call validate_memory() each time?
def op_bit_length(mem: MemRgn) -> int:
    """
    The number of used bits in the memory region.

    Does not count unset partial bits. For example, the bit length would be 9:
    [[0, 0, 0, 0, 0, 0, 0, 0], [0, None, None, None, None, None, None, None]]
    """
    index_counter = 0
    for byte in mem.bytes:
        for bit in byte:
            if bit != None:
                index_counter += 1
    return index_counter


# TODO(pbz): Call validate_memory() each time?
def op_byte_length(mem: MemRgn) -> int:
    """
    The number of bytes necessary to contain the bits in the memory region.

    Relies on the assumption that `MemRgn` always stores a multiple of 8 bits.
    """
    return len(mem.bytes)


# ------------------------------------------------------------------------------
# Fundamental memory read and write operations
# ------------------------------------------------------------------------------
# TODO(pbz): Call validate_memory() each time?
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


# TODO(pbz): Call validate_memory() each time?
def op_get_byte(mem: MemRgn, index: int) -> MemRgn:
    """
    Invariant: input memory region must be mapped to the program's universe.

    Note: Returned byte can be partial depending on byte order if on far side.

    Partial bytes are handled by returning them since the input memory is
    already in the host CPU's memory universe. This makes sense because the only
    way a partial byte would be undefined is if the bit or byte order was
    unknown.
    """
    ensure(0 <= index < op_byte_length(mem), f'Index out of bounds: {index}')

    out = MemRgn()
    out.bytes.append(mem.bytes[index][:])
    return out


# TODO(pbz): Call validate_memory() each time?
def op_get_bits(mem: MemRgn, start: int, stop: int) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    # TODO(pbz): I'm fairly certain this needs to be `stop < op_bit_length(mem)`
    # TODO(pbz): since I think it should be an exclusive range? Empty ranges?
    ensure(0 <= start <= stop <= op_bit_length(mem), 'Index out of bounds')

    out = MemRgn()
    for byte in mem.bytes:
        out_byte = []
        for bit in byte:
            if bit != None:
                out_byte.append(bit)
                if len(out_byte) == 8:
                    out.bytes.append(out_byte[:])
                    out_byte.clear()
        if out_byte:
            out.bytes.append(out_byte[:])
    return out


# TODO(pbz): Call validate_memory() each time?
def op_get_bytes(mem: MemRgn, start: int, stop: int) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    ensure(
        0 <= start * 8 <= stop * 8 <= op_byte_length(mem),
        'Index out of bounds'
    )

    start_index = start * 8
    stop_index = start * 8
    out = MemRgn()

    for index in range(start_index, stop_index):
        out.bytes.append(op_get_byte(index).bytes[0])

    return out


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_bit(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    ensure(op_bit_length(payload) == 1, 'More than one bit supplied')
    ensure(0 <= offset < op_bit_length(mem), 'Offset out of bounds')

    out = MemRgn()
    index_counter = 0
    for byte in mem.bytes:
        out_byte = []
        for bit in byte:
            if index_counter == offset:
                out_byte.append(payload.bytes[0][0])
            else:
                out_byte.append(bit)

            if len(out_byte) == 8:
                out.bytes.append(out_byte[:])
                out_byte.clear()

            index_counter += 1
        if out_byte:
            out.bytes.append(out_byte[:])
    return out


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_bits(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    mem_len = op_bit_length(mem)
    ending_index = offset + op_bit_length(payload)
    ensure(0 <= offset < mem_len, 'Offset out of bounds')
    ensure(
        ending_index <= mem_len,
        f"Payload can't fit: bit offset ({offset}) with length "
        f"({op_bit_length(payload)}) is too big for space left after offset "
        f"({mem_len - offset})"
    )

    out = MemRgn()
    index_counter = 0
    for byte in mem.bytes:
        out_byte = []
        for bit in byte:
            if bit != None:
                if offset <= index_counter < ending_index:
                    out_byte.append(op_get_bit(payload, index_counter))
                else:
                    out_byte.append(bit)

                if len(out_byte) == 8:
                    out.bytes.append(out_byte[:])
                    out_byte.clear()

                index_counter += 1
        if out_byte:
            out.bytes.append(out_byte[:])
    return out


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_byte(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    payload_bits = op_bit_length(payload)
    ensure(payload_bits <= 8, f'Bit count greater than 8: {payload_bits}')
    ensure(
        0 <= offset * 8 <= offset * 8 + payload_bits < op_bit_length(mem),
        "Payload byte doesn't fit within destination"
    )

    return op_set_bits(mem, offset * 8, payload)

# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Assumes exact bit length of payload should fit in dest. Concat?
# TODO(pbz): Call validate_memory() each time?
def op_set_bytes(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory region must be mapped to the program's universe."
    payload_bits = op_bit_length(payload)
    ensure(
        0 <= offset * 8 <= offset * 8 + payload_bits < op_bit_length(mem),
        "Payload byte doesn't fit within destination"
    )

    return op_set_bits(mem, offset * 8, payload)
