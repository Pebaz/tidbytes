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
    assert str(Mem[1](-1)) == '1'

    # The two's complement version of an i1(0) is just '0'
    assert str(Mem[1](i8(0))) == '0'

    # It's odd, but the twos-complement counts up towards -1 (backwards here)
    assert str(Mem[2](1)) == '10'
    assert str(Mem[2](0)) == '00'
    assert str(Mem[2](-1)) == '11'
    assert str(Mem[2](-2)) == '01'

    # It's odd, but the twos-complement counts up towards -1 (properly here)
    assert str(Signed[2](1)) == '01'
    assert str(Signed[2](0)) == '00'
    assert str(Signed[2](-1)) == '11'
    assert str(Signed[2](-2)) == '10'

    # Unsigned uses abs() to just ignore the negative sign
    assert str(Unsigned[2](2)) == '10'
    assert str(Unsigned[2](1)) == '01'
    assert str(Unsigned[2](0)) == '00'
    assert str(Unsigned[2](-1)) == '01'
    assert str(Unsigned[2](-2)) == '10'

    # TODO(pbz): This should error out. If it can't be meaningfully truncated,
    # TODO don't allow it
    # ! This is wrong. It should not error out but check this <<<
    # assert str(Mem[1](i8(-1))), 'This should have errored out'
