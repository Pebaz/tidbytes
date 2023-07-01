import math
import pytest
from mem import *
from mem.tests import *


@pytest.mark.parametrize("bit_length", [0, 1, 5, 8, 10, 16])
def test_mem_from_bit_length(bit_length):
    # TODO(pbz): Is testing the internals of this type a useful test?
    report = reporter(bit_length=bit_length)
    mem = Mem.from_bit_length(bit_length)
    assert mem.bits == [0] * bit_length, report()


@pytest.mark.parametrize("bit_length", [5, 8, 10, 16])
def test_mem_str(bit_length):
    report = reporter(bit_length=bit_length)
    mem = Mem.from_bit_length(bit_length)
    assert str(mem) == '0' * bit_length, report()


@pytest.mark.parametrize("bit_length", [5, 8, 10, 16])
def test_mem_to_bytes(bit_length):
    report = reporter(bit_length=bit_length)
    mem = Mem.from_bit_length(bit_length)
    assert mem.to_bytes() == b'\x00' * bytes_needed(bit_length), report()


@pytest.mark.parametrize("bits,byte_length,expected", [
    ([], None, []),
    ([0], None, [0]),
    ([1], None, [1]),
    ([1, 0], None, [1, 0]),
    ([0, 1], None, [0, 1]),
    ('', None, []),
    ('0', None, [0]),
    ('1', None, [1]),
    ('10', None, [1, 0]),
    ('01', None, [0, 1]),
    ([], 1, [0] * 8),
    ([1], 1, [1, 0, 0, 0, 0, 0, 0, 0]),
    ([0, 1], 1, [0, 1, 0, 0, 0, 0, 0, 0]),
    ([0, 1], 1, [0, 1, 0, 0, 0, 0, 0, 0]),
])
def test_mem_from_bits_pass(bits, byte_length, expected):
    report = reporter(bits=bits, byte_length=byte_length, expected=expected)
    mem = Mem.from_bits(bits, byte_length)
    assert mem.bits == expected, report('Bits do not match')


@pytest.mark.parametrize("bits,byte_length,exception", [
    ([0] * 16, 1, AssertionError),
    ([0] * 16, 1, AssertionError),
])
def test_mem_from_bits(bits, byte_length, exception):
    with pytest.raises(exception):
        mem = Mem.from_bits(bits, byte_length)


def test_instruction():
    mem = Mem.from_bits()
