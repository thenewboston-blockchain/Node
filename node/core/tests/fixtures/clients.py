import traceback
import types
from functools import partial
from unittest.mock import MagicMock, patch

import pytest
from django.test.client import Client
from requests.exceptions import HTTPError
from rest_framework.test import APIClient

from node.core.clients.node import NodeClient

TEST_SERVER_ADDRESS = 'http://testserver/'
MOCKED_ADDRESSES = (TEST_SERVER_ADDRESS,)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def web_client():
    return Client()


@pytest.fixture
def mocked_node_client():
    client = NodeClient()
    with patch.object(client, 'requests_post'), patch.object(client, 'requests_get'):
        yield client


def raise_for_status(self):
    if self.status_code >= 400:
        raise HTTPError()


def client_method_wrapper(substitute_callable, original_callable, url, *args, **kwargs):
    # We need to convert requests to Django test client interface here
    if not any(url.startswith(mocked_address) for mocked_address in MOCKED_ADDRESSES):
        return original_callable(url, *args, **kwargs)

    # Convert `json` to `data`
    json_ = kwargs.pop('json', None)
    if json_ is not None:
        kwargs['data'] = json_

    # Convert headers
    headers = kwargs.pop('headers', None)
    if headers:
        # TODO(dmu) LOW: Improve dealing with content type. Looks over engineered now
        content_type = headers.get('Content-Type')
        if content_type:
            kwargs['content_type'] = content_type
        kwargs.update(**headers)

    try:
        response = substitute_callable(url, *args, **kwargs)
    except Exception as ex:
        traceback.print_exc()

        response = MagicMock()
        response.status_code = 500
        response.content = f'(SIMULATED CONTENT for debug purposes only) Exception: {ex}'.encode('utf-8')

    response.raise_for_status = types.MethodType(raise_for_status, response)
    response.text = response.content.decode('utf-8')
    return response


@pytest.fixture
def smart_mocked_node_client(api_client):
    client = NodeClient()

    post_arguments = {
        'attribute': 'requests_post',
        'new': partial(client_method_wrapper, api_client.post, client.requests_post),
    }
    get_arguments = {
        'attribute': 'requests_get',
        'new': partial(client_method_wrapper, api_client.get, client.requests_get),
    }
    with patch.object(client, **post_arguments), patch.object(client, **get_arguments):
        yield client


@pytest.fixture
def force_smart_mocked_node_client(smart_mocked_node_client):
    with patch.object(NodeClient, '_instance', new=smart_mocked_node_client):
        yield


@pytest.fixture
def test_server_address():
    return TEST_SERVER_ADDRESS
