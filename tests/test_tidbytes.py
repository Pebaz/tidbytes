import pytest
from typing import *
from tidbytes import *

HALF_BYTE = [0, 1] * 2
BYTE = HALF_BYTE * 2
BYTE_AND_HALF = BYTE + HALF_BYTE
BYTE_X2 = BYTE * 2
L2R = Order.LeftToRight
R2L = Order.RightToLeft

HALF = [1, 0, 1, 0]
BYTE1 = [1, 0, 0, 0, 0, 0, 0, 0]  # ? , [1, 0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0]
BYTE2 = [0, 1, 0, 0, 0, 0, 0, 0]
BYTE3 = [1, 1, 0, 0, 0, 0, 0, 0]
BYTE4 = [0, 0, 1, 0, 0, 0, 0, 0]


def memory(bit_count_or_init: int | str | list | tuple) -> Mem:
    """
    The Idiomatic interface is for rich memory construction. This is a utility
    function since mixing the Idiomatic and Von Neumann would be no good.
    """
    mem = MemRgn()
    if isinstance(bit_count_or_init, int):
        mem.bytes = [[0] * 8 for _ in range(bit_count_or_init // 8)]
        part = bit_count_or_init % 8
        if part > 0:
            mem.bytes.append([0] * part + [None] * (8 - part))
    elif isinstance(bit_count_or_init, (str, list, tuple)):
        byte = []
        for i, bit in enumerate(map(int, bit_count_or_init)):
            if byte and i % 8 == 0:
                mem.bytes.append(byte[:])
                byte.clear()
            byte.append(bit)
        mem.bytes.append((byte + [None] * 8)[:8])
    validate_memory(mem)
    return mem


def validate_memory(mem: MemRgn) -> bool:
    assert all(len(byte) == 8 for byte in mem.bytes), (
        f'Some bytes not 8 bits: {mem.bytes}'
    )
    assert all(all(i in {0, 1, None} for i in byte) for byte in mem.bytes), (
        f'Some bytes do not contain 0, 1, or None: {mem.bytes}'
    )
    assert any(any(i in {0, 1} for i in byte) for byte in mem.bytes), (
        f'No bits set: {mem.bytes}'
    )

    all_bits = []
    for byte in mem.bytes:
        for bit in byte:
            if bit != None:
                all_bits.append(bit)
    all_bits += [None] * (8 - len(all_bits) % 8)
    all_bytes = []
    while all_bits:
        all_bytes.append(all_bits[:8])
        all_bits = all_bits[8:]
    assert mem.bytes == all_bytes, (
        f'Some bytes contained unset bits in the middle: {mem.bytes}. Should be: {all_bytes}'
    )


def test_get_bit():
    mem = memory(9)
    for i in range(op_bit_length(mem)):
        assert op_get_bit(mem, i).bytes == memory(1).bytes


def test_get_byte():
    mem = memory(4)
    assert op_get_byte(mem, 0).bytes == memory(4).bytes


def test_set_bit():
    mem = memory(9)
    pay = memory(1)
    pay.bytes[0][0] = 1
    mem = op_set_bit(mem, 8, pay)
    assert mem.bytes[1][0] == 1
    validate_memory(mem)

def test_set_bits():
    mem = memory(12)
    pay = memory([1, 0, 1, 0])
    pay.bytes[0][0] = 1
    mem = op_set_bits(mem, 8, pay)
    assert mem.bytes[1] == pay.bytes[0]
    validate_memory(mem)
