import sys
import pytest
import tidbytes.codec
from types import SimpleNamespace
from typing import *
from tidbytes import *
from . import raises_exception

UN = None  # Unsized

# TODO(pbz): Careful, ctypes u8(0b100000101) truncates to 5, not Tidbytes...
@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b100, '00100000', 'Four'),
    (UN, 0b1011, '11010000', 'Single byte'),
    (UN, 0b100000101, '10100000', 'Single byte out of 2 bytes'),
    (4, 0b1011, '1101', 'Truncation'),
])
def test_from_natural_u8(bits, init, expect, msg):
    assert str(Mem[bits](u8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b100, '00000100', 'Four'),
    (UN, 0b1011, '00001011', 'Single byte'),
    (UN, 0b100000101, '00000101', 'Single byte out of 2 bytes'),
    (7, 0b100000101, '0000101', 'Truncation'),
])
def test_from_numeric_u8(bits, init, expect, msg):
    assert str(Num[bits](u8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '11010000 00000000', 'Single byte'),
    (UN, 0b100000101, '10100000 10000000', '2 bytes'),
    (8, 0b100000101, '10100000', 'Truncation'),
])
def test_from_natural_u16(bits, init, expect, msg):
    assert str(Mem[bits](u16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '00000000 00001011', 'Single byte'),
    (UN, 0b100000101, '00000001 00000101', '2 bytes'),
    (8, 0b100000101, '00000101', '2 bytes'),
])
def test_from_numeric_u16(bits, init, expect, msg):
    assert str(Num[bits](u16(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '11010000 00000000 00000000 00000000', 'Single byte'),
    (UN, 0b101100001011, '11010000 11010000 00000000 00000000', '4 bytes'),
    (16, 0b101100001011, '11010000 11010000', 'Truncate'),
])
def test_from_natural_u32(bits, init, expect, msg):
    assert str(Mem[bits](u32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
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
    assert str(Num[bits](u32(init))) == expect, msg


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
        'Truncate'
    ),
])
def test_from_natural_u64(bits, init, expect, msg):
    assert str(Mem[bits](u64(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
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
    assert str(Num[bits](u64(init))) == expect, msg


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
    (UN, 0b1, '00000001', 'Positive'),
    (UN, -0b1, '11111111', 'Negative'),
    (UN, 0b10, '00000010', 'Positive'),
    (UN, -0b10, '11111110', 'Negative'),
    (4, 0b10, '0000', 'Truncation positive'),
    (4, -0b10, '1111', 'Truncation negative'),
])
def test_from_numeric_i8(bits, init, expect, msg):
    assert str(Num[bits](i8(init))) == expect, msg


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
    (UN, 0b1, '00000000 00000001', 'Positive'),
    (UN, -0b1, '11111111 11111111', 'Negative'),
    (UN, 0b10, '00000000 00000010', 'Positive'),
    (UN, -0b10, '11111111 11111110', 'Negative'),
    (8, 0b10, '00000000', 'Truncation positive'),
    (8, -0b10, '11111111', 'Truncation negative'),
])
def test_from_numeric_i16(bits, init, expect, msg):
    assert str(Num[bits](i16(init))) == expect, msg


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
    (UN, 0b1, '00000000 00000000 00000000 00000001', 'Positive'),
    (UN, -0b1, '11111111 11111111 11111111 11111111', 'Negative'),
    (UN, 0b10, '00000000 00000000 00000000 00000010', 'Positive'),
    (UN, -0b10, '11111111 11111111 11111111 11111110', 'Negative'),
    (16, 0b10, '00000000 00000000', 'Truncation positive'),
    (16, -0b10, '11111111 11111111', 'Truncation negative'),
])
def test_from_numeric_i32(bits, init, expect, msg):
    assert str(Num[bits](i32(init))) == expect, msg


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


@pytest.mark.parametrize('bits,init,expect,msg', [
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
    (32, 0b10, '00000000 00000000 00000000 00000000', 'Truncation positive'),
    (32, -0b10, '11111111 11111111 11111111 11111111', 'Truncation negative'),
])
def test_from_numeric_i64(bits, init, expect, msg):
    assert str(Num[bits](i64(init))) == expect, msg



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
    (UN, 1.0, '00111111 10000000 00000000 00000000', None, 'Positive'),
    (UN, -1.0, '10111111 10000000 00000000 00000000', None, 'Negative'),
    (33, 1.0, '00011111 11000000 00000000 00000000 0', None, 'Pad positive'),
    (33, -1.0, '01011111 11000000 00000000 00000000 0', None, 'Pad negative'),
    (4, 1.0, (), MemException, 'Truncation positive'),
    (4, -1.0, (), MemException, 'Truncation negative'),
])
def test_from_numeric_f32(bits, init, expect, exc, msg):
    with raises_exception(exc):
        assert str(Num[bits](f32(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
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
        assert str(Num[bits](f64(init))) == expect, msg


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


@pytest.mark.parametrize('bits,init,expect,exc,msg', [
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
            assert str(Num[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old

@pytest.mark.parametrize('bits,init,expect,exc,msg', [
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
    try:
        old = tidbytes.codec.PYTHON_X64_FLOATS
        with raises_exception(exc):
            tidbytes.codec.PYTHON_X64_FLOATS = True
            assert str(Num[bits](init)) == expect, msg
    finally:
        tidbytes.codec.PYTHON_X64_FLOATS = old


@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, '', '', 'Empty'),
    (UN, 'a', 'a', 'String'),
    (16, 'a', 'a\x00', 'Pad'),
    (8, 'ab', 'a', 'Truncate'),
])
def test_from_str(bits, init, expect, msg):
    assert str(Str[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
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
    (None, 1, '1', 'Single bit'),
    (None, 4, '001', 'Bit ordering'),
    (1, -1, '1', 'Negative bit'),
    (4, -2, '0111', 'Bit ordering negative'),
    (16, -10, '01101111 11111111', 'Byte ordering'),
    (
        UN,
        sys.maxsize,
        '11111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 1111111',
        'Big integer'
    ),
    (UN, sys.maxsize + 1, '00000000 00000000 00000000 00000000 '
    '00000000 00000000 00000000 00000001', 'Big integer + 1')
])
def test_from_natural_big_integer(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
    (None, 1, '1', 'Single bit'),
    (None, 4, '100', 'Bit ordering'),
    (1, -1, '1', 'Negative bit'),
    (4, -2, '1110', 'Bit ordering negative'),
    (16, -10, '11111111 11110110', 'Byte ordering'),
    (
        UN,
        sys.maxsize,
        '11111111 11111111 11111111 11111111 '
        '11111111 11111111 11111111 1111111',
        'Big integer'
    ),
    (UN, sys.maxsize + 1, '10000000 00000000 00000000 00000000 '
    '00000000 00000000 00000000 00000000', 'Big integer + 1')
])
def test_from_numeric_big_integer(bits, init, expect, msg):
    assert str(Num[bits](init)) == expect, msg



def test_from_bit_list(): ...
def test_from_grouped_bits(): ...



def test_from_bit_length():
    mem = Mem[1]()
    assert str(mem) == '0', 'Invalid!'


# def test_index():
#     mem = Mem.from_byte_u8(255)
#     print(repr(mem))
