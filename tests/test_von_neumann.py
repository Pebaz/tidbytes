import pytest
from tidbytes.mem_types import Order
from tidbytes.idiomatic import Mem
from tidbytes.von_neumann import (
    MemRgn, op_transform, op_identity, op_reverse, op_reverse_bytes,
    op_reverse_bits, op_get_bit, op_get_byte, op_get_bits, op_get_bytes,
    op_set_bit, op_set_bits, op_set_byte, op_set_bytes, op_truncate,
    contract_validate_memory, meta_op_bit_length, meta_op_byte_length,

    # TODO(pbz): These are not tested here
    op_extend,
    op_ensure_bit_length, op_ensure_byte_length, op_concatenate, op_fill,
    op_fill_range
)

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

    int: num bits
    str: bit string
    list: bit list
    tuple: bit tuple
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
    contract_validate_memory(mem)
    return mem


# ------------------------------------------------------------------------------
# Fail fast tests
# ------------------------------------------------------------------------------

def test_bit_length():
    mem = memory(9)
    assert meta_op_bit_length(mem) == 9


def test_byte_length():
    mem = memory(9)
    assert meta_op_byte_length(mem) == 2


def test_get_bit():
    mem = memory(9)
    for i in range(meta_op_bit_length(mem)):
        assert op_get_bit(mem, i).bytes == memory(1).bytes


def test_get_bits():
    mem = memory([0] * 8 + [1, 0, 1, 0])
    out = op_get_bits(mem, 0, 8)
    assert out.bytes == [[0] * 8]
    contract_validate_memory(out)


def test_get_byte():
    mem = memory(4)
    assert op_get_byte(mem, 0).bytes == memory(4).bytes


def test_set_bit():
    mem = memory(9)
    pay = memory(1)
    pay.bytes[0][0] = 1
    mem = op_set_bit(mem, 8, pay)
    assert mem.bytes[1][0] == 1
    contract_validate_memory(mem)


def test_set_bits():
    mem = memory(12)
    pay = memory([1, 0, 1, 0])
    pay.bytes[0][0] = 1
    mem = op_set_bits(mem, 8, pay)
    assert mem.bytes[1] == pay.bytes[0]
    contract_validate_memory(mem)


# ------------------------------------------------------------------------------
# Parametrized tests
# ------------------------------------------------------------------------------

@pytest.mark.parametrize('init,expect,msg', [
    (1, 1, 'Single bit, 7 unset bits'),
    (8, 8, '8 set bits'),
    (9, 9, '9 set bits, 7 unset bits crossing byte boundary'),
    (16, 16, '2 bytes'),
])
def test_meta_op_bit_length(init, expect, msg):
    mem = memory(init)
    out = meta_op_bit_length(mem)
    assert out == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (1, 1, 'Single bit, 7 unset bits, 1 byte'),
    (8, 1, '1 full byte'),
    (9, 2, '9 set bits, 7 unset bits crossing byte boundary'),
    (17, 3, '3 bytes, 7 unset bits'),
])
def test_meta_op_byte_length(init, expect, msg):
    mem = memory(init)
    out = meta_op_byte_length(mem)
    assert out == expect, msg


@pytest.mark.parametrize('init,index,expect,msg', [
    (1, 0, [[0] + [None] * 7], 'Get only bit'),
    (2, 0, [[0] + [None] * 7], 'Get first bit'),
    ([0] * 7 + [1], 7, [[1] + [None] * 7], 'Get last bit'),
    ([0] * 1 + [1] + [0] * 2, 1, [[1] + [None] * 7], 'Even bit'),
    ([0] * 2 + [1] + [0] * 2, 2, [[1] + [None] * 7], 'Odd bit'),
])
def test_op_get_bit(init, index, expect, msg):
    mem = memory(init)
    out = op_get_bit(mem, index)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,index,expect,msg', [
    (8, 0, [[0] * 8], 'Get only byte'),
    ([0] * 8 + [1] + [0] * 3, 1, [[1] + [0] * 3 + [None] * 4], 'Odd byte'),
])
def test_op_get_byte(init, index, expect, msg):
    mem = memory(init)
    out = op_get_byte(mem, index)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,start,stop,expect,msg', [
    (1, 0, 1, [[0] + [None] * 7], 'Get only bit'),
    (2, 0, 1, [[0] + [None] * 7], 'Get first bit'),
])
def test_op_get_bits(init, start, stop, expect, msg):
    mem = memory(init)
    out = op_get_bits(mem, start, stop)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,start,stop,expect,msg', [
    (8, 0, 1, [[0] * 8], 'Get only byte'),
])
def test_op_get_bytes(init, start, stop, expect, msg):
    mem = memory(init)
    out = op_get_bytes(mem, start, stop)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,offset,payload,expect,msg', [
    (1, 0, [1], [[1] + [None] * 7], 'Set only bit'),
    (2, 0, [1], [[1, 0] + [None] * 6], 'Set first bit'),
])
def test_op_set_bit(init, offset, payload, expect, msg):
    mem = memory(init)
    payload_mem = memory(payload)
    out = op_set_bit(mem, offset, payload_mem)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,offset,payload,expect,msg', [
    (1, 0, [1], [[1] + [None] * 7], 'Set only bit'),
    (2, 0, [1], [[1, 0] + [None] * 6], 'Set first bit'),
])
def test_op_set_bits(init, offset, payload, expect, msg):
    mem = memory(init)
    payload_mem = memory(payload)
    out = op_set_bit(mem, offset, payload_mem)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,offset,payload,expect,msg', [
    (1, 0, [1], [[1] + [None] * 7], 'Set only byte'),
    # (9, 0, [1], [[1] + [None] * 8], 'Set first byte'),
])
def test_op_set_byte(init, offset, payload, expect, msg):
    mem = memory(init)
    payload_mem = memory(payload)
    out = op_set_byte(mem, offset, payload_mem)
    assert out.bytes == expect, msg


@pytest.mark.parametrize('init,offset,payload,expect,msg', [
    (1, 0, [1], [[1] + [None] * 7], 'Set only byte'),
    (9, 0, [1], [[1] + [0] * 7, [0] + [None] * 7], 'Set first byte'),
])
def test_op_set_bytes(init, offset, payload, expect, msg):
    mem = memory(init)
    payload_mem = memory(payload)
    out = op_set_bytes(mem, offset, payload_mem)
    assert out.bytes == expect, msg

# ------------------------------------------------------------------------------
# TODO(pbz): Organize and perhaps parametrize these:

def test_op_truncate():
    mem = memory(8)
    out = op_truncate(mem, 4)
    assert meta_op_bit_length(out) == 4
    assert out.bytes == [[0, 0, 0, 0, None, None, None, None]]


def test_op_transform():
    mem = MemRgn()
    mem.bytes = [[1, 1] + [0] * 6, [0] * 2 + [None] * 6]

    mem = op_transform(mem, bit_order=L2R, byte_order=L2R)

    assert mem.bytes == [
        [1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, None, None, None, None, None, None]
    ]

    mem = op_transform(mem, bit_order=L2R, byte_order=R2L)

    assert mem.bytes == [
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, None, None, None, None, None, None]
    ]

    mem = op_transform(mem, bit_order=R2L, byte_order=L2R)

    assert mem.bytes == [
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, None, None, None, None, None, None]
    ]

    # Undo last op so that the last check is not symmetrical
    mem = op_transform(mem, bit_order=R2L, byte_order=L2R)

    assert mem.bytes == [
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, None, None, None, None, None, None]
    ]

    mem = op_transform(mem, bit_order=R2L, byte_order=R2L)

    assert mem.bytes == [
        [0, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, None, None, None, None, None, None]
    ]

def test_op_identity():
    mem = memory([1, 1, 0])
    out = op_identity(mem)
    assert out.bytes == [[1, 1, 0, None, None, None, None, None]]


def test_op_reverse():
    mem = memory([1, 1, 0])
    out = op_reverse(mem)
    assert out.bytes == [[0, 1, 1, None, None, None, None, None]]


def test_op_reverse_bits():
    mem = memory([1, 1, 0])
    out = op_reverse_bits(mem)
    assert out.bytes == [[0, 1, 1, None, None, None, None, None]]


def test_op_reverse_bytes():
    mem = MemRgn()
    mem.bytes = [[1, 1] + [0] * 6, [0] * 2 + [None] * 6]
    print(mem.bytes)
    out = op_reverse_bytes(mem)
    print(out.bytes)
    assert out.bytes == [
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, None, None, None, None, None, None]
    ]

