from ..tools import sort_and_encode


def test_sort_and_encode():
    obj = {
       'b': 'value',
       'c': 'value',
       'a': 'value',
    }
    assert sort_and_encode(obj) == b'{"a":"value","b":"value","c":"value"}'
