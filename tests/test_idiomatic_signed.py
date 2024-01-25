import sys
import pytest
import tidbytes.codec

from tidbytes.mem_types import (
    MemException, u8, u16, u32, u64, i8, i16, i32, i64, f32, f64
)
from tidbytes.idiomatic import Mem, Unsigned, Signed, Str

from . import raises_exception, UN, Slice


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b0, '', 'Truncate to null'),
    (UN, 0b100, '00000100', 'Four'),
    (UN, 0b1011, '00001011', 'Single byte'),
])
def test_from_numeric_u8(bits, init, expect, msg):
    assert str(Signed[bits](u8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1011, '', 'Truncate to null'),
    (UN, 0b1011, '00000000 00001011', 'Single byte'),
    (UN, 0b100000101, '00000001 00000101', '2 bytes'),
    (8, 0b100000101, '00000101', '2 bytes'),
])
def test_from_numeric_u16(bits, init, expect, msg):
    assert str(Signed[bits](u16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1011, '', 'Truncate to null'),
    (UN, 0b1011, '00000000 00000000 00000000 00001011', 'Single byte'),
    (
        UN,
        0b00000001000001010000000100000101,
        '00000001 00000101 00000001 00000101',
        '4 bytes'
    ),
    (
        16,
        0b00000001000001010000000100000101,
        '00000001 00000101',
        'Truncate'
    ),
])
def test_from_numeric_u32(bits, init, expect, msg):
    assert str(Signed[bits](u32(init))) == expect, msg



@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1011, '', 'Truncate to null'),
    (
        UN,
        0b1011,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00001011',
        'Single byte'
    ),
    (
        UN,
        0b0000000100000101000000010000010100000001000001010000000100000101,
        '00000001 00000101 00000001 00000101 '
        '00000001 00000101 00000001 00000101',
        '8 bytes'
    ),
    (
        32,
        0b0000000100000101000000010000010100000001000001010000000100000101,
        '00000001 00000101 00000001 00000101',
        'Truncate'
    ),
])
def test_from_numeric_u64(bits, init, expect, msg):
    assert str(Signed[bits](u64(init))) == expect, msg



@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b0, '', 'Truncate to null'),
    (UN, 0b1, '00000001', 'Positive'),
    (UN, -0b1, '11111111', 'Negative'),
    (UN, 0b10, '00000010', 'Positive'),
    (UN, -0b10, '11111110', 'Negative'),
    (4, 0b10, '0010', 'Truncation positive'),
    (4, -0b10, '1110', 'Truncation negative'),
])
def test_from_numeric_i8(bits, init, expect, msg):
    assert str(Signed[bits](i8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1, '', 'Truncate to null'),
    (UN, 0b1, '00000000 00000001', 'Positive'),
    (UN, -0b1, '11111111 11111111', 'Negative'),
    (UN, 0b10, '00000000 00000010', 'Positive'),
    (UN, -0b10, '11111111 11111110', 'Negative'),
    (8, 0b10, '00000010', 'Truncation positive'),
    (8, -0b10, '11111110', 'Truncation negative'),
])
def test_from_numeric_i16(bits, init, expect, msg):
    assert str(Signed[bits](i16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1, '', 'Truncate to null'),
    (UN, 0b1, '00000000 00000000 00000000 00000001', 'Positive'),
    (UN, -0b1, '11111111 11111111 11111111 11111111', 'Negative'),
    (UN, 0b10, '00000000 00000000 00000000 00000010', 'Positive'),
    (UN, -0b10, '11111111 11111111 11111111 11111110', 'Negative'),
    (16, 0b10, '00000000 00000010', 'Truncation positive'),
    (16, -0b10, '11111111 11111110', 'Truncation negative'),
])
def test_from_numeric_i32(bits, init, expect, msg):
    assert str(Signed[bits](i32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 0b1, '', 'Truncate to null'),
    (
        UN,
        0b1,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000001',
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
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000010',
        'Positive'
    ),
    (
        UN,
        -0b10,
        '11111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 11111110',
        'Negative'
    ),
    (32, 0b10, '00000000 00000000 00000000 00000010', 'Truncation positive'),
    (32, -0b10, '11111111 11111111 11111111 11111110', 'Truncation negative'),
])
def test_from_numeric_i64(bits, init, expect, msg):
    assert str(Signed[bits](i64(init))) == expect, msg




@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (0, 1.0, '', None, 'Truncate to null'),
    (UN, 1.0, '00111111 10000000 00000000 00000000', None, 'Positive'),
    (UN, -1.0, '10111111 10000000 00000000 00000000', None, 'Negative'),
    (33, 1.0, '00011111 11000000 00000000 00000000 0', None, 'Pad positive'),
    (33, -1.0, '01011111 11000000 00000000 00000000 0', None, 'Pad negative'),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_numeric_f32(bits, init, expect, exc, msg):
    with raises_exception(exc):
        assert str(Signed[bits](f32(init))) == expect, msg



@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (0, 1.0, '', None, 'Truncate to null'),
    (
        UN,
        1.0,
        '00111111 11110000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        None,
        'Positive'
    ),
    (
        UN,
        -1.0,
        '10111111 11110000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        None,
        'Negative'
    ),
    (
        65,
        1.0,
        '00011111 11111000 00000000 00000000 0'
        '0000000 00000000 00000000 00000000 0',
        None,
        'Pad positive'
    ),
    (
        65,
        -1.0,
        '01011111 11111000 00000000 00000000 0'
        '0000000 00000000 00000000 00000000 0',
        None,
        'Pad negative'
    ),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_numeric_f64(bits, init, expect, exc, msg):
    with raises_exception(exc):
        assert str(Signed[bits](f64(init))) == expect, msg







@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (0, 1.0, '', None, 'Truncate to null'),
    (UN, 1.0, '00111111 10000000 00000000 00000000', None, 'Positive'),
    (UN, -1.0, '10111111 10000000 00000000 00000000', None, 'Negative'),
    (33, 1.0, '00011111 11000000 00000000 00000000 0', None, 'Pad positive'),
    (33, -1.0, '01011111 11000000 00000000 00000000 0', None, 'Pad negative'),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_numeric_float_python32(bits, init, expect, exc, msg):
    try:
        old = tidbytes.codec.PYTHON_X64_FLOATS
        with raises_exception(exc):
            tidbytes.codec.PYTHON_X64_FLOATS = False
            assert str(Signed[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old



@pytest.mark.parametrize('bits,init,expect,exc,msg', [
    (0, 1.0, '', None, 'Truncate to null'),
    (
        UN,
        1.0,
        '00111111 11110000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        None,
        'Positive'
    ),
    (
        UN,
        -1.0,
        '10111111 11110000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        None,
        'Negative'
    ),
    (
        65,
        1.0,
        '00011111 11111000 00000000 00000000 0'
        '0000000 00000000 00000000 00000000 0',
        None,
        'Pad positive'
    ),
    (
        65,
        -1.0,
        '01011111 11111000 00000000 00000000 0'
        '0000000 00000000 00000000 00000000 0',
        None,
        'Pad negative'
    ),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_numeric_float_python64(bits, init, expect, exc, msg):
    (0, 1.0, '', 'Truncate to null'),
    try:
        old = tidbytes.codec.PYTHON_X64_FLOATS
        with raises_exception(exc):
            tidbytes.codec.PYTHON_X64_FLOATS = True
            assert str(Signed[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old



@pytest.mark.parametrize('bits,init,expect,msg', [
    (None, 1, '01', 'Single bit'),
    (None, 4, '0100', 'Bit ordering'),
    (2, -1, '11', 'Negative bits'),
    (4, -2, '1110', 'Bit ordering negative'),
    (16, -10, '11111111 11110110', 'Byte ordering'),
    (
        UN,
        sys.maxsize,
        '01111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 11111111',
        'Big integer'
    ),
    (UN, sys.maxsize + 1, '01000000 00000000 00000000 00000000 '
    '00000000 00000000 00000000 00000000 0', 'Big integer + 1')
])
def test_from_numeric_big_integer(bits, init, expect, msg):
    assert str(Signed[bits](init)) == expect, msg


def test_signed_from_hex_str():
    num = Signed('0xFE')
    assert str(num) == '01111111 0'  # Padding bit for twos-complement

def test_signed_from_bin_str():
    num = Signed('0b1011')
    assert str(num) == '01011'  # Padding bit for twos-complement



@pytest.mark.parametrize('bits,init,expect', [
    (2, 0, '00'),
    (2, 1, '01'),
    (2, -2, '10'),
    (2, -1, '11'),

    (3, 0, '000'),
    (3, 1, '001'),
    (3, 2, '010'),
    (3, 3, '011'),
    (3, -4, '100'),
    (3, -3, '101'),
    (3, -2, '110'),
    (3, -1, '111'),
])
def test_signed___int__(bits, init, expect):
    num = Signed[bits](init)
    assert str(num) == expect, f'Incorrect bits: {init}'
    assert int(num) == init, f'Incorrect number: {init}'



@pytest.mark.parametrize('index,expect,msg', [
    (Slice[::1], '11111111 11111110', 'Copy self'),
    (Slice[:1], '1', 'First bit'),
    (Slice[:1:1], '1', 'First bit'),
    (Slice[:1:8], '11111111', 'First byte'),
    (Slice[0:1], '1', 'First bit'),
    (Slice[0:1:], '1', 'First bit'),
    (Slice[0:1:8], '11111111', 'First byte'),
    (Slice[1::1], '11111111 1111110', 'Missing a bit'),
    (Slice[1::8], '11111110', 'Second byte'),
])
def test_signed__getitem__(index, expect, msg):
    num = Signed[16]([1] * 15 + [0])
    other = num[:]
    start, stop, step = index.start, index.stop, index.step

    assert num.rgn is not other.rgn, 'Should not be same region'
    assert num.rgn.bytes is not other.rgn.bytes, 'Should not be same bytes'
    assert str(other) == str(num), 'Copy constructor failed'
    assert str(num[0]) == '1', 'Single bit index failed'
    assert str(num[len(num) - 1]) == '0', 'Last bit index failed'
    assert str(num[start:stop:step]) == expect, (
        f'[{msg}]: {num}[{start}:{stop}:{step}] != {expect}'
    )
