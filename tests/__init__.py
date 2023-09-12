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
