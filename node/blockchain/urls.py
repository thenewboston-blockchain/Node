from rest_framework import routers

from node.blockchain.views.node import NodeViewSet
from node.blockchain.views.signed_change_request import SignedChangeRequestViewSet

router = routers.SimpleRouter()
router.register('signed-change-requests', SignedChangeRequestViewSet, basename='signed-change-request')
router.register('nodes', NodeViewSet, basename='node')

urlpatterns = router.urls
