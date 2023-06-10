import pytest
from typing import *
from tidbytes import *

FROM_U8 = Mem.from_u8_as_byte
FROM_U16 = Mem.from_u16_as_bytes

@pytest.mark.parametrize('init,expect,ctor,msg', [
    (0b101, '10100000', FROM_U8, 'Single byte'),
    (0b100000101, '10100000', FROM_U8, 'Single byte out of 2 bytes'),
    (0b100000101, '10100000 10000000', FROM_U16, 'Two bytes'),
])
def test_internal_representation(init, expect, ctor, msg):
    assert str(ctor(init)) == expect, msg



