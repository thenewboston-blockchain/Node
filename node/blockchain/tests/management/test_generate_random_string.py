from io import StringIO

from django.core.management import call_command

from node.blockchain.management.commands.generate_random_string import SPECIAL_CHARS


def test_generate_random_string_without_special_characters():
    out = StringIO()
    call_command('generate_random_string', 32, stdout=out)
    random_string = out.getvalue().strip('\n')
    assert len(random_string) == 32
    assert not set(random_string).intersection(SPECIAL_CHARS)


def test_generate_random_string_with_special_characters():
    out = StringIO()
    call_command('generate_random_string', 32, special=True, stdout=out)
    random_string = out.getvalue().strip('\n')
    assert len(random_string) == 32
    assert set(random_string).intersection(SPECIAL_CHARS)
