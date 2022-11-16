from rest_framework.routers import DefaultRouter

from api.views import ImageViewSet

router = DefaultRouter()
router.register(r"images", ImageViewSet, basename="image")
urlpatterns = router.urls
