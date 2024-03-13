import indexed_meta
import copy
import pytest
from typing import TypeVar
from tidbytes import (
    Mem, MemRgn, InvalidInitializerException, ensure, op_ensure_bit_length,
    identity_bits_from_numeric_byte
)
from . import UN

T = TypeVar('T')

# * Leaving this unimplemented by storing it in tests for now. Not sure if this
# * is really that useful
class Str(Mem):
    """
    Semantically meaningful data representing a array of UTF8 code points. Not
    distinct from an array of unsigned 8 bit integers. Input types are
    constrained since the output concept is the logical notion of string rather
    than raw memory.
    """
    @classmethod
    def from_(cls, init: T, bit_length: int) -> 'Str':
        # If the input value is any type descended from Mem, copy construct it
        if indexed_meta.is_instance(init, tuple(cls.mro()[:-1])):  # Skip object
            init.validate()
            out = MemRgn()
            out.bytes = copy.copy(init.rgn.bytes)
            return out
        if isinstance(init, type(None)):
            return MemRgn()
        elif isinstance(init, str):
            return from_bytes_utf8(init.encode(), bit_length)
        elif isinstance(init, list):
            if not init:
                return MemRgn()
            elif init and isinstance(init[0], int) and 0 <= init[0] <= 255:
                return from_bytes_utf8(bytearray(init))
            else:
                raise InvalidInitializerException()
        else:
            raise InvalidInitializerException()

    def __str__(self):
        chars = (int(byte, base=2) for byte in Mem.__str__(self).split())
        return bytearray(chars).decode()


def from_bytes_utf8(value: list[int], bit_length: int) -> MemRgn:
    "Memory region from list of unsigned integers in range 0x00 to 0xFF."
    ensure(all(0 <= byte <= 0xFF for byte in value))
    bit_length = bit_length if bit_length is not None else len(value) * 8
    bytes_ = [
        list(reversed(identity_bits_from_numeric_byte(byte)))
        for byte in value
    ]
    out = MemRgn()
    out.bytes = bytes_

    return op_ensure_bit_length(out, bit_length)


@pytest.mark.parametrize('bits,init,expect,msg', [
    (0, 'a', '', 'Truncate to null'),
    (UN, '', '', 'Empty'),
    (UN, 'a', 'a', 'String'),
    (16, 'a', 'a\x00', 'Pad'),
    (8, 'ab', 'a', 'Truncate'),
])
def test_from_str(bits, init, expect, msg):
    assert str(Str[bits](init)) == expect, msg
