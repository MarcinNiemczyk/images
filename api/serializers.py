from rest_framework import serializers

from api.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = ("author",)

    def create(self, validated_data):
        author = self.context.get("request").user
        image = Image(author=author, **validated_data)
        image.save()
        return image
