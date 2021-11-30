import json
import re

import pytest
from pydantic import ValidationError

from node.blockchain.inner_models import NodeDeclarationSignedChangeRequest, SignedChangeRequest
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
        '375a38f1934a3480e9db256d41b4dc19dfcbaaa5e7d8d6a1669e13bf5839bdbc'
        'b3c14b986beae1be2d10b855e1ab07a85699e61c87ff349f4ab8d55a1a67ef0c'
    )


@pytest.mark.skip('Not implemented yet')
def test_serialize_and_deserialize_node_declaration():
    # TODO(dmu) HIGH: Implement similar to `.test_genesis.test_serialize_and_deserialize_genesis_type`
    #                 https://thenewboston.atlassian.net/browse/BC-169
    raise NotImplementedError


@pytest.mark.skip('Not implemented yet')
def test_signature_validation_node_declaration():
    # TODO(dmu) HIGH: Implement similar to `.test_genesis.test_signature_validation_genesis_type`
    #                 https://thenewboston.atlassian.net/browse/BC-169
    raise NotImplementedError


@node_declaration_message_type_validation_parametrizer
def test_type_validation_for_node_declaration_message_on_parsing(
    id_, regular_node, node, node_identifier, node_addresses, node_fee, account_lock, search_re
):
    serialized = {
        'signer': '0' * 64,
        'signature': '0' * 128,
        'message': {
            'type':
                1,
            'account_lock':
                regular_node.identifier if account_lock is VALID else account_lock,
            'node':
                regular_node.dict() if node is VALID else ({
                    'identifier': regular_node.identifier if node_identifier is VALID else node_identifier,
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
        # TODO(dmu) HIGH: Make enum strict, so coerce strings are not allowed
        #                 https://thenewboston.atlassian.net/browse/BC-162
        # (11, '0' * 64, '0' * 128, '1', r'type.*value is not a valid integer'),
        (12, '0' * 64, '0' * 128, 0, r'GenesisSignedChangeRequest.*field required'),
        (13, '0' * 64, '0' * 128, 1000, r'type.*value is not a valid enumeration member'),
        (14, '0' * 64, '0' * 128, -1, r'type.*value is not a valid enumeration member'),
    )
)
def test_type_validation_for_node_declaration_on_parsing(id_, regular_node, signer, signature, type_, search_re):
    serialized = {
        'signer': signer,
        'signature': signature,
        'message': {
            'type': type_,
            'account_lock': regular_node.identifier,
            'node': regular_node.dict()
        }
    }
    serialized_json = json.dumps(serialized)
    with pytest.raises(ValidationError) as exc_info:
        SignedChangeRequest.parse_raw(serialized_json)

    assert re.search(search_re, str(exc_info.value), flags=re.DOTALL)
