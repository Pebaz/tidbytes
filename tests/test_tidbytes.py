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


def test_get_bit():
    mem = memory(9)
    for i in range(op_bit_length(mem)):
        assert op_get_bit(mem, i).bytes == memory(1).bytes


def test_get_bits():
    mem = memory([0] * 8 + [1, 0, 1, 0])
    out = op_get_bits(mem, 0, 8)
    assert out.bytes == [[0] * 8]
    validate_memory(out)


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
