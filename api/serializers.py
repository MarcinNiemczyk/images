from rest_framework import serializers

from api.models import Image


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
