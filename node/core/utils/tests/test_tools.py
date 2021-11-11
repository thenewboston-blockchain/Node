from ..tools import sort_and_encode


def test_sort_and_encode():
    assert sort_and_encode({'b': 'value', 'c': 'value', 'a': 'value'}) == b'{"a":"value","b":"value","c":"value"}'
