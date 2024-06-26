import sys, pytest, tidbytes.codec
from tidbytes.mem_types import (
    MemException, u8, u16, u32, u64, i8, i16, i32, i64, f32, f64, L2R, R2L
)
from tidbytes.idiomatic import Mem, Unsigned, Signed
from . import raises_exception, UN, Slice

@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b100, '00100000', 'Four'),
    (UN, 0b1011, '11010000', 'Single byte'),
])
def test_from_natural_u8(bits, init, expect, msg):
    assert str(Mem[bits](u8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '11010000 00000000', 'Single byte'),
    (UN, 0b100000101, '10100000 10000000', '2 bytes'),
])
def test_from_natural_u16(bits, init, expect, msg):
    assert str(Mem[bits](u16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '11010000 00000000 00000000 00000000', 'Single byte'),
    (UN, 0b101100001011, '11010000 11010000 00000000 00000000', '4 bytes'),
    (16, 0b101100001011, '11010000 11010000', 'Pad'),
])
def test_from_natural_u32(bits, init, expect, msg):
    assert str(Mem[bits](u32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (
        UN,
        0b1011,
        '11010000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        'Single byte'
    ),
    (
        UN,
        0b1011000010110000101100001011,
        '11010000 11010000 11010000 11010000 '
        '00000000 00000000 00000000 00000000',
        '8 bytes'
    ),
    (
        32,
        0b1011000010110000101100001011,
        '11010000 11010000 11010000 11010000',
        'Pad'
    ),
])
def test_from_natural_u64(bits, init, expect, msg):
    assert str(Mem[bits](u64(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1, '10000000', 'Positive'),
    (UN, -0b1, '11111111', 'Negative'),
    (UN, 0b10, '01000000', 'Positive'),
    (UN, -0b10, '01111111', 'Negative'),
    (4, 0b10, '0100', 'Truncation positive'),
    (4, -0b10, '0111', 'Truncation negative'),
])
def test_from_natural_i8(bits, init, expect, msg):
    assert str(Mem[bits](i8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1, '10000000 00000000', 'Positive'),
    (UN, -0b1, '11111111 11111111', 'Negative'),
    (UN, 0b10, '01000000 00000000', 'Positive'),
    (UN, -0b10, '01111111 11111111', 'Negative'),
    (8, 0b10, '01000000', 'Truncation positive'),
    (8, -0b10, '01111111', 'Truncation negative'),
])
def test_from_natural_i16(bits, init, expect, msg):
    assert str(Mem[bits](i16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1, '10000000 00000000 00000000 00000000', 'Positive'),
    (UN, -0b1, '11111111 11111111 11111111 11111111', 'Negative'),
    (UN, 0b10, '01000000 00000000 00000000 00000000', 'Positive'),
    (UN, -0b10, '01111111 11111111 11111111 11111111', 'Negative'),
    (16, 0b10, '01000000 00000000', 'Truncation positive'),
    (16, -0b10, '01111111 11111111', 'Truncation negative'),
])
def test_from_natural_i32(bits, init, expect, msg):
    assert str(Mem[bits](i32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (
        UN,
        0b1,
        '10000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        'Positive'
    ),
    (
        UN,
        -0b1,
        '11111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 11111111',
        'Negative'
    ),
    (
        UN,
        0b10,
        '01000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        'Positive'
    ),
    (
        UN,
        -0b10,
        '01111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 11111111',
        'Negative'
    ),
    (32, 0b10, '01000000 00000000 00000000 00000000', 'Truncation positive'),
    (32, -0b10, '01111111 11111111 11111111 11111111', 'Truncation negative'),
])
def test_from_natural_i64(bits, init, expect, msg):
    assert str(Mem[bits](i64(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (UN, 1.0, '00000000 00000000 00000001 11111100', None, 'Positive'),
    (UN, -1.0, '00000000 00000000 00000001 11111101', None, 'Negative'),
    (33, 1.0, '00000000 00000000 00000001 11111100 0', None, 'Pad positive'),
    (33, -1.0, '00000000 00000000 00000001 11111101 0', None, 'Pad negative'),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_natural_f32(bits, init, expect, exc, msg):
    with raises_exception(exc):
        assert str(Mem[bits](f32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (
        UN,
        1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111100',
        None,
        'Positive'
    ),
    (
        UN,
        -1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111101',
        None,
        'Negative'
    ),
    (
        65,
        1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111100 0',
        None,
        'Pad positive'
    ),
    (
        65,
        -1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111101 0',
        None,
        'Pad negative'
    ),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_natural_f64(bits, init, expect, exc, msg):
    with raises_exception(exc):
        assert str(Mem[bits](f64(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (UN, 1.0, '00000000 00000000 00000001 11111100', None, 'Positive'),
    (UN, -1.0, '00000000 00000000 00000001 11111101', None, 'Negative'),
    (33, 1.0, '00000000 00000000 00000001 11111100 0', None, 'Pad positive'),
    (33, -1.0, '00000000 00000000 00000001 11111101 0', None, 'Pad negative'),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_natural_float_python32(bits, init, expect, exc, msg):
    try:
        old = tidbytes.codec.PYTHON_X64_FLOATS
        with raises_exception(exc):
            tidbytes.codec.PYTHON_X64_FLOATS = False
            assert str(Mem[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (
        UN,
        1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111100',
        None,
        'Positive'
    ),
    (
        UN,
        -1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111101',
        None,
        'Negative'
    ),
    (
        65,
        1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111100 0',
        None,
        'Pad positive'
    ),
    (
        65,
        -1.0,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00001111 11111101 0',
        None,
        'Pad negative'
    ),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_natural_float_python64(bits, init, expect, exc, msg):
    try:
        old = tidbytes.codec.PYTHON_X64_FLOATS
        with raises_exception(exc):
            tidbytes.codec.PYTHON_X64_FLOATS = True
            assert str(Mem[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, b'\x00', '', 'Trucate to null'),
    (UN, b'\x00', '00000000', 'Single byte'),
    (UN, b'\x00\x01', '00000000 00000001', '2 bytes 1 bit'),
    (UN, b'\x00\x02', '00000000 00000010', '2 bytes 2 bits'),
    (16, b'\x02', '00000010 00000000', 'Pad'),
    (8, b'\x00\x02', '00000000', 'Truncation'),
])
def test_from_bytes(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, True, '1', 'Single bit true'),
    (UN, False, '0', 'Single bit false'),
    (3, True, '100', 'Multiple bits true'),
    (3, False, '000', 'Multiple bits false'),
])
def test_from_bool(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (None, 1, '1', 'Single bit, intrinsic pad bit for twos complement'),
    (None, 4, '001', 'Bit ordering'),
    (
        UN,
        sys.maxsize,
        '11111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 1111111',
        'Big integer'
    ),
    (
        UN,
        sys.maxsize + 1,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000001',
        'Big integer + 1'
    )
])
def test_from_natural_big_integer_unsigned(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (1, [1], '1', 'Single bit'),
    (UN, [1], '1', 'Single bit'),
    (UN, [1, 0], '10', 'Bit ordering'),
    (UN, [1, 0, 1, 1, 1, 1, 1, 1, 0], '10111111 0', 'Byte ordering'),
    (4, [1, 0, 1, 1], '1011', 'Sized'),
])
def test_from_bit_list(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (1, [[1]], '1', 'Single bit'),
    (UN, [[1]], '1', 'Single bit'),
    (UN, [[1, 0]], '10', 'Bit ordering'),
    (UN, [[1, 0, 1, 1, 1, 1, 1, 1], [0]], '10111111 0', 'Byte ordering'),
    (4, [[1, 0, 1, 1]], '1011', 'Sized region'),
])
def test_from_grouped_bits(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


def test_from_bit_length():
    mem = Mem[1]()
    assert str(mem) == '0', 'Invalid!'


@pytest.mark.parametrize('bits,init,expect', [
    (UN, 0, False),
    (UN, 1, True),
    (2, 0, False),
    (2, 1, True),
    # This is a dangerous precedent but is necessary because it's not truncating
    # anything it's converting 0 to a zero sized memory region (0 == null in C)
    (0, 0, False),
])
def test_mem___bool__(bits, init, expect):
    mem = Mem[bits](init)
    assert bool(mem) == expect


@pytest.mark.parametrize('bits,init,out,expect', [
    (2, 0, 0, '00'),
    (2, 1, 2, '10'),
    (3, 0, 0, '000'),
    (3, 1, 4, '100'),
    (3, 2, 2, '010'),
    (3, 3, 6, '110'),
])
def test_mem___int__(bits, init, out, expect):
    mem = Mem[bits](init)
    assert str(mem) == expect, f'Incorrect bits: {init}'
    assert int(mem) == out, f'Incorrect number: {init}'


@pytest.mark.parametrize('index,expect,msg', [
    (Slice[::1], '01111111 11001101', 'Identity'),
    (Slice[::8], '01111111 11001101', 'Identity'),
    (Slice[2::1], '11111111 001101', 'Start, step bit'),
    (Slice[1::8], '11001101', 'Start, step byte'),
    (Slice[:4], '0111', 'Stop'),
    (Slice[:4:1], '0111', 'Stop, step bit'),
    (Slice[:2:8], '01111111 11001101', 'Stop, step byte'),
    (Slice[8:12], '1100', 'Start, stop'),
    (Slice[8:12:], '1100', 'Start, stop'),
    (Slice[8:12:1], '1100', 'Start, stop, step bit'),
    (Slice[0:2:8], '01111111 11001101', 'Start, stop, step byte'),

    (Slice[::-1], '10110011 11111110', 'Reverse'),
    (Slice[::-8], '11001101 01111111', 'Reverse bytes'),
    (Slice[-4::1], '1101', 'Start, step bit negative'),
    (Slice[-1::8], '11001101', 'Start, step byte negative'),
    (Slice[:-4], '01111111 1100', 'Stop negative'),
    (Slice[:-4:1], '01111111 1100', 'Stop, step bit negative'),
    (Slice[:-1:8], '01111111', 'Stop, step byte negative'),
    (Slice[-8:-4], '1100', 'Start, stop negative'),
    (Slice[-8:-4:], '1100', 'Start, stop negative'),
    (Slice[-8:-4:1], '1100', 'Start, stop, step bit negative'),
    (Slice[-2:-1:8], '01111111', 'Start, stop, step byte negative'),
    # TODO(pbz): Make sure wrapping negatives works for op_get_bit, etc.
    # TODO Test limits like -10000 should be akin to 0
    # TODO Check indexes backwards like: [10:4] returns []
    # TODO Allow this to work: [10:2:-1] (iterate backwards)

    (Slice[1:], '11111111 1001101', 'Slice to end'),
    (Slice[1::1], '11111111 1001101', 'Slice to end'),
])
def test_mem__getitem__(index, expect, msg):
    mem = Mem[16]('0111111111001101')
    assert str(mem[0]) == '0'
    assert str(mem[1]) == '1'
    assert str(mem[Slice[1]]) == '1'
    other = mem[:]
    start, stop, step = index.start, index.stop, index.step

    assert mem.rgn is not other.rgn, 'Should not be same region'
    assert mem.rgn.bytes is not other.rgn.bytes, 'Should not be same bytes'
    assert str(other) == str(mem), 'Copy constructor failed'
    assert str(mem[0]) == '0', 'Single bit index failed'
    assert str(mem[len(mem) - 1]) == '1', 'Last bit index failed'
    assert str(mem[start:stop:step]) == expect, (
        f'[{msg}]: {mem}[{start}:{stop}:{step}] != {expect}'
    )

    with pytest.raises(MemException, match='Can only step index by*'):
        mem['foo':1:'asdf']
    with pytest.raises(MemException, match='Invalid index'):
        mem['foo':1:8]


def test_mem__setitem__():
    mem = Mem[1]()
    assert int(mem[0]) == 0

    mem[0] = Unsigned[1](u8(1))
    assert int(mem[0]) == 1

    mem = Mem[2]()
    mem[0] = Signed[2](i8(1))
    assert int(mem[1]) == 1


def test_mem___init__():
    assert list(iter(Mem[4](1))) == [1, 0, 0, 0]


def test_mem___reversed__():
    assert list(reversed(Mem[4](1))) == [0, 0, 0, 1]


def test_mem_identity():
    mem = Mem[24](1)
    assert str(mem) == str(mem.identity())


def test_mem_reverse():
    mem = Mem[24](1)
    assert list(reversed(mem)) == list(mem.reverse())


def test_mem_reverse_bytes():
    mem = Mem[24](1).reverse_bytes()
    res = type(mem)(1)
    res.rgn.bytes = list(reversed(res.rgn.bytes))
    assert mem == res


def test_mem_reverse_bits():
    mem = Mem[24](1).reverse_bits()
    res = type(mem)(1)
    res.rgn.bytes = [list(reversed(byte)) for byte in res.rgn.bytes]
    assert mem == res


def test_mem__repr__():
    assert repr(Mem[4](1)) == '<Mem [1000]>'
    assert repr(Mem[65](1)) == '<Mem [0x10000000000000000]>'


def test_mem__format__():
    mem = Mem[4](1)
    assert f'{mem}' == '1000'
    assert f'{mem:bits}' == '1000'
    assert f'{mem:hex}' == hex(int(mem))
    assert f'{mem:x}' == hex(int(mem))
    assert f'{mem:X}' == hex(int(mem)).upper()


def test_mem___add__():
    a, b = [Mem[4](1)] * 2
    assert str(a + b) == '10001000'


def test_mem_bytes():
    mem = Mem[4](1)
    # bytes() calls __iter__ and apparently accepts ints
    assert bytes(mem) == b'\x01\x00\x00\x00'


def test_passthrough_methods():
    "This might be the most valuable test in the entire suite."
    mem = Mem[16](1)
    assert str(mem) == '10000000 00000000'
    assert (
        str(mem.transform(bit_order=L2R, byte_order=L2R)) == '10000000 00000000'
    )
    assert str(mem.identity()) == '10000000 00000000'
    assert str(mem.reverse()) == '00000000 00000001'
    assert str(mem.reverse_bits()) == '00000000 10000000'
    assert str(mem.reverse_bytes()) == '10000000 00000000'
    assert str(mem.get_bit(0)) == '1'
    assert str(mem.get_byte(0)) == '10000000'
    assert str(mem.get_bits(0, 8)) == '10000000'
    assert str(mem.get_bytes(0, 1)) == '10000000'
    assert str(mem.set_bit(8, 1)) == '10000000 10000000'
    assert str(mem.set_bits(1, 1)) == '11000000 10000000'
    assert str(mem.set_byte(0, 0)) == '00000000 10000000'
    assert str(mem.set_bytes(0, [1] * 15)) == '11111111 11111110'
    assert str(mem.truncate(8)) == '11111111'
    assert str(mem.extend(8, 0)) == '11111111 00000000'
    assert str(mem.ensure_bit_length(8)) == '11111111'
    assert str(mem.ensure_bit_length(16)) == '11111111 00000000'
    assert str(mem.ensure_byte_length(1)) == '11111111'
    assert str(mem.ensure_byte_length(2)) == '11111111 00000000'
    assert str(mem.concatenate(1)) == '11111111 00000000 1'


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, '', '', 'Unsized raw'),

    (UN, '1', '1', 'Unsized raw'),
    (UN, '10', '10', 'Unsized raw'),

    (5, '1', '10000', 'Sized raw'),
    (5, '10', '10000', 'Sized raw'),
])
def test_from_str(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


little, big = L2R, R2L
@pytest.mark.parametrize('bits,init,expect1,expect2,expect3,order', [
    (UN, '1', 0b1, 0x01, b'\x01', little),
    (UN, '10000000', 0b10000000, 0x80, b'\x80', little),
    (8, '1', 0b10000000, 0x80, b'\x80', little),
    (9, '1', 0b10000000_0, 0x0100, b'\x80\x00', little),

    (UN, '1', 0b1, 0x01, b'\x01', big),
    (UN, '10000000', 0b10000000, 0x80, b'\x80', big),
    (8, '1', 0b10000000, 0x80, b'\x80', big),
    (9, '1', 0b10000000_0, 0x0100, b'\x00\x80', big),
])
def test_mem_as_bytes(bits, init, expect1, expect2, expect3, order):
    mem = Mem[bits](init)
    assert int(mem) == expect1 == expect2
    assert mem.as_bytes(order) == expect3
