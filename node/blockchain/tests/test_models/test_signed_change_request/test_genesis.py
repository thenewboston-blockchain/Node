import re

import pytest
from pydantic import ValidationError

from node.blockchain.inner_models import (
    GenesisSignedChangeRequest, GenesisSignedChangeRequestMessage, SignedChangeRequest
)


def test_create_from_genesis_signed_change_request_message(
    genesis_signed_change_request_message, primary_validator_key_pair
):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    assert isinstance(signed_change_request, GenesisSignedChangeRequest)
    assert signed_change_request.message == genesis_signed_change_request_message
    assert signed_change_request.signer == primary_validator_key_pair.public
    assert signed_change_request.signature == (
        'e344e90ece282fc8fcbb92bf552a8238b8c2e93ef96dd50b49d53cce9fc7b5e0'
        'd0353f1464c1ed8b91e5246dc282ada0d03aa9e992f82689067d9db4eff4d508'
    )


def test_serialize_and_deserialize_genesis_type(genesis_signed_change_request, primary_validator_key_pair):
    assert isinstance(genesis_signed_change_request, GenesisSignedChangeRequest)
    serialized = genesis_signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert isinstance(deserialized, GenesisSignedChangeRequest)
    assert deserialized.signer == genesis_signed_change_request.signer
    assert deserialized.signature == genesis_signed_change_request.signature
    assert deserialized.message == genesis_signed_change_request.message
    assert deserialized == genesis_signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2


def test_signature_validation_genesis_type(genesis_signed_change_request, primary_validator_key_pair):
    with pytest.raises(ValidationError) as exc_info:
        GenesisSignedChangeRequest(
            signer=genesis_signed_change_request.signer,
            signature='0' * 128,
            message=genesis_signed_change_request.message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)

    with pytest.raises(ValidationError) as exc_info:
        GenesisSignedChangeRequest(
            signer='0' * 64,
            signature=genesis_signed_change_request.signature,
            message=genesis_signed_change_request.message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)

    message = GenesisSignedChangeRequestMessage(
        accounts=genesis_signed_change_request.message.accounts,
        account_lock='0' * 64,
        type=genesis_signed_change_request.message.type,
    )
    with pytest.raises(ValidationError) as exc_info:
        GenesisSignedChangeRequest(
            signer=genesis_signed_change_request.signer,
            signature=genesis_signed_change_request.signature,
            message=message,
        )
    assert re.search(r'__root__.*Invalid signature', str(exc_info.value), flags=re.DOTALL)
