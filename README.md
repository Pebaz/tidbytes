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
        %% direction RL
        op_bit_length
        op_byte_length
        validate_memory
        iterate_logical_bits
    end
```
