from rest_framework import routers

from node.blockchain.views.account_state import AccountStateViewSet
from node.blockchain.views.block import BlockViewSet
from node.blockchain.views.block_confirmation import BlockConfirmationViewSet
from node.blockchain.views.node import NodeViewSet
from node.blockchain.views.signed_change_request import SignedChangeRequestViewSet

router = routers.SimpleRouter()
router.register('signed-change-requests', SignedChangeRequestViewSet, basename='signed-change-request')
router.register('nodes', NodeViewSet, basename='node')
router.register('blocks', BlockViewSet, basename='block')
router.register('block-confirmations', BlockConfirmationViewSet, basename='block-confirmation')
router.register('account-states', AccountStateViewSet, basename='account-state')

urlpatterns = router.urls
