import sys
import pytest
from typing import *
from tidbytes import *

UN = None  # Unsized

@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, b'\x00', '00000000', 'Single byte'),
    (UN, b'\x00\x01', '00000000 00000001', '2 bytes 1 bit'),
    (UN, b'\x00\x02', '00000000 00000010', '2 bytes 2 bits'),
    (8, b'\x00\x02', '00000000', 'Truncation'),
])
def test_from_bytes(bits, init, expect, msg):
    assert str(Mem[bits](init)) == expect, msg

# TODO(pbz): Careful, ctypes u8(0b100000101) truncates to 5, not Tidbytes...
@pytest.mark.parametrize('bits,init,expect,msg', [
    (UN, 0b1011, '11010000', 'Single byte'),
    (UN, 0b100000101, '10100000', 'Single byte out of 2 bytes'),
    (4, 0b1011, '1101', 'Truncation'),
])
def test_from_natural_u8(bits, init, expect, msg):
    assert str(Mem[bits](u8(init))) == expect, msg


@pytest.mark.parametrize('bits,init,expect,msg', [
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






# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!

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


# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!
# TODO(pbz): Test signed integers!







def test_from_bit_length():
    mem = Mem[1]()
    assert str(mem) == '0', 'Invalid!'


'''
# def test_index():
#     mem = Mem.from_byte_u8(255)
#     print(repr(mem))


# def test_mem_constructor():
#     mem = Mem.from_ascii('Hello World!')
'''
