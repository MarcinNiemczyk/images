from django.urls import reverse
from rest_framework import serializers

from api.models import Image, TemporaryLink


class ImageSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField("get_images")

    class Meta:
        model = Image
        fields = ("images", "image")
        read_only_fields = ("images",)
        extra_kwargs = {"image": {"write_only": True}}

    def create(self, validated_data):
        author = self.context.get("request").user
        image = Image(author=author, **validated_data)
        image.save()
        return image

    def get_images(self, obj):
        output = {}
        request = self.context.get("request")
        account_tier = obj.author.tier
        thumbnail_sizes = account_tier.thumbnail_sizes

        if account_tier.orginal_image:
            image_url = request.build_absolute_uri(obj.image.url)
            output["orginal"] = image_url

        thumbnails = obj.thumbnail_set.all()
        for thumbnail in thumbnails:
            if thumbnail.size in thumbnail_sizes.all():
                thumbnail_url = request.build_absolute_uri(thumbnail.image.url)
                output[thumbnail.size.height] = thumbnail_url

        return output


class UserImagesForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context["request"].user
        return Image.objects.filter(author=user)


class TemporaryLinkSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField("get_absolute_url")
    image = UserImagesForeignKey()

    class Meta:
        model = TemporaryLink
        fields = ("link", "expiry_time", "image", "seconds")
        read_only_fields = ("expiry_time", "link")
        extra_kwargs = {
            "seconds": {"write_only": True},
            "image": {"write_only": True},
        }

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        url = request.build_absolute_uri(
            reverse("temporary-links", kwargs={"link": obj.link})
        )
        return url
