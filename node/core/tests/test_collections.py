import pytest

from node.core.utils.collections import deep_get, deep_set


def test_deep_get():
    assert deep_get({'a': 1}, ('a',)) == 1
    assert deep_get({'a': {'b': 2}}, ('a', 'b')) == 2
    assert deep_get({'a': {'b': {'c': 3}}}, ('a', 'b', 'c')) == 3
    assert deep_get({'a': {'b': {'c': 3}}}, ('a', 'b')) == {'c': 3}

    with pytest.raises(ValueError, match='Not enough nesting'):
        deep_get({'a': 1}, ('a', 'b'))

    with pytest.raises(ValueError, match='Not enough nesting'):
        deep_get({'a': {'b': ['v']}}, ('a', 'b', 'c'))


@pytest.mark.parametrize(
    'target, keys, value', (
        ({
            'a': 1
        }, ('a',), 2),
        ({
            'a': {
                'b': 2
            }
        }, ('a', 'b'), 3),
        ({
            'a': {
                'b': {
                    'c': 3
                }
            }
        }, ('a', 'b', 'c'), 4),
        ({
            'a': {
                'b': {
                    'c': 3
                }
            }
        }, ('a', 'b', 'x', 'd', 'e', 'f'), 4),
        ({
            'a': {
                'b': {
                    'c': 3
                }
            }
        }, ('a', 'b'), 5),
        ({
            'a': 1
        }, ('a', 'b'), ValueError),
        ({
            'a': {
                'b': ['v']
            }
        }, ('a', 'b', 'c'), ValueError),
    )
)
def test_deep_set(target, keys, value):
    if value is ValueError:
        with pytest.raises(ValueError, match='Not enough nesting'):
            deep_set(target, keys, value)
    else:
        deep_set(target, keys, value)
        assert deep_get(target, keys) == value
