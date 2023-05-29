op_ensure_bit_length
op_ensure_byte_length
op_concatenate
op_extend
repr_byte
repr_byte_in_universe
op_transform
op_reverse
op_reverse_bytes
op_reverse_bits
op_identity
iterate_logical_bits
validate_memory
op_bit_length
op_byte_length
op_get_bit
op_get_byte
op_get_bits
op_get_bytes
op_set_bit
op_set_bits
op_set_byte
op_set_bytes

# TODO(pbz): make a graph of the state machine or at least logical flow of the
# TODO(pbz): operations.
# TODO(pbz): Perhaps all languages are actually IRs. Perhaps this is the only
# TODO(pbz): way forward. This would make sense because languages compile to C,
# TODO(pbz): Jakt compiles to C++, etc. Perhaps languages stack on each other
# TODO(pbz): like a pipeline of IRs within a compiler. Decoupling them could be
# TODO(pbz): a way forward. Perhaps Handmade Network was right, perhaps making
# TODO(pbz): new languages should be dead simple. Perhaps they are all dialects
# TODO(pbz): in a pluggable programmable compilation pipeline.

(iterate_logical_bits)
(validate_memory)
op_bit_length
op_byte_length
op_transform
  op_identity
  op_reverse

