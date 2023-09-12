from contextlib import contextmanager
from pytest import raises

@contextmanager
def closure():
    yield

def raises_exception(expected_exception) -> object:
    if expected_exception:
        return raises(expected_exception)
    else:
        return closure()
