import json
import re

import pytest
from pydantic import ValidationError

from node.blockchain.inner_models import (
    NodeDeclarationSignedChangeRequest, NodeDeclarationSignedChangeRequestMessage, SignedChangeRequest
)
from node.blockchain.mixins.crypto import HashableStringWrapper
from node.blockchain.tests.test_models.base import CREATE, VALID, node_declaration_message_type_validation_parametrizer


def test_create_from_node_declaration_signed_change_request_message(
    node_declaration_signed_change_request_message, regular_node_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=regular_node_key_pair.private,
    )
    assert isinstance(signed_change_request, NodeDeclarationSignedChangeRequest)
    assert signed_change_request.message == node_declaration_signed_change_request_message
    assert signed_change_request.signer == regular_node_key_pair.public
    assert signed_change_request.signature == (
        'e6f950cce5fbe79ebc58dbd317ba7dec5baf6387bfeeb4656d73c8790d2564a4'
        '44f8c702b3e3ca931b5bb6e534781a135d5c17c4ff03886a80f32643dbd8fe0d'
    )


def test_serialize_and_deserialize_node_declaration(
    regular_node_declaration_signed_change_request, regular_node_key_pair
):
    assert isinstance(regular_node_declaration_signed_change_request, NodeDeclarationSignedChangeRequest)
    serialized = regular_node_declaration_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, NodeDeclarationSignedChangeRequest)
    assert deserialized.signer == regular_node_declaration_signed_change_request.signer
    assert deserialized.signature == regular_node_declaration_signed_change_request.signature
    assert deserialized.message == regular_node_declaration_signed_change_request.message
    assert deserialized == regular_node_declaration_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


def test_node_does_not_serialize_identifier(regular_node_declaration_signed_change_request, regular_node_key_pair):
    assert isinstance(regular_node_declaration_signed_change_request, NodeDeclarationSignedChangeRequest)
    serialized = regular_node_declaration_signed_change_request.dict()
    assert 'identifier' not in serialized['message']['node']

    serialized_json = regular_node_declaration_signed_change_request.json()
    serialized = json.loads(serialized_json)
    assert 'identifier' not in serialized['message']['node']


def test_signature_validation_node_declaration(
    node_declaration_signed_change_request_message, primary_validator_key_pair
):
    signed_change_request_template = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(
        message=node_declaration_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    with pytest.raises(ValidationError) as exc_info:
        NodeDeclarationSignedChangeRequest(
            signer=signed_change_request_template.signer,
            signature='0' * 128,
            message=signed_change_request_template.message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)

    with pytest.raises(ValidationError) as exc_info:
        NodeDeclarationSignedChangeRequest(
            signer='0' * 64,
            signature=signed_change_request_template.signature,
            message=signed_change_request_template.message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)

    message = NodeDeclarationSignedChangeRequestMessage(
        node=signed_change_request_template.message.node,
        account_lock='0' * 64,
        type=signed_change_request_template.message.type,
    )
    with pytest.raises(ValidationError) as exc_info:
        NodeDeclarationSignedChangeRequest(
            signer=signed_change_request_template.signer,
            signature=signed_change_request_template.signature,
            message=message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)


@node_declaration_message_type_validation_parametrizer
def test_type_validation_for_node_declaration_message_on_parsing(
    id_, regular_node, node, node_identifier, node_addresses, node_fee, account_lock, search_re
):
    if node is CREATE and node_identifier is not VALID:  # Skip not applicable tests
        return

    regular_node_dict = regular_node.dict()
    del regular_node_dict['identifier']
    serialized = {
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type':
                1,
            'account_lock':
                regular_node.identifier if account_lock is VALID else account_lock,
            'node':
                regular_node_dict if node is VALID else ({
                    'addresses': regular_node.addresses if node_addresses is VALID else node_addresses,
                    'fee': regular_node.fee if node_fee is VALID else node_fee,
                } if node is CREATE else node)
        }
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(ValidationError) as exc_info:
        SignedChangeRequest.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


@pytest.mark.parametrize(
    'id_, signer, signature, type_, search_re',
    (
        # signer
        (1, None, '0' * 128, 1, r'signer.*none is not an allowed value'),
        (2, 1, '0' * 128, 1, r'signer.*str type expected'),
        (3, '', '0' * 128, 1, r'signer.*ensure this value has at least 64 characters'),
        (4, 'ab', '0' * 128, 1, r'signer.*ensure this value has at least 64 characters'),

        # signature
        (5, '0' * 64, None, 1, r'signature.*none is not an allowed value'),
        (6, '0' * 64, 1, 1, r'signature.*str type expected'),
        (7, '0' * 64, '', 1, r'signature.*ensure this value has at least 128 characters'),
        (8, '0' * 64, 'ab', 1, r'signature.*ensure this value has at least 128 characters'),

        # type_
        (9, '0' * 64, '0' * 128, None, r'type.*none is not an allowed value'),
        (10, '0' * 64, '0' * 128, '', r'type.*value is not a valid integer'),
        (11, '0' * 64, '0' * 128, '1', r'type.*value is not a valid integer'),
        (12, '0' * 64, '0' * 128, 0, r'GenesisSignedChangeRequest.*field required'),
        (13, '0' * 64, '0' * 128, 1000, r'type.*value is not a valid enumeration member'),
        (14, '0' * 64, '0' * 128, -1, r'type.*value is not a valid enumeration member'),
    )
)
def test_type_validation_for_node_declaration_on_parsing(id_, regular_node, signer, signature, type_, search_re):
    node = regular_node.dict()
    del node['identifier']
    serialized = {
        'signer': signer,
        'signature': signature,
        'message': {
            'type': type_,
            'account_lock': regular_node.identifier,
            'node': node
        }
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(ValidationError) as exc_info:
        SignedChangeRequest.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)


def test_hashing_does_not_include_node_identifier(regular_node_declaration_signed_change_request):
    request_dict = regular_node_declaration_signed_change_request.dict()

    assert 'identifier' not in request_dict['message']['node']
    hashing_string = json.dumps(request_dict, separators=(',', ':'), sort_keys=True)
    expected_hash = HashableStringWrapper(hashing_string).make_hash()

    assert regular_node_declaration_signed_change_request.make_hash() == expected_hash
