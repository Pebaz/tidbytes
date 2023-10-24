# Test Suite

The test suite is a parametrized version of the tests so that reimplementations
of Tidbytes in other languages can test validity immediately over the entire set
of fundamental natural operations. Tidbytes was designed to be straightforward
to reimplement in other languages and its test suite mechanizes this.

# Idioms

Within the JSON test suite, the following conventions are used to construct data
for use within the tests. For each item in the `in` or `out` array, specific
data can be constructed by the host language according to the following table:

| Object Type | Syntax |
| - | - |
| Literal integer | `0` |
| ... | `[0]` |
| ... | `3.14` |
| Mem from bit length | `{"Mem": 0}` |
| Num from bit length | `{"Num": 0}` |
| Mem from bit list | `{"Mem": ["bit", 1, 0, 1, 0, 0]}` |
| Mem from byte list | `{"Mem": ["byte", 255, 255, 255]}` |

### Example

```json
{
    "version": "0.1.0",
    "tests": [
        {
            "op": "meta_op_bit_length",
            "in": [[1]],
            "out": [1],
            "tag": "Single bit, 7 unset bits"
        }
    ]
}
```
