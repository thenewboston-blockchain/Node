from rest_framework import serializers

from node.blockchain.models import AccountState

from .node import NodeSerializer


class AccountStateSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source='identifier')
    balance = serializers.IntegerField()
    account_lock = serializers.CharField()
    node = NodeSerializer()

    class Meta:
        model = AccountState
        fields = ('_id', 'balance', 'account_lock', 'node')
