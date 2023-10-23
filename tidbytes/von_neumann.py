from .mem_types import Order, L2R, R2L, ensure

# TODO(pbz): Rename von_neumann to natural

# Putting this first and foremost to declare the opportunity to refactor all
# operations to use a more efficient backing store for bits and bytes. One idea
# is to use actual bytes, although there may still be better options. Rust
# BitVec?
LogicalMemory = list[list[int]]


class MemRgn:
    """
    Von Neumann root backing store type for bits. Language specific.

    Assumes bytes are always length of 8, filling empty spaces with None.
    """
    # Since all memory operations should assume the memory region is mapped into
    # the host CPU's universe, I should be able to re-implement `MemRgn` using
    # integers and bit masks. Over-fetching partial bytes are well-defined so a
    # bit mask will ignore extra bits.
    def __init__(self):
        self.bytes: LogicalMemory = []


# ------------------------------------------------------------------------------
# Memory transformation operations to map memory from another universe into the
# universe of the host system of the running application or back the other way.
# They are generally used as transitions between memory universe boundaries.
# This bit and byte order system is scalable in that mixed-endian byte order can
# also be added as a universe boundary. All memory is eventually mapped to
# identity order which is left to right bit and byte order.
# ------------------------------------------------------------------------------
def op_transform(mem: MemRgn, *, bit_order: Order, byte_order: Order) -> MemRgn:
    contract_validate_memory(mem)

    if not mem.bytes:  # Handle null
        return mem

    bit_direction = iter if bit_order == L2R else reversed
    byte_direction = iter if byte_order == L2R else reversed

    transformed_bytes = [
        [bit for bit in bit_direction(byte)]
        for byte in byte_direction(mem.bytes)
    ]

    # Slide down if reversed and regroup into bytes
    out = MemRgn()
    out.bytes = group_bits_into_bytes(iterate_logical_bits(transformed_bytes))

    contract_validate_memory(out)
    return out


def op_identity(mem: MemRgn) -> MemRgn:
    "Maps a memory region to itself."
    contract_validate_memory(mem)
    return op_transform(mem, bit_order=L2R, byte_order=L2R)


def op_reverse(mem: MemRgn) -> MemRgn:
    "Reverse both the bits and bytes for a full reversal."
    contract_validate_memory(mem)
    return op_transform(mem, bit_order=R2L, byte_order=R2L)


def op_reverse_bytes(mem: MemRgn) -> MemRgn:
    "Reverse the bytes but maintain bit order."
    contract_validate_memory(mem)
    return op_transform(mem, bit_order=L2R, byte_order=R2L)


def op_reverse_bits(mem: MemRgn) -> MemRgn:
    "Reverse the bits in every byte but maintain byte order."
    contract_validate_memory(mem)
    return op_transform(mem, bit_order=R2L, byte_order=L2R)


# ------------------------------------------------------------------------------
# Fundamental memory read and write operations
# ------------------------------------------------------------------------------
def op_get_bit(mem: MemRgn, index: int) -> MemRgn:
    """
    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    ensure(0 <= index < meta_op_bit_length(mem), f'Index out of bounds: {index}')

    out = op_get_bits(mem, index, index + 1)
    return contract_validate_memory(out)


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
    contract_validate_memory(mem)
    mem_bits = meta_op_bit_length(mem)
    ensure(0 <= index < mem_bits, f'Index out of bounds: {index}')

    out = op_get_bits(mem, index * 8, min(index * 8 + 8, mem_bits))
    return contract_validate_memory(out)


def op_get_bits(mem: MemRgn, start: int, stop: int) -> MemRgn:
    """
    Exclusive index.

    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    ensure(0 <= start <= stop <= meta_op_bit_length(mem), 'Index out of bounds')

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

    return contract_validate_memory(out)


def op_get_bytes(mem: MemRgn, start: int, stop: int) -> MemRgn:
    """
    Exclusive index.

    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    print('💡', start, stop, meta_op_byte_length(mem))
    ensure(
        0 <= start <= stop <= meta_op_byte_length(mem),
        'Index out of bounds'
    )

    out = op_get_bits(mem, start * 8, stop * 8)
    return contract_validate_memory(out)


def op_set_bit(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    contract_validate_memory(mem)
    ensure(meta_op_bit_length(payload) == 1, 'More than one bit supplied')
    ensure(0 <= offset < meta_op_bit_length(mem), 'Offset out of bounds')

    out = op_set_bits(mem, offset, payload)
    return contract_validate_memory(out)


def op_set_bits(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    contract_validate_memory(mem)
    mem_len = meta_op_bit_length(mem)
    ending_index = offset + meta_op_bit_length(payload)
    ensure(0 <= offset < mem_len, 'Offset out of bounds')
    ensure(
        ending_index <= mem_len,
        f"Payload can't fit: bit offset ({offset}) with length "
        f"({meta_op_bit_length(payload)}) is too big for space left after offset "
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

    return contract_validate_memory(out)


def op_set_byte(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    "Invariant: input memory must be valid and mapped to program's universe."
    contract_validate_memory(mem)
    payload_bits = meta_op_bit_length(payload)
    ensure(payload_bits <= 8, f'Bit count greater than 8: {payload_bits}')
    ensure(
        0 <= offset * 8 < meta_op_bit_length(mem),
        f"Offset out of bounds: {meta_op_bit_length(mem)=}, {offset=}"
    )
    ensure(
        meta_op_bit_length(mem) - offset * 8 + payload_bits >= 0,
        f"Payload byte doesn't fit within destination: "
        f"{meta_op_bit_length(mem)=}, {offset=}, {meta_op_bit_length(payload)=}"
    )

    out = op_set_bits(mem, offset * 8, payload)
    return contract_validate_memory(out)


def op_set_bytes(mem: MemRgn, offset: int, payload: MemRgn) -> MemRgn:
    """
    Assumes exact bit length of payload should fit in destination. Does not
    concatenate the bits that don't fit from the payload. The payload is
    expected to be smaller than or equal to the memory region (plus offset * 8).

    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    payload_bits = meta_op_bit_length(payload)
    ensure(
        0 <= offset * 8 <= offset * 8 + payload_bits <= meta_op_bit_length(mem),
        f"Payload byte doesn't fit within destination: "
        f"{meta_op_bit_length(mem)=}, {offset=}, {payload_bits=}"
    )

    out = op_set_bits(mem, offset * 8, payload)
    return contract_validate_memory(out)


# ------------------------------------------------------------------------------
# Memory transformation operations for memory within the program's universe.
# ------------------------------------------------------------------------------

def op_truncate(mem: MemRgn, length: int) -> MemRgn:
    "Truncates a memory region to be shorter or equal bit length."
    contract_validate_memory(mem)
    mem_len = meta_op_bit_length(mem)
    ensure(
        length <= mem_len,
        f'Truncated length ({length}) is longer than region size ({mem_len}). '
        f'Use `{op_extend.__name__}` or `{op_ensure_bit_length.__name__}` '
        f'instead'
    )

    bits = [bit for byte in mem.bytes for bit in byte][:length]
    out = MemRgn()

    out.bytes = group_bits_into_bytes(bits)

    return contract_validate_memory(out)


def op_extend(mem: MemRgn, amount: int, fill: MemRgn) -> MemRgn:
    "Extends a memory region with 0 or 1 to a given bit length."
    contract_validate_memory(mem)
    mem_len = meta_op_bit_length(fill)
    ensure(mem_len == 1, 'Fill payload must be 0 or 1')

    length = mem_len + amount
    padding = [fill.bytes[0][0]] * (length - mem_len)
    bits = list(iterate_logical_bits(mem.bytes)) + padding
    out = MemRgn()
    out.bytes = group_bits_into_bytes(bits)

    return contract_validate_memory(out)


def op_ensure_bit_length(mem: MemRgn, length: int) -> MemRgn:
    "Extends with zeros or truncates a memory region to be a specific length."
    contract_validate_memory(mem)
    mem_len = meta_op_bit_length(mem)

    if mem_len > length:
        out = op_truncate(mem, length)

    elif mem_len < length:
        fill = MemRgn()
        fill.bytes.append([0] + [None] * 7)
        out = op_extend(mem, length - mem_len, fill)

    else:
        out = mem

    return contract_validate_memory(out)


def op_ensure_byte_length(mem: MemRgn, length: int) -> MemRgn:
    "Extends with zeros or truncates a memory region to be a specific length."
    contract_validate_memory(mem)
    out = op_ensure_bit_length(mem, length * 8)
    return contract_validate_memory(out)


def op_concatenate(mem_left: MemRgn, mem_right: MemRgn) -> MemRgn:
    """
    Invariant: memory regions should be from the same universe and valid.
    """

    contract_validate_memory(mem_left)
    contract_validate_memory(mem_right)

    bits = [
        bit for region in [mem_left, mem_right]
        for byte in region.bytes
        for bit in byte if bit is not None
    ]

    out = MemRgn()
    out.bytes = group_bits_into_bytes(bits)

    return contract_validate_memory(out)


# ------------------------------------------------------------------------------
# Host language specific meta operations for memory regions
# ------------------------------------------------------------------------------

# Contract to uphold invariant in a decentralized way
def contract_validate_memory(mem: MemRgn) -> MemRgn:
    ensure(
        all(len(byte) == 8 for byte in mem.bytes),
        f'Some bytes not 8 bits: {mem.bytes}'
    )
    ensure(
        all(all(i in {0, 1, None} for i in byte) for byte in mem.bytes),
        f'Some bytes do not contain 0, 1, or None: {mem.bytes}'
    )

    if mem.bytes:
        ensure(
            any(any(i in {0, 1} for i in byte) for byte in mem.bytes),
            f'No bits set: {mem.bytes}'
        )

    all_bits = list(iterate_logical_bits(mem.bytes))

    # This reconstructs the memory by hand to make sure it's valid but it
    # assumes that it's in identity format. Does that work with the algebra?

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
    return mem


# This is a meta-operation that acts as a getter on the data state machine. It
# does not produce the same type used by the algebra so it is not an operation.
# It does however retrieve metadata so it is a meta operation.
def meta_op_bit_length(mem: MemRgn) -> int:
    """
    The number of used bits in the memory region.

    Does not count unset partial bits. For example, the bit length would be 9:
    [[0, 0, 0, 0, 0, 0, 0, 0], [0, None, None, None, None, None, None, None]]

    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    return len(list(iterate_logical_bits(mem.bytes)))


# This is a meta-operation that acts as a getter on the data state machine. It
# does not produce the same type used by the algebra so it is not an operation.
# It does however retrieve metadata so it is a meta operation.
def meta_op_byte_length(mem: MemRgn) -> int:
    """
    The number of bytes necessary to contain the bits in the memory region.

    Relies on the assumption that `MemRgn` always stores a multiple of 8 bits.

    Invariant: input memory must be valid and mapped to program's universe.
    """
    contract_validate_memory(mem)
    return len(mem.bytes)


# ------------------------------------------------------------------------------
# Internal Utility Functions
# ------------------------------------------------------------------------------

def group_bits_into_bytes(bits: list[int]) -> LogicalMemory:
    "Collect flat list of bits into lists of lists of 8 bits (bytes)."
    if not bits:
        return bits
    bytes_ = []
    byte = []
    for i, bit in enumerate(bits):
        if byte and i % 8 == 0:
            bytes_.append(byte[:])
            byte.clear()
        byte.append(bit)
    bytes_.append((byte + [None] * 8)[:8])
    return bytes_


def iterate_logical_bits(bytes_: LogicalMemory) -> list[int]:
    """
    Iterate over a list of list of 8 bits (bytes) one bit at a time, discarding
    Nones.
    """
    return (bit for byte in bytes_ for bit in byte if bit is not None)
