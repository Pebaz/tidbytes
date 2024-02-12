from contextlib import contextmanager
from pytest import raises

def raises_exception(expected_exception) -> object:
    if expected_exception:
        return raises(expected_exception)

    @contextmanager
    def closure():
        yield
    return closure()

UN = None  # Unsized

# Helper type to test literal slice syntax without explicitly using `slice()`
_slicer = lambda self, index: (
    slice(index, index + 1) if isinstance(index, int) else index
)
Slice = type('Slice', tuple(), dict(__getitem__=_slicer))()
