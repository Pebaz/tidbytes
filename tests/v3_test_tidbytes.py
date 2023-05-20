"""
Trying to keep a running total of the considerations that I've run into:

- Bytes are the only portable type
- Byte order
- Bit order
- Memory transformations between universes
- Partial bytes & over-fetching & over-setting
- Exclusive or inclusive start/stop indices for getting/setting ranges

---

Help me design a bit manipulation library. I don't want you to mention the
choice of language as it is unimportant. I am stuck on the problem of how to
handle partial bytes.

Normally, bit manipulation is performed on various sizes of integers. My library
uses lists of ints where each int represents 1 or 0. Those lists are only a max
of 8 bits so entire memory regions will be a list of lists of bits.

The problem is that when specifying memory regions that are not divisible by 8,
I don't know how to handle bit and byte order.

Bit order exists. Byte order exists and is often expressed as little and big
endian. However, I've found that endianness is irrelevant to my library. I just
want to put bits where I want them to be period. As far as my library is
concerned, there is left to right and right to left bit order and byte order.

When getting a bit from a memory region, that memory region exists in memory
raw. However, it is not straightforward to answer the question: "what is the 9th
bit?" due to the bit and byte order.

I have figured out how to get the 9th bit for both left to right and right to
left bit and byte order, but that is only for memory regions that have a length
that is evenly divisible by 8.

I discovered that left to right byte order means the memory is unchanged. Right
to left byte order means a logical transformation where all the bytes (but not
bits) are reversed.

Normally, they would go left to right byte order and you'd read each bit
starting from the left or right depending on bit order. However, what happens
when you first transform the bytes from right to left (reversing them) and then
start reading bits? There's a logical gap of 4 bits. What do I do with that 4
bit gap?

---

I figured it out: I need `op_transform(bit_order, byte_order)`

If I create this operation, all indexing and setting operations are trivial. For
the purposes of this initial implementation, I need to use lists of lists of
bits along with null values so that I can just skip empty bits in partial bytes.

I have created some sort of operation that I don't know the name of:

Transform Byte Order To L2R, Transform Bit Order To L2R = >>
Byte Order To R2L, Bit Order To R2L = <<
Bytes To L2R, Bits To R2L = ><
Bytes R2L, Bits L2R = <>

In other words, the first arrow is the byte order, the second is the bit order.
This ordering is because byte order always happens first. I haven't figured out
if this actually matters.

rgn = Memory Region
>> rgn = Identity operation (does nothing) (`op_identity()`)
<< rgn = Inverse operation (`op_reverse()`)
<> rgn = Reverse bytes, keep bits (`op_reverse_bytes()`)
>< rgn = Keep bytes, reverse bits (`op_reverse_bits()`)

Notation:

The top arrow is the byte order. The bottom arrow is the bit order. This
notation matches the `>>` syntax and the order corresponds to it also. Since
these symbols conflict with bit shifting syntax, a line could be added that
makes them more into arrows and gives the impression that the first arrow is
bigger which matches the canonicalized representation: `->>` `-<>`, `-><`, `-<<`

      -->               -->
1 1 1 1 0 0 0 0   1 0 1 0 . . . .
>                 >

Example Operation:
1 1 1 1 0 0 0 0   1 0 1 0 . . . . <>= 1 0 1 0 . . . .   1 1 1 1 0 0 0 0

Ninth Bit:
1 1 1 1 0 0 0 0   1 0 1 0 . . . .
                  ^

9th bit of: <> 1 1 1 1 0 0 0 0   1 0 1 0 . . . .
    1 0 1 0 . . . .   1 1 1 1 0 0 0 0
                              ^  <- Trivial due to transformation operations!!
"""

import pytest
from typing import *
from tidbytes import *

HALF_BYTE = [0, 1] * 2
BYTE = HALF_BYTE * 2
BYTE_AND_HALF = BYTE + HALF_BYTE
BYTE_X2 = BYTE * 2
L2R = Order.LeftToRight
R2L = Order.RightToLeft

HALF = [1, 0, 1, 0]
BYTE1 = [1, 0, 0, 0, 0, 0, 0, 0]# , [1, 0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0]
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


def index_to_byte_offset(
    bit_index: int,
    bit_len: int,
    bit_order: Order,
    byte_order: Order
) -> int:
    """
    This function assumes that:
    - 'First bit' is within 'First byte'
    - 'Ninth bit' is within the 'Second byte'
    - 'First byte' is the 'First byte'
    - 'Second byte' is after the 'First byte' according to the byte order
    - The input bit index is within the logical memory region
    - The output bit index plugs into the physical memory region

    You can emulate byte indices by making sure the bit index is divisible by 8.
    """

    # TODO(pbz): Current thought? Store bytes as list of bits. Store list of bytes
    # TODO(pbz): There needs to be a universal calculation of what exact bit an
    # TODO(pbz): index corresponds to <-- If so, you could just iterate

    # ! Current status: How to handle partial bytes

    """
    Byte L2R: 1 0 0 1 1 1 1 1   1 0 0 0 0 0 0 1   1 1 1 1 0 0 0 0
    Byte R2L: 1 1 1 1 0 0 0 0   1 0 0 0 0 0 0 1   1 0 0 1 1 1 1 1

    Byte L2R: 1 0 0 1 1 1 1 1   1 0 0 0 0 0 0 1   1 1 1 1 <- Partial bytes...?
    Byte R2L: 1 1 1 1 1 0 0 0   0 0 0 1 1 0 0 1   1 1 1 1 <- Wow. How to handle?
    Byte R2L:         1 1 1 1   1 0 0 0 0 0 0 1   1 0 0 1 1 1 1 1

    R2L, L2R: 1 0 0 1 1 1 1 1   1 0 0 0 0 0 0 1   1 1 1 1 0 0 0 0
    R2L, L2R: 1 1 1 1 1 0 0 1   1 0 0 0 0 0 0 1   0 0 0 0 1 1 1 1
    """


# TODO(pbz): Move this to the idiomatic interface and make it a utility function
def repr_byte(byte: list[int], bit_order: Order, byte_order: Order):
    bit_range = range(len(byte))
    if bit_order == Order.RightToLeft:
        bit_range = reversed(bit_range)

    first_line = ''.join(str(bit).ljust(3) for bit in byte)
    second_line = ''.join(str(i).ljust(3) for i in bit_range)

    third_line_slots = ['   ' for i in range(len(byte))]

    if byte_order == Order.RightToLeft:
        for byte_index, bit_index in enumerate(range(0, len(byte), 8)):
            index = len(byte) - 1 - bit_index
            if index < len(third_line_slots):
                third_line_slots[index] = str(byte_index).ljust(3)
    else:
        for byte_index, bit_index in enumerate(range(0, len(byte), 8)):
            index = bit_index
            if index < len(third_line_slots):
                third_line_slots[index] = str(byte_index).ljust(3)

    third_line = ''.join(third_line_slots)

    raise Exception('^^^ UGH this is still wrong! It needs to reorder the bits according to the byte order! ^^^')

    # ! Essentially, I thought this was a visualization of where the bit and
    # ! byte indices would start and the direction they grow in. It's not.
    # ! It needs to off of the BYTES not the BITS.
    # ! This means the bytes need to be reordered to fit the byte order and each
    # ! individual group of bits needs to be reordered to match the byte order.

    return f' Bit Val: {first_line}\n Bit Idx: {second_line}\nByte Idx: {third_line}'



def test_repr_byte():
    a = [0, 0, 0, 0, 0, 0, 0, 1]
    b = [0, 0, 0, 0, 0, 0, 1, 1]
    c = [0, 0, 0, 0, 0, 1, 1, 1]

    assert repr_byte(a * 3, L2R, L2R) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  1  \n'
        ' Bit Idx: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 \n'
        'Byte Idx: 0                       1                       2                       '
    )

    assert repr_byte(a + b + c, R2L, L2R) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  0  1  1  0  0  0  0  0  1  1  1  \n'
        ' Bit Idx: 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9  8  7  6  5  4  3  2  1  0  \n'
        'Byte Idx: 0                       1                       2                       '
    )

    assert repr_byte(a + b + c, L2R, R2L) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  0  1  1  0  0  0  0  0  1  1  1  \n'
        ' Bit Idx: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 \n'
        'Byte Idx:                      2                       1                       0  '
    )

    assert repr_byte(a + b + c, R2L, R2L) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  0  1  1  0  0  0  0  0  1  1  1  \n'
        ' Bit Idx: 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9  8  7  6  5  4  3  2  1  0  \n'
        'Byte Idx:                      2                       1                       0  '
    )

    assert repr_byte([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], L2R, L2R) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  \n'
        ' Bit Idx: 0  1  2  3  4  5  6  7  8  9  10 11 12 \n'
        'Byte Idx: 0                       1              '
    )

    assert repr_byte([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], R2L, L2R) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  \n'
        ' Bit Idx: 12 11 10 9  8  7  6  5  4  3  2  1  0  \n'
        'Byte Idx: 0                       1              '
    )

    assert repr_byte([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], L2R, R2L) == (
        ' Bit Val: 0  0  0  0  0  0  0  1  0  0  0  0  0  \n'
        ' Bit Idx: 0  1  2  3  4  5  6  7  8  9  10 11 12 \n'
        'Byte Idx:             1                       0  '
    )


@pytest.mark.parametrize('init,index,sliced,bit_order,byte_order,msg', [
    (BYTE1, 0, [1], L2R, L2R, 'First bit'),
    (BYTE1, 0, [0], R2L, L2R, 'First bit'),
    (BYTE1, 0, [1], L2R, R2L, 'First bit'),
    (BYTE1, 0, [0], R2L, R2L, 'First bit'),

    (BYTE1, 7, [0], L2R, L2R, 'Last bit'),
    (BYTE1, 7, [1], R2L, L2R, 'Last bit'),
    (BYTE1, 7, [0], L2R, R2L, 'Last bit'),
    (BYTE1, 7, [1], R2L, R2L, 'Last bit'),

    (BYTE2, 6, [0], L2R, L2R, 'Second to last bit'),
    (BYTE2, 6, [1], R2L, L2R, 'Second to last bit'),
    (BYTE2, 6, [0], L2R, R2L, 'Second to last bit'),
    (BYTE2, 6, [1], R2L, R2L, 'Second to last bit'),

    (BYTE1 * 2, 8, [1], L2R, L2R, 'First bit of second byte'),
    (BYTE1 * 2, 8, [0], R2L, L2R, 'First bit of second byte'),
    (BYTE1 * 2, 8, [1], L2R, R2L, 'First bit of second byte'),
    (BYTE1 * 2, 8, [0], R2L, R2L, 'First bit of second byte'),

    (BYTE2 * 2, 9, [1], L2R, L2R, 'Second bit of second byte'),
    (BYTE2 * 2, 9, [0], R2L, L2R, 'Second bit of second byte'),
    (BYTE2 * 2, 9, [1], L2R, R2L, 'Second bit of second byte'),
    (BYTE2 * 2, 9, [0], R2L, R2L, 'Second bit of second byte'),

    # Does the same thing with half bytes:
    # (BYTE1 + HALF, 0, [1], L2R, L2R, 'First bit with half'),
    # (BYTE1 + HALF, 0, [0], R2L, L2R, 'First bit with half'),
    # (BYTE1 + HALF, 0, [0], L2R, R2L, 'First bit with half'),
    # (BYTE1 + HALF, 0, [0], R2L, R2L, 'First bit with half'),

    # (BYTE1 + HALF, 7, [0], L2R, L2R, 'Last bit with half'),
    # (BYTE1 + HALF, 7, [1], R2L, L2R, 'Last bit with half'),
    # (BYTE1 + HALF, 7, [0], L2R, R2L, 'Last bit with half'),
    # (BYTE1 + HALF, 7, [0], R2L, R2L, 'Last bit with half'),

    # (BYTE2 + HALF, 6, [0], L2R, L2R, 'Second to last bit with half'),
    # (BYTE2 + HALF, 6, [1], R2L, L2R, 'Second to last bit with half'),
    # (BYTE2 + HALF, 6, [1], L2R, R2L, 'Second to last bit with half'),
    # (BYTE2 + HALF, 6, [0], R2L, R2L, 'Second to last bit with half'),

    (BYTE1 * 2 + HALF, 8, [1], L2R, L2R, 'First bit of second byte with half'),
    (BYTE1 * 2 + HALF, 8, [0], R2L, L2R, 'First bit of second byte with half'),
    # TODO(pbz): This is the failing test:
    (BYTE1 * 2 + HALF, 8, [1], L2R, R2L, 'First bit of second byte with half'),
    # (BYTE1 * 2 + HALF, 8, [0], R2L, R2L, 'First bit of second byte with half'),

    # (BYTE2 * 2 + HALF, 9, [1], L2R, L2R, 'Second bit of second byte with half'),
    # (BYTE2 * 2 + HALF, 9, [0], R2L, L2R, 'Second bit of second byte with half'),
    # (BYTE2 * 2 + HALF, 9, [0], L2R, R2L, 'Second bit of second byte with half'),
    # (BYTE2 * 2 + HALF, 9, [0], R2L, R2L, 'Second bit of second byte with half'),
])
def test_get_bit(init, index, sliced, bit_order, byte_order, msg):
    mem = memory(init)
    mem_slice = op_get_bit(mem, index, bit_order, byte_order)
    expected = f'{msg}:\n{repr_byte(init, bit_order, byte_order)}'
    assert mem_slice.bits == memory(sliced).bits, expected


# @pytest.mark.parametrize('init,start,stop,sliced,bit_order,byte_order,msg', [
#     # (BYTE, 0, 0, [], L2R, L2R, 'Empty range'),
#     # (BYTE, 0, 0, [], R2L, 'Empty range'),
#     # (BYTE, 0, 1, [0], L2R, 'Single element'),
#     # (BYTE, 0, 1, [1], R2L, 'Single element'),
#     # (BYTE, 0, 4, [0, 1, 0, 1], L2R, 'Full range'),
#     # (BYTE, 0, 4, [1, 0, 1, 0], R2L, 'Full range'),
#     # (BYTE, 0, 8, BYTE, L2R, 'Full byte'),
#     # (BYTE, 0, 8, [*reversed(BYTE)], R2L, 'Full byte'),
#     # (BYTE_AND_HALF, 0, 9, BYTE + [0], L2R, 'Byte boundary'),
#     # (BYTE_AND_HALF, 0, 10, BYTE + [0, 1], L2R, 'Byte boundary'),
#     # (BYTE_AND_HALF, 0, 9, [*reversed(BYTE)] + [1], R2L, 'Byte boundary'),
#     # (BYTE_AND_HALF, 0, 10, [*reversed(BYTE)] + [1, 0], R2L, 'Byte boundary'),
# ])
# def test_get_bits(init, start, stop, sliced, bit_order, byte_order, msg):
#     mem = memory(init)
#     mem_slice = op_get_bits(mem, start, stop, bit_order, byte_order)
#     assert mem_slice.bits == memory(sliced).bits, msg



# # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# # TODO(pbz): 🚨 Have to support bit order on byte operations since a number will
# # TODO(pbz): 🚨 have reverse byte order but not necessarily reverse bit order
# # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# # TODO(pbz): Wish there was a tool to generate map of control flow paths
# # TODO(pbz): Go back through each contract and test its interface
# # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# @pytest.mark.parametrize('init,start,stop,sliced,order,msg', [
#     (BYTE, 0, 0, [], L2R, 'Empty range'),
#     (BYTE, 0, 0, [], R2L, 'Empty range'),
#     (BYTE, 0, 1, BYTE, L2R, 'First byte'),
#     (BYTE, 0, 1, [*reversed(BYTE)], R2L, 'First byte'),
#     (BYTE_X2, 0, 1, BYTE, L2R, 'First byte'),
#     (BYTE_X2, 0, 1, [*reversed(BYTE)], R2L, 'First byte'),
#     (BYTE_X2, 0, 2, BYTE_X2, L2R, 'Two bytes'),
#     (BYTE_X2, 0, 2, [*reversed(BYTE_X2)], R2L, 'Two bytes'),
#     (BYTE_AND_HALF, 0, 1, BYTE, L2R, 'First byte'),
#     (BYTE_AND_HALF, 0, 1, [*reversed(BYTE)], R2L, 'First byte'),
#     (BYTE_AND_HALF, 0, 2, BYTE_AND_HALF, L2R, 'No padding bytes'),
#     (BYTE_AND_HALF, 0, 2, [*reversed(BYTE_AND_HALF)], R2L, 'No padding bytes'),
# ])
# def test_get_bytes(init, start, stop, sliced, order, msg):
#     mem = memory(init)
#     mem_slice = op_get_bytes(mem, start, stop, order)
#     assert mem_slice.bits == memory(sliced).bits, msg


@pytest.mark.parametrize('init,index,sliced,bit_order,byte_order,msg', [
    (BYTE1, 0, BYTE1, L2R, L2R, 'Only byte'),
    (BYTE1, 0, BYTE1[REV], R2L, L2R, 'Only byte'),
    (BYTE_AND_HALF, 1, HALF_BYTE, L2R, L2R, 'First byte'),
    (BYTE_AND_HALF, 1, HALF_BYTE[REV], R2L, L2R, 'First byte'),
    (BYTE_X2, 1, BYTE, L2R, L2R, 'Second byte'),
    (BYTE_X2, 1, BYTE[REV], R2L, L2R, 'Second byte'),
])
def test_get_byte(init, index, sliced, bit_order, byte_order, msg):
    mem = memory(init)
    mem_slice = op_get_byte(mem, index, bit_order, byte_order)
    assert mem_slice.bits == memory(sliced).bits, msg


# # TODO(pbz): Add more tests
# @pytest.mark.parametrize('init,offset,payload,result,order,msg', [
#     ([0] * 8, 4, [1, 0, 1, 0], [0] * 4 + [1, 0] * 2, L2R, 'First half byte'),
#     ([0] * 8, 4, [1, 0, 1, 0], [0, 1] * 2 + [0] * 4, R2L, 'R2L first half'),
#     ([0] * 8, 0, [1], [1] + [0] * 7, L2R, 'First bit'),
#     ([0] * 8, 0, [1], [0] * 7 + [1], R2L, 'First bit'),
#     ([0] * 8, 7, [1], [0] * 7 + [1], L2R, 'Last bit'),
#     ([0] * 8, 7, [1], [1] + [0] * 7, R2L, 'Last bit'),
#     ([0] * 8, 0, '10000011', '10000011', L2R, 'Entire range'),
# ])
# def test_set_bits(init, offset, payload, result, order, msg):
#     mem = memory(init)
#     mem_payload = memory(payload)

#     op_set_bits(mem, offset, mem_payload, order)

#     assert mem.bits == memory(result).bits, msg


# # TODO(pbz): Add more tests
# @pytest.mark.parametrize('init,offset,payload,result,order,msg', [
#     ([0] * 16, 1, [1, 0] * 4, [0] * 8 + [1, 0] * 4, L2R, 'Set 1 byte'),
#     ([0] * 16, 0, [1, 0] * 8, [1, 0] * 8, L2R, 'Set 2 bytes'),
# ])
# def test_set_bytes(init, offset, payload, result, order, msg):
#     mem = memory(init)
#     mem_payload = memory(payload)

#     op_set_bytes(mem, offset, mem_payload, order)

#     assert mem.bits == memory(result).bits, msg


# # TODO(pbz): Add more tests
# @pytest.mark.parametrize('init,offset,payload,result,order,msg', [
#     ([0] * 3, 0, [1], [1] + [0] * 2, L2R, 'Smaller than byte'),
#     ([0] * 12, 0, [1], [1] + [0] * 11, L2R, 'Crosses byte boundaries'),
#     ([0] * 3, 0, [1], [0] * 2 + [1], R2L, 'Smaller than byte'),
#     ([0] * 12, 0, [1], [0] * 11 + [1], R2L, 'Crosses byte boundaries'),
# ])
# def test_set_bit(init, offset, payload, result, order, msg):
#     mem = memory(init)
#     mem_payload = memory(payload)

#     op_set_bit(mem, offset, mem_payload, order)

#     assert mem.bits == memory(result).bits, msg


# # TODO(pbz): Add more tests
# @pytest.mark.parametrize('init,offset,payload,result,order,msg', [
#     ([0] * 12, 0, [1] * 8, [1] * 8 + [0] * 4, L2R, 'Within byte boundaries'),
#     ([0] * 18, 1, [1] * 8, [0] * 8 + [1] * 8 + [0] * 2, L2R, 'Second byte'),
# ])
# def test_set_byte(init, offset, payload, result, order, msg):
#     mem = memory(init)
#     mem_payload = memory(payload)

#     op_set_byte(mem, offset, mem_payload, order)

#     assert mem.bits == memory(result).bits, msg


# @pytest.mark.parametrize('closure,msg', [
#     (lambda: op_set_bytes(memory(8), 0, memory([1] * 3), L2R), 'Not a byte'),

#     (lambda: op_get_bit(memory(BYTE), -1, L2R), 'Negative index'),
#     (lambda: op_get_bit(memory(BYTE), 9, L2R), 'Index out of bounds'),
#     (lambda: op_get_bit(memory(BYTE), -1, R2L), 'Negative index'),
#     (lambda: op_get_bit(memory(BYTE), 9, R2L), 'Index out of bounds'),

#     (lambda: op_get_byte(memory(BYTE), -1, L2R), 'Negative index'),
#     (lambda: op_get_byte(memory(BYTE), 1, L2R), 'Index out of bounds'),
#     (lambda: op_get_byte(memory(BYTE), 9, L2R), 'Index out of bounds'),
#     (lambda: op_get_byte(memory(BYTE), -1, R2L), 'Negative index'),
#     (lambda: op_get_byte(memory(BYTE), 1, R2L), 'Index out of bounds'),
#     (lambda: op_get_byte(memory(BYTE), 9, R2L), 'Index out of bounds'),

#     (lambda: op_get_bits(memory(BYTE), -1, 0, L2R), 'Negative index'),
#     (lambda: op_get_bits(memory(BYTE), 0, 256, L2R), 'Stop > length'),
#     (lambda: op_get_bits(memory(BYTE), 8, 4, L2R), 'Stop < start'),
#     (lambda: op_get_bits(memory(BYTE), -1, 0, R2L), 'Negative index'),
#     (lambda: op_get_bits(memory(BYTE), 0, 256, R2L), 'Stop > length'),
#     (lambda: op_get_bits(memory(BYTE), 8, 4, R2L), 'Stop < start'),

#     (lambda: op_get_bytes(memory(BYTE), -1, 0, L2R), 'Negative index'),
#     (lambda: op_get_bytes(memory(BYTE), 0, 256, L2R), 'Stop > length'),
#     (lambda: op_get_bytes(memory(BYTE), 1, 0, L2R), 'Stop < start'),
#     (lambda: op_get_bytes(memory(BYTE), 1, 2, L2R), 'Start/Stop out of bounds'),
#     (lambda: op_get_bytes(memory(BYTE), -1, 0, R2L), 'Negative index'),
#     (lambda: op_get_bytes(memory(BYTE), 0, 256, R2L), 'Stop > length'),
#     (lambda: op_get_bytes(memory(BYTE), 1, 0, R2L), 'Stop < start'),
#     (lambda: op_get_bytes(memory(BYTE), 1, 2, R2L), 'Start/Stop out of bounds'),

#     (lambda: op_set_bit(memory(3), 0, memory([1] * 3), L2R), 'Not single bit'),
#     (lambda: op_set_bit(memory(3), -1, memory([1] * 3), L2R), 'Negative index'),
#     (lambda: op_set_bit(memory(3), 0, memory(0), L2R), 'Set with empty memory'),

#     (lambda: op_set_bytes(memory(16), 14, memory([1] * 3), L2R), 'Too big'),
#     (lambda: op_set_bytes(memory(16), 14, memory(0), L2R), 'Too small'),
#     (lambda: op_set_bytes(memory(16), 0, memory(17), L2R), 'Would not fit'),
#     (lambda: op_set_bytes(memory(16), -1, memory(17), L2R), 'Negative index'),
# ])
# def test_contracts(closure, msg):
#     # Would use pytest.raises but need to attach a custom message
#     try:
#         closure()
#         raise AssertionError(f'Did not raise ({msg})')
#     except MemException:
#         pass
