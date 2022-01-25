from node.blockchain.inner_models.node import Node


def get_nodes_for_syncing() -> list[Node]:
    # TODO(dmu) CRITICAL: Implement in https://thenewboston.atlassian.net/browse/BC-164
    #                     If local blockchain contains at least one node then use nodes from local blockchain
    #                     Otherwise try to get nodes from thenewboston.com end-point
    #                     Otherwise use nodes from JSON-file (stored during docker image build)
    #                     Otherwise return an empty list of nodes
    return []
