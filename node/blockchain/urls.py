from rest_framework import routers

from node.blockchain.views.signed_change_request import SignedChangeRequestViewSet

router = routers.SimpleRouter()
router.register('signed-change-request', SignedChangeRequestViewSet, basename='signed-change-request')

urlpatterns = router.urls
