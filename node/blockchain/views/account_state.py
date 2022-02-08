from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from node.blockchain.serializers.account_state import AccountStateSerializer


class AccountStateViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = AccountStateSerializer
    queryset = AccountStateSerializer.Meta.model.objects
