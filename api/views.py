from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Image, TemporaryLink
from api.permissions import GenerateLinksAllowed
from api.serializers import ImageSerializer, TemporaryLinkSerializer


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer

    def get_queryset(self):
        return Image.objects.filter(author=self.request.user).all()


class TemporaryLinkViewSet(viewsets.ModelViewSet):
    serializer_class = TemporaryLinkSerializer
    permission_classes = [IsAuthenticated, GenerateLinksAllowed]

    def get_queryset(self):
        return TemporaryLink.objects.filter(
            image__author=self.request.user, expiry_time__gte=timezone.now()
        ).all()


class PublicTemporaryLinkView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, link):
        try:
            temporary_link = TemporaryLink.objects.get(
                link=link, expiry_time__gte=timezone.now()
            )
        except TemporaryLink.DoesNotExist:
            content = {"detail": "Bad or expired link"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        image_path = Path(settings.MEDIA_ROOT).joinpath(
            temporary_link.image.image.name
        )
        image_data = open(image_path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpg")
