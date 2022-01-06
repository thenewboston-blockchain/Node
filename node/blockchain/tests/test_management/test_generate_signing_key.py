import re
from io import StringIO

from django.core.management import call_command


def test_generate_node_signing_key():
    out = StringIO()
    call_command('generate_signing_key', stdout=out)
    assert re.match(r'^[0-9a-f]{64}$', out.getvalue().rstrip('\n'))
