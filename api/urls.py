from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    ImageViewSet,
    PublicTemporaryLinkView,
    TemporaryLinkViewSet,
)

router = DefaultRouter()
router.register(r"images", ImageViewSet, basename="image")
router.register(r"generate", TemporaryLinkViewSet, basename="generate")

urlpatterns = [
    path("", include(router.urls)),
    path(
        r"temp/<uuid:link>/",
        PublicTemporaryLinkView.as_view(),
        name="temporary-links",
    ),
]
