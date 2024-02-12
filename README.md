# tidbytes

> **Memory manipulation reimagined with bit addressing**

> Bit & byte manipulation library

# Fully Under Construction (Made Public To Reduce Risk Of Name Squatting)

**Need to create a graph that is the tree of re-implementation so that all the
operations can be created in order in another language.**

# Operation Hierarchy

> Represents a tree of re-implementation so that porting can be performed
    methodically.

```mermaid
graph TD;
    subgraph Operation API Design
        direction LR
        mem1{{Mem}}
        mem2{{Mem}}
        mem1 -- input --> op -- output --> mem2
    end
```


```mermaid
graph TD;
    subgraph Memory Transformation Operations
        _1[[op_transform]]
        op_identity --> _1
        op_reverse --> _1
        op_reverse_bits --> _1
        op_reverse_bytes --> _1
    end
```

```mermaid
graph TD;
    subgraph Host Language Specific Meta Operations
        meta_op_bit_length
        meta_op_byte_length
        validate_memory
        iterate_logical_bits
    end
```

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

```mermaid
graph RL;
    subgraph Fundamental Memory Read And Write Operations
        %% direction RL
        op_get_bit --> op_get_bits
        op_get_byte --> op_get_bits
        op_get_bytes --> op_get_bits
        op_get_bits

        op_set_bit --> op_set_bits
        op_set_byte --> op_set_bits
        op_set_bytes --> op_set_bits
        op_set_bits
    end
```

```mermaid
graph TD;
    subgraph Transformation Operations In Program's Memory Universe
        direction LR
        op_ensure_bit_length --> op_extend
        op_ensure_byte_length --> op_ensure_bit_length
        op_concatenate
    end
```

```mermaid
graph RL;
    subgraph API Design Layers
        direction LR

        idiomatic("`
            **Language Specific
            Idiomatic Interface**
            *(High Level API)*
        `")

        natural("`
            **Language Agnostic Interface
            Based On Von Neumann Architecture**
            *(Low Level API)*
        `")
    end

    vonn_type{{"`
        **Von Neumann Type**
        *(Language Specific)*
    `"}}

    idio_type{{"`
        **Idiomatic Type**
        *(Language Specific)*
    `"}}

    idiomatic ==> natural
    vonn_type --> natural
    idio_type --> idiomatic
    vonn_type --> idiomatic
```

```mermaid
graph LR;
    subgraph Host Language Specific Von Neumann API
        rgn{{MemRgn Type}}
    end
```

```mermaid
graph LR;
    subgraph Host Language Specific Idiomatic API
        mem{{Mem Type}}
    end
```

<!-- https://mermaid.js.org/syntax/flowchart.html#styling-line-curves -->
```mermaid
%%{ init: { 'flowchart': { 'curve': 'basis' } } }%%
graph LR;
    subgraph "Many Input Types, Only One Output Type"
        subgraph Higher Level Types
            _6{{"list[bit]"}}
            _7{{"list[byte]"}}
            _8{{"list[u8]"}}
            _9{{"list[i64]"}}
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
        _9{{"list[i64]"}} ---- Mem
        _14{{i8}} --- Mem
        _4{{ascii}} ---- Mem
        _15{{i16}} --- Mem
    end
```

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

# Operation Notes

- When given a destination bit width of 0, this is like multiplying by 0 in
    arithmetic and results in truncation to null (no bit width).
- Codecs can never start with `op_` since that would mean they are part of an
- algebra. This is fine, but they are not compatible with the Von Neumann API.

# Hmmm

The dream of Tidbytes is to allow bits to be place precisely where they are
wanted. In the pursuit of mapping this ideal to idiomatic types, some in-built
concepts were uncovered. There really seems to be some fundamental types in
relation to mapping numeric data to bits. "Type" here means an operation either
assuming metadata about an input or an operation requiring metadata as a meta
input. This represents an orientation that points away from the operation and
towards an operation respectively. Some concepts I've uncovered are:

- Unsized data (no fixed bit length to limit input data)
- Sized data (bit length)
- Natural data (raw/untyped/uninterpreted/unmapped memory)
- Numeric data (mathematical identity or quantity)
- Unsigned numbers (one axis)
- Signed numbers (two axes)
