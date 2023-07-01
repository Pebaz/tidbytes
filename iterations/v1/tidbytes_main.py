from tidbytes import *

L2R = Order.LeftToRight
R2L = Order.RightToLeft
BYTE1 = [1, 0, 0, 0, 0, 0, 0, 0]
BYTE2 = [0, 1, 0, 0, 0, 0, 0, 0]
BYTE3 = [1, 1, 0, 0, 0, 0, 0, 0]
BYTE4 = [0, 0, 1, 0, 0, 0, 0, 0]


def memory(bit_count_or_init: int | str | list | tuple) -> Mem:
    """
    The Idiomatic interface is for rich memory construction. This is a utility
    function since mixing the Idiomatic and Von Neumann would be no good.
    """
    mem = Mem()
    if isinstance(bit_count_or_init, int):
        mem.bits = [0] * bit_count_or_init
    elif isinstance(bit_count_or_init, (str, list, tuple)):
        mem.bits = list(int(i) for i in bit_count_or_init)
    return mem


def get_bit(init, index, sliced, bit_order, byte_order, msg):
    mem = memory(init)
    mem_slice = op_get_bit(mem, index, bit_order, byte_order)
    assert mem_slice.bits == memory(sliced).bits


# get_bit(BYTE1 * 2, 8, [1], L2R, R2L, 'First bit of second byte')
get_bit(BYTE1 * 2, 8, [0], R2L, L2R, 'First bit of second byte')
