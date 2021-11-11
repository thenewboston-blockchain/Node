from django.conf import settings


def test_settings_smoke():
    assert hasattr(settings, 'NODE_SIGNING_KEY')


def test_env_var_override():
    assert getattr(settings, 'FOR_UNITTESTS_DISREGARD_OTHERWISE', None) == {1: 'for unittests'}  # noqa: B009
