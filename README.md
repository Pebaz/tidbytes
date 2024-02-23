# Tidbytes Bit Manipulation Library

> **Memory manipulation reimagined with bit addressing**

Referring to the ninth bit of a region of memory should be trivial. It is, isn’t
it? It turns out that this is not as straightforward as it might seem. Depending
on the byte order, (referred to under the canonical moniker “endianness”), the
ninth bit may appear to the left or the right (not accounting for mixed
endianness) of the first bit (bit zero). The first byte should be the rightmost
byte for numeric data, but not when reading from a file for example. In this
case the first byte would be the leftmost byte. Because of all of this, I
designed Tidbytes to work specifically with bits as the primary addressable unit
of memory to provide clarity when working with memory from diverse sources.

The purpose of Tidbytes is to allow bits to be placed precisely where they are
wanted. In the pursuit of mapping this ideal to idiomatic types, some in-built
concepts were rediscovered. There really seems to be some fundamental types in
relation to mapping numeric data to bits. "Type" here refers to a collection of
related operations that either assumes metadata about an input or requires
metadata as a meta input. This represents an orientation that points away from
the operation and towards an operation respectively. Some concepts that relate
to operations that I've rediscovered are:

- **Unsized data** (inputs can be mapped to unlimited output data)
- **Sized data** (inputs can be mapped to output data limited by region size)
- **Natural data** (raw/untyped/uninterpreted/unmapped memory)
- **Numeric data** (mathematical identity or quantity)
- **Unsigned numbers** (axis with one polarity)
- **Signed numbers** (axis with two polarities)

These types are built into modern processor architectures via Bytes & Indices.
Tidbytes takes these natural computing concepts and provides 2 APIs:

- A lower level API designed to be easily re-implemented in other languages
- A higher level API designed to be as seamless as possible for Python
    programmers

```mermaid
graph TD;
    subgraph Operation API Design
        direction LR
        mem1{{Bytes}}
        mem2{{Bytes}}
        index{{Index}}
        mem1 -- input --> op -- output --> mem2
        index -- input --> op
    end
```

Each operation in the lower level API takes Bytes & Indices as input and
produces Bytes as output or Indices if it is a meta operation. Using just Bytes
and Indices, all memory manipulation operations can be implemented because
Indices can represent offsets, lengths, ranges, slices, and (un)signed numbers.


```mermaid
graph RL;
    subgraph API Design Layers
        direction LR

        idiomatic("`
            **Language Specific Idiomatic Interface**
            *(High Level API)*
        `")

        natural("`
            **Language Agnostic Natural Interface**
            *(Low Level API)*
        `")
    end

    natural_type{{"`
        **Natural Memory Type**
        *(Language Agnostic)*
    `"}}

    idio_type{{"`
        **Idiomatic Memory Type**
        *(Language Specific)*
    `"}}

    idiomatic ==> natural
    natural_type --> natural
    idio_type --> idiomatic
    natural_type --> idiomatic
```

## Idiomatic Higher Level API

The higher level "idiomatic" API provides these main types: `Mem`, `Unsigned`,
and `Signed`. The `Mem` type is the base type for all the other types and
provides the majority of the higher level functionality that will be comfortable
to Python programmers. It upholds contracts on invariants that are unique to
unsized or sized natural data in the form of raw bytes. The `Unsigned` type
upholds contracts on invariants unique to unsized or sized unsigned numeric
data. The `Signed` type upholds contracts on invariants unique to unsized or
sized signed numeric data.

```python
from tidbytes.idiomatic import *

mem = Mem[8]()  # <Mem [00000000]>
mem[0] = 1      # <Mem [10000000]>
mem[0:3]        # <Mem [100]>
mem += mem      # <Mem [10000000 10000000]>
mem[1::8]       # <Mem [10000000]>  Step by bytes

U2 = Unsigned[2]  # Type alias
def add(a: U2, b: U2) -> U2:
    return U2(a) + U2(b)

# Underflow and Overflow checks:
add(U2(2), U2(2))  # Error: 4 doesn't fit into bit length of 2 (min 0, max 3)

num = add(U2(2), U2(1))  # <Unsigned [11]>

# Fundamental type conversion support
int(num)  # 3
str(num)  # '11'
bool(num)  # True
float(num)  # 3.0
```

The idiomatic API provides these types:

```mermaid

graph RL;
signed[[Signed]] -- Inherits --> unsigned[[Unsigned]] -- Inherits --> mem[[Mem]]
```

Each of the higher level types can be constructed from most of the types shown
here, although some types like `Unsigned` cannot be given a negative big integer
or a `Signed` memory region.

<!-- https://mermaid.js.org/syntax/flowchart.html#styling-line-curves -->
```mermaid
%%{ init: { 'flowchart': { 'curve': 'basis' } } }%%
graph LR;
    subgraph "Many Input Types, Only One Output Type"
        subgraph Higher Level Types
            _6{{"list[bit]"}}
            _7{{"list[byte]"}}
            _8{{"list[u8]"}}
            _9{{"bool"}}
            _10{{int}}
            _4{{ascii}}
            _5{{utf8}}
        end

        %% Order matters here, they are interlieved
        _1{{u8}} --- Mem
        _10{{int}} ---- Mem
        _3{{f32}} --- Mem
        _5{{utf8}} ---- Mem
        _2{{i64}} --- Mem
        _6{{"list[bit]"}} ---- Mem
        _11{{u16}} --- Mem
        _7{{"list[byte]"}} ---- Mem
        _12{{u32}} --- Mem
        _8{{"list[u8]"}} ---- Mem
        _13{{u64}} --- Mem
        _9{{"bool"}} ---- Mem
        _14{{i8}} --- Mem
        _4{{ascii}} ---- Mem
        _15{{i16}} --- Mem
    end
```

## Natural Lower Level API

The lower level "natural" API is much more verbose and not designed to follow
Python idioms but rather to conceptually model C-equivalent semantics when
possible. Although demonstrated here, the lower level API is not designed with
any user experience features by design, as that is the express role of the
higher level API. The goal of the lower level API is to make it easier to port
to new languages.

Another feature that the natural API provides to the higher level API is the

```python
from tidbytes.natural import *
from tidbytes import codec

# The underlying backing store for bits is a list of list of bits.
# Obviously this is not the highest performance choice but the logical clarity
# it provided for this reference implementation could not be ignored
mem = codec.from_bit_list([1, 0, 1], 3)
assert mem.bytes == [[1, 0, 1, None, None, None, None, None]]

mem = op_concatenate(mem, mem)
assert mem.bytes == [[1, 0, 1, 1, 0, 1, None, None]]

mem = op_truncate(mem, 3)
assert mem.bytes == [[1, 0, 1, None, None, None, None, None]]

assert meta_op_bit_length(mem) == 3

# This codec assumes signed memory as input since Python ints are always signed
assert codec.into_numeric_big_integer(mem) == -3
```

Lower level API operations:

- `op_identity`: maps a memory region to itself (multiplies by 1)

- `op_reverse_bytes`: transforms little endian to big endian and vice versa

- `op_reverse_bits`: reverses the bits of each byte while maintaining byte order

- `op_reverse`: reverses both bits and bytes, effectively flipping the entire
    region

- `op_get_bits`: slices out a range of bits into another range of bits

- `op_set_bits`: sets a range of bits with another range of bits

- `op_truncate`: remove additional space if greater than provided length

- `op_extend`: fill additional space with a value if less than provided length

- `op_ensure_bit_length`: fill or remove space if less or greater than length

- `op_concatenate`: combine two memory regions from left to right

Here is a diagram that shows dependencies between operations so that they can
be re-implemented in order in another language:

<!-- TODO(pbz): Add the rest of the operations -->
<!-- ? Codecs as well? Mention them anywhere? -->

```mermaid
mindmap
    root("
        Tree Of Re-
        Implementation
    ")
        op_transform
            op_identity
            op_reverse
            op_reverse_bytes
            op_reverse_bits
        op_get_bits
            op_get_bit
            op_get_byte
            op_get_bytes
        op_set_bits
            op_set_bit
            op_set_byte
            op_set_bytes
        meta_op_bit_length
            meta_op_byte_length
```


<!-- TODO(pbz): Add the rest of them here including meta ops -->




# The Ninth Bit

<!-- TODO(pbz): Big problem: 8 bit bytes are not from theory/comp or Neumann -->
<!-- TODO: refactor all of this to account for that. -->

<!-- TODO(pbz): Remove "algebra" -->
<!-- TODO(pbz): Remove "Von Neumann" -->

<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->
<!-- * GOOD STARTING HERE -->

↪ Reasoning about the ninth bit within the context of programming computers is
not as straightforward as it might seem. It entails preconceived notions on the
part of the programmer about how the runtime CPU architecture loads bits into
registers as well as assumptions around the origin of those bits. The ability to
refer to singular bits is not a capability natural to modern computer
architectures due to byte addressing, but there is utility in doing so
nonetheless. Some applications of referring to bits is data format encoding,
structure bit fields and layout, and machine code instruction encoding. As such,
to get around the limitation of bytes as the lone addressable unit of memory,
bit locations are calculated at runtime through the use of arithmetic and bit
shifting. This is due to the limitations in the available instructions to the
assembly programmer. However, as will be seen below, thinking past this
limitation in a higher level of software provides logical coherency that could
aid application programmers when integrating with lower level libraries,
operating systems, and hardware.

## Glossary of Terms

- **Natural**: Refers to the bit (and most commonly) byte order of a given
    processor architecture: the memory universe. It is from the point of view of
    the host.

- **Foreign**: Refers to a memory universe of another processor host, regardless
    if it exactly matches.

- **Origin**: Refers to which memory universe a memory region was allocated.

## Identity Order

> ***Tidbytes is based off of the concept of Identity Order which means the
first bit is always the leftmost bit of the leftmost byte.***

When both the bit and byte order of a region of memory is left to right, this is
called “Identity Order” in Tidbytes.

<!-- TODO(pbz): Replace this diagram -->
```mermaid
flowchart LR;
    subgraph b[Byte 1]
        direction LR
        b0((0)) --> b1[0] --> b2[0] --> b3[0] --> b4[0] --> b5[0] --> b6[0]
        b6[0] --> b7[0]
    end
    subgraph a[Byte 0]
        direction LR
        a0((0)) --> a1[0] --> a2[0] --> a3[0] --> a4[0] --> a5[0] --> a6[0]
        a6[0] --> a7[0]
    end
    a ==> b
```

This is the most useful memory order for bit reading (indexing, offsetting) and
writing (set, concat, extend, truncate) operations because it matches most
mathematical notation such as equations and cardinal graphs. For memory in
identity order, it is unlikely to be semantically meaningful in a primitive
(scalar) way. Generally, memory in identity order tends to be for everything
*except* for directly storing data. Floats.

For identity order memory, the first and ninth bits are the leftmost bit of the
leftmost byte and the leftmost bit of the second byte from the left:

<!-- TODO(pbz): Replace this diagram -->
```mermaid
flowchart LR;
    subgraph b[Byte 1]
        direction LR
        b0[[0]] --> b1[0] --> b2[0] --> b3[0] --> b4[0] --> b5[0] --> b6[0]
        b6[0] --> b7[0]
    end
    subgraph a[Byte 0]
        direction LR
        a0[[0]] --> a1[0] --> a2[0] --> a3[0] --> a4[0] --> a5[0] --> a6[0]
        a6[0] --> a7[0]
    end
    a ==> b
    style a0 fill:#f9f,stroke:#333,stroke-width:4px
    style b0 fill:#f9f,stroke:#333,stroke-width:4px

    subgraph legend[Legend]
        direction TB
        _0[First Bit] --> a0
        _1[Ninth Bit] --> b0
    end
```

## Numeric Data

<!-- TODO(pbz): Replace this diagram -->
```mermaid
flowchart RL;
    subgraph b[Byte 1]
        direction LR
        b0((0)) --> b1[0] --> b2[0] --> b3[0] --> b4[0] --> b5[0] --> b6[0]
        b6[0] --> b7[0]
    end
    subgraph a[Byte 0]
        direction LR
        a0((0)) --> a1[0] --> a2[0] --> a3[0] --> a4[0] --> a5[0] --> a6[0]
        a6[0] --> a7[0]
    end
    a ==> b
```


<!-- TODO(pbz): I wish this wasn't bogus but it probably will be torn apart. -->
<!-- TODO: Just remove all mention of Neumann and make it about numeric data -->


## Memory Origin And Universes

Every memory region within a given program has an origin. Fundamental properties
of memory origin include bit and byte order. For the purposes of Tidbytes, only
pure left-to-right and right-to-left bit and byte orders are supported, leaving
split order as an future extension, should it prove it’s utility.

The most common orders are left-to-right (little endian) and right-to-left (big
endian). Big endian matches how numbers are written while little endian matches
zero-indexing of bytes.

Although it is commonly thought that bits always go from right-to-left, on
occasion they also go from left to right. This can be the case when slicing out
bit fields from structs that are smaller that a byte or otherwise cross byte
boundaries. In such cases, is the first bit on the far right or on the far left?
This is an intriguing duality. Memory origin does seem to matter then. When
considering the entire struct, the first bit is always the leftmost bit of the
leftmost byte. When considering numeric data, the first bit is the rightmost bit
of the rightmost byte. Strange.

The use case for transforming between memory universes often comes up when
reading from a file or a network socket. When reading bytes from a file, they
are read (logically) from left to right one at a time. These bytes come from an
entirely separate memory universe: the universe of the file format. Once they
have been read into memory, they are now within the memory universe of the
program, although they have not yet been transformed to identity order.

```mermaid
graph TD;
    subgraph Memory Universe Boundaries Require Transformation Operations
        direction LR

        _1(((Memory Universe 1)))
        _2(((Memory Universe 2)))
        op_transform
        _1 <===> op_transform <===> _2

        subgraph op_transform
            op_identity
            op_reverse
            op_reverse_bytes
            op_reverse_bits
        end
    end

    style op_transform fill:#9893bf,stroke:#5c5975
```

> ***Amazingly, simply applying a foreign memory region’s bit and byte order as
a transformation on itself produces that same region in identity order, easily
usable by the host program. This is a surprising insight which ensures that the
“first bit” is always the leftmost bit of the leftmost byte.***

# TLDR;

Take the origin of a region of memory and perform the corresponding memory
transformation operation to map it to identity order in the natural host CPU
memory so that bits and bytes are always from left to right.

| Foreign Order | Natural Order | Transformation Operation |
|---|---|---|
| Big Endian | Little Endian | `op_reverse_bytes` |
| Little Endian | Big Endian | `op_reverse_bytes` |
| Big Endian | Big Endian | `op_identity` (no op) |
| Little Endian | Little Endian | `op_identity` (no op) |

# So What Truly Is The “Ninth Bit”

By taking a foreign memory region and applying it’s own bit and byte order as a
transformation upon itself it yields a region with identity memory order,
wherein the “ninth bit” is always the leftmost bit of the second byte from the
left.

<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->
<!-- * GOOD ENDING HERE -->




# Extra Topics

If someone could refactor to use integers as backing store that would be great.

However, each individual byte is generally treated as a C `char` so it is
effectively a numeric value having right-to-left bit order and a pre-declared
byte order dictated by the file format.

show how to index bits in ASM and C operations

zero-indexing bytes

reverse indexing bytes for numeric values

Numeric: R2L bits, R2L bytes

LE Numeric: R2L bits, L2R bytes

Logical/Identity: L2R bits, L2R bytes

“Numeric Universe”.
