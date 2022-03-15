from rest_framework import serializers

from node.blockchain.models import AccountState

from .node import NodeSerializer


class AccountStateSerializer(serializers.ModelSerializer):
    """
    Account state, which defines a set of attributes about the current account state, such as account balance
    (the amount of coins owned by an account). These attributes change over time.
    """

    _id = serializers.CharField()
    balance = serializers.IntegerField()
    account_lock = serializers.CharField()
    node = NodeSerializer()

    class Meta:
        model = AccountState
        fields = ('_id', 'balance', 'account_lock', 'node')
