# tidbytes

> Bit & byte manipulation library

# TODO(pbz):

**Need to create a graph that is the tree of re-implementation so that all the
operations can be created in order in another language.**

# Operation Hierarchy

> Represents a tree of re-implementation so that porting can be performed
    methodically.

```mermaid
graph TD;
    subgraph Memory Transformation Operations
        op_identity --> op_transform
        op_reverse --> op_transform
        op_reverse_bits --> op_transform
        op_reverse_bytes --> op_transform
    end
```

```mermaid
graph TD;
    subgraph Host Language Specific Meta Operations
        op_bit_length
        op_byte_length
        validate_memory
        iterate_logical_bits
    end
```

```mermaid
graph TD;
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
graph LR;
    subgraph Host Language Specific Von Neumann API
        rgn[MemRgn Type]
    end
```

```mermaid
graph LR;
    subgraph Host Language Specific Idiomatic API
        mem[Mem Type]
    end
```



