from node.blockchain.inner_models.signed_change_request import SignedChangeRequest


def test_create_from_signed_change_request_message(genesis_signed_change_request_message, primary_validator_key_pair):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    assert signed_change_request.message == genesis_signed_change_request_message
    assert signed_change_request.signer == primary_validator_key_pair.public
    assert signed_change_request.signature == (
        'e344e90ece282fc8fcbb92bf552a8238b8c2e93ef96dd50b49d53cce9fc7b5e0'
        'd0353f1464c1ed8b91e5246dc282ada0d03aa9e992f82689067d9db4eff4d508'
    )


def test_serialize_and_deserialize(genesis_signed_change_request_message, primary_validator_key_pair):
    signed_change_request = SignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
    serialized = signed_change_request.json()
    deserialized = SignedChangeRequest.parse_raw(serialized)
    assert deserialized.signer == signed_change_request.signer
    assert deserialized.signature == signed_change_request.signature
    assert deserialized.message == signed_change_request.message
    assert deserialized == signed_change_request

    serialized2 = deserialized.json()
    assert serialized == serialized2
