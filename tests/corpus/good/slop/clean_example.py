"""A clean module the slop gate must not flag."""


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def test_add_returns_sum():
    assert add(2, 3) == 5
