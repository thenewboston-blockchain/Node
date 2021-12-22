from io import StringIO

from django.core.management import call_command


def test_generate_node_signing_key():
    out = StringIO()
    call_command('generate_node_signing_key', stdout=out)
    assert len(out.getvalue().strip('\n')) == 64
