import sys
import pytest
import tidbytes.codec

from tidbytes.mem_types import (
    MemException, u8, u16, u32, u64, i8, i16, i32, i64, f32, f64
)
from tidbytes.idiomatic import Mem, Unsigned, Signed, Str

from . import raises_exception, UN, Slice

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
    assert str(Mem[0](0)) == ''
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

    # It's odd, but the twos-complement counts up towards -1 (properly here)
    # ! assert str(Signed[2](2)) == '10' <- This should error out -2 ..= 1
    # ! This is the problem ^^^
    # ! There needs to be checking even for the positive range:
    # ! from_numeric_big_integer needs to check for signed/unsigned because the
    # ! ranges are totally different
    # TODO(pbz): Mem[2](2) is also wrong due to signedness issues with bit_len
    # ? Does that mean codecs need to know origin AND destination?
    # * bit_length has different range for signed and unsigned although this
    # * isn't the case with other codec types right?
    # ? from_numeric_big_integer_into_signed()
    # * from_numeric_u32() says the signedness -> u32
    # * from_numeric_signed_big_integer() has half range than unsigned
    # * from_numeric_unsigned_big_integer() has full range, truncs null values
    # Concerns: the goal of splitting these up is because I thought there would
    # be generic versions of these but it turns out that the codec may have to
    # know the destination type (Signed vs Unsigned). Is this true? <-
    # In theory, the codec doesn't care how the bits are treated afterwards. It
    # could just load them into memory according to a

    # * For these two functions, the signedness impacts how the bit_length field
    # * is interpreted:
    # *     from_numeric_big_integer_signed
    # *     from_numeric_big_integer_unsigned
    # * from_ubig(), from_ibig()

    # I think this is ok: these codecs are generic because the `_signed` and
    # `_unsigned` postfix refers to how the `bit_length` field is interpreted
    # and validated/verified.

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
