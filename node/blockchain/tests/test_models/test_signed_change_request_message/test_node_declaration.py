import json
import re

import pytest
from pydantic.error_wrappers import ValidationError

from node.blockchain.inner_models import Node, NodeDeclarationSignedChangeRequestMessage
from node.blockchain.mixins.crypto import SignableStringWrapper
from node.blockchain.types import Type

from ..base import CREATE, VALID, node_declaration_message_type_validation_parametrizer


def test_create_node_declaration_change_request_message(regular_node):
    message = NodeDeclarationSignedChangeRequestMessage(
        node=regular_node,
        account_lock=regular_node.identifier,
    )
    assert message.type == Type.NODE_DECLARATION


@pytest.mark.parametrize(
    'node_addresses', (
        [
            'https://not-existing-node-address-674898923.com:8555/',
            'http://127.0.0.1:8555/',
        ],
        [
            'http://not-existing-node-address-674898923.com:8555/',
            'mongodb://username:password@not-existing-node-address-674898923.com:27017/'
        ],
    )
)
def test_support_various_addresses(regular_node, node_addresses):
    node = Node(
        identifier=regular_node.identifier,
        addresses=node_addresses,
        fee=regular_node.fee,
    )

    message = NodeDeclarationSignedChangeRequestMessage(
        node=node,
        account_lock=regular_node.identifier,
    )
    assert message.type == Type.NODE_DECLARATION
    assert message.node.addresses == node_addresses


@node_declaration_message_type_validation_parametrizer
def test_type_validation_on_instantiation(
    id_, regular_node, node, node_identifier, node_addresses, node_fee, account_lock, search_re
):
    with pytest.raises(ValidationError) as exc_info:
        if node is VALID:
            node = regular_node
        elif node is CREATE:
            node = Node(
                identifier=regular_node.identifier if node_identifier is VALID else node_identifier,
                addresses=regular_node.addresses if node_addresses is VALID else node_addresses,
                fee=regular_node.fee if node_fee is VALID else node_fee,
            )
        account_lock = regular_node.identifier if account_lock is VALID else account_lock

        NodeDeclarationSignedChangeRequestMessage(
            node=node,
            account_lock=account_lock,
        )
    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


@node_declaration_message_type_validation_parametrizer
def test_type_validation_on_parsing(
    id_, regular_node, node, node_identifier, node_addresses, node_fee, account_lock, search_re
):
    serialized = {
        'account_lock':
            regular_node.identifier if account_lock is VALID else account_lock,
        'node':
            regular_node.dict() if node is VALID else ({
                'identifier': regular_node.identifier if node_identifier is VALID else node_identifier,
                'addresses': regular_node.addresses if node_addresses is VALID else node_addresses,
                'fee': regular_node.fee if node_fee is VALID else node_fee,
            } if node is CREATE else node)
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(ValidationError) as exc_info:
        NodeDeclarationSignedChangeRequestMessage.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


def test_signing_does_not_include_node_identifier(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    message = node_declaration_signed_change_request_message.dict()
    del message['node']['identifier']
    message_string = json.dumps(message, separators=(',', ':'), sort_keys=True)

    signing_key = regular_node_key_pair.private
    expected_signature = SignableStringWrapper(message_string).make_signature(signing_key)
    assert node_declaration_signed_change_request_message.make_signature(signing_key) == expected_signature
