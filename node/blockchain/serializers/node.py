from rest_framework import serializers

from node.blockchain.models import Node


class NodeSerializer(serializers.ModelSerializer):
    # TODO(dmu) HIGH: Instead of redefining serializer fields generate serializer from
    #                 Node model metadata
    identifier = serializers.CharField()
    addresses = serializers.ListField(serializers.CharField())
    fee = serializers.IntegerField()

    class Meta:
        model = Node
        fields = ('identifier', 'addresses', 'fee')
