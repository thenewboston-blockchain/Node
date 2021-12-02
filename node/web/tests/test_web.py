import pytest
from django.test import override_settings
from django.urls import reverse

from node.web.templatetags.node_extras import get_node_identifier


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
def test_web_view(web_client):
    response = web_client.get(reverse('web'))
    assert response.status_code == 200
    assert 'Admin panel' in response.rendered_content
    assert f'<title>thenewboston node {get_node_identifier()}</title>' in response.rendered_content
