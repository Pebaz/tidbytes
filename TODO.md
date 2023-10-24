# TODO

> What would it take to consider this project done?

- 🔰 Serialization to idiomatic primitive types
- 🔰 Expose fundamental natural operations as methods on `Mem`
- 🔰 Assign by index
- 🔰 Negative indexes
- 🔰 From hex string
- 🔰 From bin string
- 🔰 Test all methods from `Mem`
- 🔰 Test all methods from `Num`
- 🔰 Test all methods from `Str`
- 🔰 Test all methods from `Struct`
- 🔰 IEEE754 float as struct example
- 🔰 Struct alignment
- 🔰 Struct padding
- 🔰 Struct offset
- 🔰 Struct nested types
- 🔰 `F32` inherits `Struct` to have nested fields but support index
- 🔰 Rename "Von Neumann" to "Natural"
- 🔰 Does `Struct` even belong in Tidbytes or should it be moved to assembler?
    Perhaps only `Mem` and `Num` are needed in Tidbytes. After all, it is a
    memory manipulation algebra, not a library of data structures

# Aspirational Goals

- ⭐ Parametrize test suite
- ⭐ C++ implementation
- ⭐ Rust implementation
- ⭐ Refactor Python implementation to use bindings to C++ implementation for speed
