from node.blockchain.inner_models import GenesisSignedChangeRequest


def make_genesis_signed_change_request(genesis_signed_change_request_message, primary_validator_key_pair):
    return GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_key_pair.private,
    )
