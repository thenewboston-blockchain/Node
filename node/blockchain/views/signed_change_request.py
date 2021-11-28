from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from node.blockchain.serializers.signed_change_request import SignedChangeRequestSerializer


class SignedChangeRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SignedChangeRequestSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        # TODO(dmu) CRITICAL: Provide actual implementation of perform_create()
        #                     https://thenewboston.atlassian.net/browse/BC-167
        raise NotImplementedError(instance.json())
