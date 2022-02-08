from node.blockchain.inner_models import GenesisBlockMessage, GenesisSignedChangeRequest


def make_genesis_block_message(
    genesis_signed_change_request_message, primary_validator_private_key, primary_validator_node
) -> GenesisBlockMessage:
    request = GenesisSignedChangeRequest.create_from_signed_change_request_message(
        message=genesis_signed_change_request_message,
        signing_key=primary_validator_private_key,
    )
    return GenesisBlockMessage.create_from_signed_change_request(
        request=request, primary_validator_node=primary_validator_node
    )
