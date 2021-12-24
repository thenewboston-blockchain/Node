from rest_framework import serializers

from node.blockchain.models import Node
from node.blockchain.types import Type

API_SUPPORTED_TYPES = {item for item in Type if item != Type.GENESIS}


class NodeSerializer(serializers.ModelSerializer):
    # TODO(dmu) HIGH: Instead of redefining serializer fields generate serializer from
    #                 Node model metadata
    identifier = serializers.CharField()
    addresses = serializers.ListField(serializers.CharField())
    fee = serializers.IntegerField()

    class Meta:
        model = Node
        fields = ('identifier', 'addresses', 'fee')
