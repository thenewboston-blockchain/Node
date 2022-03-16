from django.http import Http404
from pydantic.errors import PydanticValueError
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from node.blockchain.models import AccountState
from node.blockchain.serializers.account_state import AccountStateSerializer
from node.blockchain.types import AccountNumber


class AccountStateViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = AccountStateSerializer
    queryset = AccountStateSerializer.Meta.model.objects.all()

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            account_number = self.kwargs.get(lookup_url_kwarg)
            if not account_number:
                raise

            try:
                AccountNumber.validate(account_number)
            except PydanticValueError:
                raise Http404

            # If account is not found then we virtually assume that it exists (although not know to the blockchain)
            # TODO(dmu) MEDIUM: Should we move this logic to AccountStateManage or BlockchainFacade?
            return AccountState(
                _id=account_number,
                balance=0,
                account_lock=account_number,
                node=None,
            )
