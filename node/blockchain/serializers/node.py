from rest_framework import serializers

from node.blockchain.models import Node


class NodeSerializer(serializers.ModelSerializer):
    """
    The network uses multiple nodes, which are servers with several responsibilities.
    Nodes connect users or client apps to the network, or enable important processes,
    such as transaction validation.
    """

    # TODO(dmu) HIGH: Instead of redefining serializer fields generate serializer from
    #                 Node model metadata
    identifier = serializers.CharField()
    addresses = serializers.ListField(child=serializers.CharField())
    fee = serializers.IntegerField()

    class Meta:
        model = Node
        fields = ('identifier', 'addresses', 'fee')
