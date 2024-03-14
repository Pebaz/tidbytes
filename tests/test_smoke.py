import pytest
from tidbytes.mem_types import MemException, i8, i16, i32, i64
from tidbytes.idiomatic import Mem, Unsigned, Signed
from tidbytes.codec import (
    range_unsigned, range_signed, is_in_range_signed, is_in_range_unsigned,
    from_natural_big_integer_signed, from_natural_big_integer_unsigned,
    from_numeric_big_integer_signed, from_numeric_big_integer_unsigned
)

def test_smoke():
    """
    This test is extremely important. It basically checks all major assumptions
    in the idiomatic interface. Of particular note is the handling of negative
    two's-complement (big) integers.
    """

    def ensure_fails(lambda_fn):
        with pytest.raises(MemException):
            lambda_fn()

    # Pretends input is unsigned unless it's negative:
    assert str(Mem[1](0)) == '0'
    assert str(Mem[1](1)) == '1'
    ensure_fails(lambda: Mem[1](2))

    # The two's complement version of an i1(-1) is "all ones" or '1'
    assert str(Signed[1](-1)) == '1'

    # The two's complement version of an i1(0) is just '0'
    assert str(Mem[1](i8(0))) == '0'

    # It's odd, but the twos-complement counts up towards -1 (backwards here)
    assert str(Mem[2](1)) == '10'
    assert str(Mem[2](0)) == '00'
    assert str(Signed[2](-1)) == '11'
    assert str(Signed[2](-2)) == '10'

    # assert str(Signed[2](2)) != '10', 'i2 has range -2 ..= 1'
    assert str(Signed[2](1)) == '01'
    assert str(Signed[2](0)) == '00'
    assert str(Signed[2](-1)) == '11'
    assert str(Signed[2](-2)) == '10'

    # Unsigned uses abs() to just ignore the negative sign
    ensure_fails(lambda: str(Unsigned[2](4)))
    assert str(Unsigned[2](3)) == '11'
    assert str(Unsigned[2](2)) == '10'
    assert str(Unsigned[2](1)) == '01'
    assert str(Unsigned[2](0)) == '00'
    ensure_fails(lambda: str(Unsigned[2](-1)))
    ensure_fails(lambda: str(Unsigned[2](-2)))

    '''
    This proves that signed integers are twos complement encoded. Generate this
    range with:

    >>> lo, hi = range_signed(4)
    >>> for i in range(lo, hi + 1):
    >>>     print(f'{i:<3}', f'{Signed[4](i)}')
    '''

    assert str(Signed[4](-8)) == '1000'
    assert str(Signed[4](-7)) == '1001'
    assert str(Signed[4](-6)) == '1010'
    assert str(Signed[4](-5)) == '1011'
    assert str(Signed[4](-4)) == '1100'
    assert str(Signed[4](-3)) == '1101'
    assert str(Signed[4](-2)) == '1110'
    assert str(Signed[4](-1)) == '1111'
    assert str(Signed[4](0)) == '0000'
    assert str(Signed[4](1)) == '0001'
    assert str(Signed[4](2)) == '0010'
    assert str(Signed[4](3)) == '0011'
    assert str(Signed[4](4)) == '0100'
    assert str(Signed[4](5)) == '0101'
    assert str(Signed[4](6)) == '0110'
    assert str(Signed[4](7)) == '0111'

    # Unsigned cannot take ctypes signed integers
    ensure_fails(lambda: Unsigned[4](i8(-8)))

    assert str(Signed[4](-8)) == '1000'
    assert str(Signed[4](i8(-8))) == '1000'
    assert str(Signed[16](i16(-32768))) == '10000000 00000000'

    assert str(Signed[1](-1)) == '1'
    assert str(Signed[1](i8(-1))) == '1'
    assert str(Signed[1](i16(-1))) == '1'
    assert str(Signed[1](i32(-1))) == '1'
    assert str(Signed[1](i64(-1))) == '1'

    assert str(Unsigned[1](1)) == '1'
    assert str(Unsigned[1](i8(1))) == '1'
    assert str(Unsigned[1](i16(1))) == '1'
    assert str(Unsigned[1](i32(1))) == '1'
    assert str(Unsigned[1](i64(1))) == '1'

    assert range_signed(0) == (0, 0)
    assert range_unsigned(8) == (0, 255)
    assert range_signed(8) == (-128, 127)
    assert is_in_range_unsigned(1, 8)
    assert is_in_range_signed(1, 8)

    assert str(Mem(0)) == '0'
    assert str(Unsigned(0)) == '0'
    assert str(Signed(0)) == '0'

    # Make sure zeroed memory counts as non-null (from the perspective of
    # Tidbyte's idioms):
    assert int(Mem(from_natural_big_integer_signed(0, None))) == 0
    assert int(Mem(from_natural_big_integer_signed(0, 0))) == 0
    assert int(Mem(from_natural_big_integer_signed(0, 8))) == 0
    assert int(Mem(from_natural_big_integer_unsigned(0, None))) == 0
    assert int(Mem(from_natural_big_integer_unsigned(0, 0))) == 0
    assert int(Mem(from_natural_big_integer_unsigned(0, 8))) == 0
    assert int(Mem(from_numeric_big_integer_signed(0, None))) == 0
    assert int(Mem(from_numeric_big_integer_signed(0, 0))) == 0
    assert int(Mem(from_numeric_big_integer_signed(0, 8))) == 0
    assert int(Mem(from_numeric_big_integer_unsigned(0, None))) == 0
    assert int(Mem(from_numeric_big_integer_unsigned(0, 0))) == 0
    assert int(Mem(from_numeric_big_integer_unsigned(0, 8))) == 0

    # These particular copy constructors are intense. Check em
    assert str(Signed(Unsigned(Mem(1)))) == '1', 'Copy constructor failed'
    assert str(Signed(Mem(Unsigned(1)))) == '1', 'Copy constructor failed'
    assert str(Unsigned(Signed(Mem(1)))) == '1', 'Copy constructor failed'
    assert str(Unsigned(Mem(Signed[1](-1)))) == '1', 'Copy constructor failed'
    assert str(Mem(Unsigned(Signed[1](-1)))) == '1', 'Copy constructor failed'
    assert str(Mem(Signed(Unsigned(1)))) == '1', 'Copy constructor failed'
