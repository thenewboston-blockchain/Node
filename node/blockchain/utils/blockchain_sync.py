from typing import Optional

# TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-226
# from node.blockchain.facade import BlockchainFacade
# from node.core.clients.node import NodeClient


def sync_with_address(address: str, to_block_number: Optional[int]):
    raise NotImplementedError
    # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-226
    # if to_block_number is None:
    #     # TODO(dmu) CRITICAL: Get block number from the address
    #     raise NotImplementedError
    #
    # facade = BlockchainFacade.get_instance()
    # next_block_number = facade.get_next_block_number()
    #
    # for block in NodeClient.get_instance().yield_blocks():
    #     facade.add_block_from_json(block)


def sync_with_node():
    raise NotImplementedError
