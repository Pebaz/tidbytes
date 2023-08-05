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
# universe of the host system of the running application or back the other way.
# They are generally used as transitions between memory universe boundaries.
# This bit and byte order system is scalable in that mixed-endian byte order can
# also be added as a universe boundary. All memory is eventually mapped to
# identity order which is left to right bit and byte order.
# ------------------------------------------------------------------------------
# TODO(pbz): Call validate_memory() each time?
def op_transform(mem: MemRgn, bit_order: Order, byte_order: Order) -> MemRgn:
    byte_direction = iter if byte_order == Order.LeftToRight else reversed
    bit_direction = iter if bit_order == Order.LeftToRight else reversed

    out = MemRgn()
    out.bytes = [
        [bit for bit in bit_direction(byte)]
        for byte in byte_direction(mem.bytes)
    ]

    return out


# TODO(pbz): Call validate_memory() each time?
def op_identity(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.LeftToRight)


# TODO(pbz): Call validate_memory() each time?
def op_reverse(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.RightToLeft)


# TODO(pbz): Call validate_memory() each time?
def op_reverse_bytes(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.RightToLeft, Order.LeftToRight)


# TODO(pbz): Call validate_memory() each time?
def op_reverse_bits(mem: MemRgn) -> MemRgn:
    return op_transform(mem, Order.LeftToRight, Order.RightToLeft)


# ------------------------------------------------------------------------------
# Host language specific meta operations for memory regions
# ------------------------------------------------------------------------------

# TODO(pbz): Call validate_memory() each time?
def iterate_logical_bits(mem: MemRgn):
    return (bit for byte in mem.bytes for bit in byte if bit != None)


def validate_memory(mem: MemRgn):
    ensure(
        all(len(byte) == 8 for byte in mem.bytes),
        f'Some bytes not 8 bits: {mem.bytes}'
    )
    ensure(
        all(all(i in {0, 1, None} for i in byte) for byte in mem.bytes),
        f'Some bytes do not contain 0, 1, or None: {mem.bytes}'
    )
    ensure(
        any(any(i in {0, 1} for i in byte) for byte in mem.bytes),
        f'No bits set: {mem.bytes}'
    )

    all_bits = list(iterate_logical_bits(mem))

    if len(all_bits) % 8 > 0:
        all_bits += [None] * (8 - len(all_bits) % 8)
    all_bytes = []
    while all_bits:
        all_bytes.append(all_bits[:8])
        all_bits = all_bits[8:]
    ensure(
        mem.bytes == all_bytes,
        (
            f'Some bytes contained unset bits in the middle: {mem.bytes}.'
            f'Should be: {all_bytes}'
        )
    )


# TODO(pbz): Call validate_memory() each time?
def op_bit_length(mem: MemRgn) -> int:
    """
    The number of used bits in the memory region.

    Does not count unset partial bits. For example, the bit length would be 9:
    [[0, 0, 0, 0, 0, 0, 0, 0], [0, None, None, None, None, None, None, None]]

    Invariant: input memory must be valid and mapped to program's universe.
    """
    return len(list(iterate_logical_bits(mem)))


# TODO(pbz): Call validate_memory() each time?
def op_byte_length(mem: MemRgn) -> int:
    """
    The number of bytes necessary to contain the bits in the memory region.

    Relies on the assumption that `MemRgn` always stores a multiple of 8 bits.

    Invariant: input memory must be valid and mapped to program's universe.
    """
    return len(mem.bytes)


# ------------------------------------------------------------------------------
# Fundamental memory read and write operations
# ------------------------------------------------------------------------------
# TODO(pbz): Call validate_memory() each time?
def op_get_bit(mem: MemRgn, index: int) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    ensure(0 <= index < op_bit_length(mem), f'Index out of bounds: {index}')

    return op_get_bits(mem, index, index + 1)


# TODO(pbz): Call validate_memory() each time?
def op_get_byte(mem: MemRgn, index: int) -> MemRgn:
    """
    Invariant: input memory must be valid and mapped to program's universe.

    Note: Returned byte can be partial depending on byte order if on far side.

    Partial bytes are handled by returning them since the input memory is
    already in the host CPU's memory universe. This makes sense because the only
    way a partial byte would be undefined is if the bit or byte order was
    unknown.

    Memory can always be addressed with byte indices. However, over-fetching is
    handled by truncating the returned bits to the bit length of the source
    memory. If 2 bytes is fetched from a 15 bit region, only 15 bits will be
    returned but it will not error out since bits aren't addressable.
    """
    mem_bits = op_bit_length(mem)
    ensure(0 <= index < mem_bits, f'Index out of bounds: {index}')

    return op_get_bits(mem, index * 8, min(index * 8 + 8, mem_bits))


# TODO(pbz): Call validate_memory() each time?
def op_get_bits(mem: MemRgn, start: int, stop: int) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    # TODO(pbz): I'm fairly certain this needs to be `stop < op_bit_length(mem)`
    # TODO(pbz): since I think it should be an exclusive range? Empty ranges?
    ensure(0 <= start <= stop <= op_bit_length(mem), 'Index out of bounds')

    out = MemRgn()
    index_counter = 0
    for byte in mem.bytes:
        out_byte = []
        for bit in byte:
            if start <= index_counter < stop:
                out_byte.append(bit)

            if len(out_byte) == 8:
                out.bytes.append(out_byte[:])
                out_byte.clear()

            index_counter += 1
        if out_byte:
            out.bytes.append(out_byte[:])

    if out.bytes and len(out.bytes[-1]) < 8:
        out.bytes[-1] = (out.bytes[-1] + [None] * 8)[:8]

    return out


# TODO(pbz): Call validate_memory() each time?
def op_get_bytes(mem: MemRgn, start: int, stop: int) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    ensure(
        0 <= start <= stop <= op_byte_length(mem),
        'Index out of bounds'
    )

    return op_get_bits(mem, start * 8, stop * 8)


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_bit(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    ensure(op_bit_length(payload) == 1, 'More than one bit supplied')
    ensure(0 <= offset < op_bit_length(mem), 'Offset out of bounds')

    return op_set_bits(mem, offset, payload)


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_bits(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
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
            if offset <= index_counter < ending_index:
                bit = op_get_bit(payload, index_counter - offset).bytes[0][0]
                out_byte.append(bit)
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
    "Invariant: input memory must be valid and mapped to program's universe."
    payload_bits = op_bit_length(payload)
    ensure(payload_bits <= 8, f'Bit count greater than 8: {payload_bits}')
    ensure(
        0 <= offset * 8 < op_bit_length(mem),
        f"Offset out of bounds: {op_bit_length(mem)=}, {offset=}"
    )
    ensure(
        op_bit_length(mem) - offset * 8 + payload_bits >= 0,
        f"Payload byte doesn't fit within destination: "
        f"{op_bit_length(mem)=}, {offset=}, {op_bit_length(payload)=}"
    )

    return op_set_bits(mem, offset * 8, payload)


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_set_bytes(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    """
    Assumes exact bit length of payload should fit in destination. Does not
    concatenate the bits that don't fit from the payload. The payload is
    expected to be smaller than or equal to the memory region (plus offset * 8).

    Invariant: input memory must be valid and mapped to program's universe.
    """
    payload_bits = op_bit_length(payload)
    ensure(
        0 <= offset * 8 <= offset * 8 + payload_bits <= op_bit_length(mem),
        f"Payload byte doesn't fit within destination: "
        f"{op_bit_length(mem)=}, {offset=}, {payload_bits=}"
    )

    return op_set_bits(mem, offset * 8, payload)


# ------------------------------------------------------------------------------
# Memory transformation operations for memory within the program's universe.
# ------------------------------------------------------------------------------

# TODO(pbz): Need these?
def op_fill(): ...
def op_fill_range(): ...

# ??????????????????????????????????????????????????????????????????????????????
# TODO(pbz): I don't think it should be pass by reference because arithmetic is
# TODO(pbz): pass by value
# ??????????????????????????????????????????????????????????????????????????????

# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_truncate(mem: MemRgn, length: int) -> MemRgn:
    "Truncates a memory region to be shorter or equal bit length."
    mem_len = op_bit_length(mem)
    ensure(
        length <= mem_len,
        f'Truncated length ({length}) is longer than region size ({mem_len}). '
        f'Use `{op_extend.__name__}` or `{op_ensure_bit_length.__name__}` '
        f'instead'
    )

    bits = [bit for byte in mem.bytes for bit in byte][:length]
    out = MemRgn()
    byte = []

    for i, bit in enumerate(bits):
        if byte and i % 8 == 0:
            out.bytes.append(byte[:])
            byte.clear()
        byte.append(bit)
    out.bytes.append((byte + [None] * 8)[:8])

    return out


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_extend(mem: MemRgn, amount: int, fill: MemRgn) -> MemRgn:
    "Extends a memory region with 0 or 1 to a given bit length."
    mem_len = op_bit_length(fill)
    ensure(mem_len == 1, 'Fill payload must be 0 or 1')

    length = mem_len + amount
    bits = [bit for byte in mem.bytes for bit in byte] + [0] * length - mem_len
    out = MemRgn()
    byte = []

    for i, bit in enumerate(bits):
        if byte and i % 8 == 0:
            out.bytes.append(byte[:])
            byte.clear()
        byte.append(bit)
    out.bytes.append((byte + [None] * 8)[:8])

    return out


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_ensure_bit_length(mem: MemRgn, length: int) -> MemRgn:
    "Extends with zeros or truncates a memory region to be a specific length."
    mem_len = op_bit_length(mem)

    # ensure(
    #     mem_len <= length,
    #     f'Cannot truncate bits from {mem_len} to {length}'
    # )

    if mem_len > length:
        return op_truncate(mem, length)

    elif mem_len < length:
        fill = MemRgn()
        fill.bytes.append([0] + [None] * 7)

        return op_extend(
            mem,
            mem_len - length,
            fill
        )

    else:
        return mem


# TODO(pbz): Should this be pass by reference?
# TODO(pbz): Call validate_memory() each time?
def op_ensure_byte_length(mem: MemRgn, length: int) -> MemRgn:
    "Extends with zeros or truncates a memory region to be a specific length."
    mem_len = op_bit_length(mem)
    ensure(
        mem_len <= length * 8,
        f'Cannot truncate bits from {mem_len} to {length * 8}'
    )
    return op_ensure_bit_length(mem, length * 8)


# TODO(pbz): Call validate_memory() each time?
def op_concatenate(mem_left: MemRgn, mem_right: MemRgn) -> MemRgn:
    """
    Invariant: memory regions should be from the same universe and valid.
    """
    # TODO(pbz): Call validate_memory() each time?
    validate_memory(mem_left)
    validate_memory(mem_right)

    bits = [
        bit for region in [mem_left, mem_right]
        for byte in region.bytes
        for bit in byte if bit is not None
    ]

    out = MemRgn()
    byte = []

    for i, bit in enumerate(bits):
        if byte and i % 8 == 0:
            out.bytes.append(byte[:])
            byte.clear()
        byte.append(bit)
    out.bytes.append((byte + [None] * 8)[:8])

    validate_memory(out)

    return out
