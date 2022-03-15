import pytest
from django.test import override_settings
from django.urls import reverse

from node.web.templatetags.node_extras import get_node_identifier


@pytest.mark.django_db
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
def test_web_view(web_client):
    response = web_client.get(reverse('web'))
    assert response.status_code == 200
    assert 'Admin panel' in response.rendered_content
    assert f'<title>thenewboston node {get_node_identifier()}</title>' in response.rendered_content


@pytest.mark.django_db
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
def test_docs_view(web_client):
    response = web_client.get(reverse('docs'))
    assert response.status_code == 200
    assert response.data['title'] == 'Node'
    assert response.template_name == 'drf_spectacular/swagger_ui.html'
