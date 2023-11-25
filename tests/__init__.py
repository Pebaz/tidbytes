from contextlib import contextmanager
from pytest import raises

def raises_exception(expected_exception) -> object:
    if expected_exception:
        return raises(expected_exception)
    else:
        @contextmanager
        def closure():
            yield
        return closure()

UN = None  # Unsized

# Helper type to test literal slice syntax without explicitly using `slice()`
Slice = type('Slice', tuple(), dict(__getitem__=lambda self, index: index))()
