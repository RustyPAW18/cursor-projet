from cursor_personal.example import add


def test_add_basic():
    assert add(2, 3) == 5


def test_add_float():
    assert add(2.5, 0.5) == 3.0
