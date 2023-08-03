import sys
import pytest
from typing import *
from tidbytes import *


@pytest.mark.parametrize('init,expect,msg', [
    (b'\x00', '00000000', 'Single byte'),
    (b'\x00\x01', '00000000 00000001', '2 bytes 1 bit'),
    (b'\x00\x02', '00000000 00000010', '2 bytes 2 bits'),
])
def test_from_bytes(init, expect, msg):
    assert str(Mem.from_bytes(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '11010000', 'Single byte'),
    (0b100000101, '10100000', 'Single byte out of 2 bytes'),
])
def test_from_byte_u8(init, expect, msg):
    assert str(Mem.from_byte_u8(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '00001011', 'Single byte'),
    (0b100000101, '00000101', 'Single byte out of 2 bytes'),
])
def test_from_numeric_u8(init, expect, msg):
    assert str(Mem.from_numeric_u8(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '11010000 00000000', 'Single byte'),
    (0b100000101, '10100000 10000000', '2 bytes'),
])
def test_from_bytes_u16(init, expect, msg):
    assert str(Mem.from_bytes_u16(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '00000000 00001011', 'Single byte'),
    (0b100000101, '00000001 00000101', '2 bytes'),
])
def test_from_numeric_u16(init, expect, msg):
    assert str(Mem.from_numeric_u16(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '11010000 00000000 00000000 00000000', 'Single byte'),
    (0b101100001011, '11010000 11010000 00000000 00000000', '4 bytes'),
])
def test_from_bytes_u32(init, expect, msg):
    assert str(Mem.from_bytes_u32(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (0b1011, '00000000 00000000 00000000 00001011', 'Single byte'),
    (
        0b00000001000001010000000100000101,
        '00000001 00000101 00000001 00000101',
        '4 bytes'
    ),
])
def test_from_numeric_u32(init, expect, msg):
    assert str(Mem.from_numeric_u32(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (
        0b1011,
        '11010000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00000000',
        'Single byte'
    ),
    (
        0b1011000010110000101100001011,
        '11010000 11010000 11010000 11010000 '
        '00000000 00000000 00000000 00000000',
        '8 bytes'
    ),
])
def test_from_bytes_u64(init, expect, msg):
    assert str(Mem.from_bytes_u64(init)) == expect, msg


@pytest.mark.parametrize('init,expect,msg', [
    (
        0b1011,
        '00000000 00000000 00000000 00000000 '
        '00000000 00000000 00000000 00001011',
        'Single byte'
    ),
    (
        0b0000000100000101000000010000010100000001000001010000000100000101,
        '00000001 00000101 00000001 00000101 '
        '00000001 00000101 00000001 00000101',
        '8 bytes'
    ),
])
def test_from_numeric_u64(init, expect, msg):
    assert str(Mem.from_numeric_u64(init)) == expect, msg


def test_from_bit_length():
    mem = Mem.from_bit_length(1)
    assert str(mem) == '0', 'Invalid!'


# def test_index():
#     mem = Mem.from_byte_u8(255)
#     print(repr(mem))


def test_mem_constructor():
    mem = Mem.from_ascii('Hello World!')
