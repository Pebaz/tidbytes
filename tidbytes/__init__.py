"""
This is design iteration number 3.

Progress was made with iteration number 2 where the concepts Mem and Num were
established which determined bit and byte order deterministically. Namely, Mem
has left to right bit and byte order and Num has right to left bit order and
a byte order that matches the desired endianness. Without this insight, progress
could not be made so the effort involved with iteration 2 ultimately furthered
the goal of a universal, deterministic, and simple bit manipulation library.

The problems with iteration number 2 were that there are just too many different
ways to set bits and they need to be identified in order to move forward.
Specifically, getting (indexing), and setting (indexing and bit decoding) are
orthogonal, although setting builds on the indexing capability of getting.

Indexing memory is complicated because slicing out a range of bits/bytes needs
to work well with setting bits, but reassigning that slice to the original range
is nontrivial. Stepping should not be supported. Also, when setting an integer
data type to the sliced out range, the integer type needs to fit in that new
type but also fit back into the original range.

It would be better to just only allow getting and setting bits using the Mem
type only. Users could call from/into functions for get/set operations so there
would be minimal inconvenience. Catering to the C API doesn't seem to be the
right move here. If the Mem type is kept opaque from the point of view of the
API operations, it should be possible to only use that Mem type to get and set
bits and bytes: `mem.set_bytes(Mem.from_i32(123))`. This means that setting bits
needs to support:

:: Natural API ::
Mem <- get slice as Mem, set slice to number, set range within Mem to that slice

:: Idiomatic API ::
u8[] <- control explicit bit order no matter what
number <- convenience so that ints can be used to set bits

This may be the limit to the necessary complexity of this problem domain.

Furthermore, there seems to be 2 use cases:

- Language agnostic Natural API for getting/setting bits/bytes.
- Idiomatic Python API for structs, slicing, and indexing.

The Natural API closely follows C conventions in order to enable
reimplementation in many languages.

The Idiomatic API needs to be the smoothest experience possible since languages
can support very convenient syntax.

# Design Elements

The Natural API will return a memory slice of the same type as the normal
memory type when getting bits or bytes. There are no operations to get memory
and also convert it to language-specific types. That is what conversion methods
are for. Languages can implement any number of conversion functions as makes
sense in their language. Internally, the backing store for the bits could be
integers or an array of u8s in the range 0-1. Even getting one bit returns the
root memory type. Setting bits works the same way, the Natural API will only
accept the Mem type.

The Idiomatic API will be able to convert as many different types as makes sense
into the backing store type and vice versa.
"""

# ruff: noqa: F403: These imports are exported and need to be flexible
from .mem_types import *
from .natural import *
from .idiomatic import *
from .codec import *
