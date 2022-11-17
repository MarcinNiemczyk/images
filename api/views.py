from rest_framework import viewsets

from api.models import Image
from api.serializers import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer

    def get_queryset(self):
        return Image.objects.filter(author=self.request.user).all()
