import shutil
import tempfile
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from PIL import Image as img
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import AccountTier, Image, Size, TemporaryLink, Thumbnail, User
from api.serializers import ImageSerializer, TemporaryLinkSerializer

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SetUpClass(TestCase):
    def setUp(self):
        image = img.new("RGB", size=(50, 50), color=(256, 0, 0))
        image_bytes = BytesIO()
        image.save(image_bytes, format="png")
        image_file = ImageFile(image_bytes, name="test_image")
        self.size = Size.objects.create(height=100)
        self.basic_tier = AccountTier.objects.create(
            name="Basic",
            orginal_image=False,
            generate_links=False,
        )
        self.basic_tier.thumbnail_sizes.add(self.size)
        self.premium_tier = AccountTier.objects.create(
            name="Premium",
            orginal_image=True,
            generate_links=True,
        )
        self.premium_tier.thumbnail_sizes.add(
            self.size, Size.objects.create(height=200)
        )
        self.user = User.objects.create(
            username="foo", password="bar", tier=self.basic_tier
        )
        self.image = Image.objects.create(image=image_file, author=self.user)
        self.temporary_link = TemporaryLink.objects.create(
            seconds=600, image=self.image
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()


class ModelsTestCase(SetUpClass):
    def test_account_tier_name_max_length(self):
        max_length = self.basic_tier._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)

    def test_account_tier_object_name_is_tier_name(self):
        expected_object_name = self.basic_tier.name
        self.assertEqual(str(self.basic_tier), expected_object_name)

    def test_size_object_name_is_height(self):
        expected_object_name = self.size.height
        self.assertEqual(str(self.size), str(expected_object_name))

    def test_temporary_link_object_name_is_link(self):
        expected_object_name = self.temporary_link.link
        self.assertEqual(str(self.temporary_link), str(expected_object_name))

    def test_temporary_link_expiry_time_is_calculated_correctly(self):
        seconds = 600
        now = timezone.now()
        temporary_link = TemporaryLink.objects.create(
            seconds=seconds, image=self.image
        )
        difference = temporary_link.expiry_time - now
        self.assertEqual(round(difference.total_seconds(), -2), 600)

    def test_user_gets_basic_account_tier_by_default(self):
        self.assertEqual(self.user.tier, self.basic_tier)

    def test_user_changed_account_tier_is_not_overridden_by_default_tier(self):
        self.user.tier = self.premium_tier
        self.assertEqual(self.user.tier, self.premium_tier)
        self.assertNotEqual(self.user.tier, self.basic_tier)

    def test_user_raise_load_fixtures_exception(self):
        self.basic_tier.delete()
        with self.assertRaises(AccountTier.DoesNotExist):
            User.objects.create(username="foo", password="bar")

    def test_new_image_sends_signal_to_create_thumbnails(self):
        thumbnail1 = Thumbnail.objects.get(id=1)
        thumbnail2 = Thumbnail.objects.get(id=2)
        self.assertEqual(thumbnail1, self.image.thumbnail_set.first())
        self.assertEqual(thumbnail2, self.image.thumbnail_set.last())

    def test_updated_image_does_not_create_thumbnails(self):
        new_author = User.objects.create(username="bar", password="baz")
        self.image.author = new_author
        self.assertEqual(
            Thumbnail.objects.count(), self.image.thumbnail_set.count()
        )


class SerializersTestCase(SetUpClass):
    def setUp(self):
        super(SerializersTestCase, self).setUp()
        self.request = RequestFactory().get("./foo")
        self.request.user = self.user

    def test_image_output_contains_expected_fields(self):
        serializer = ImageSerializer(
            instance=self.image, context={"request": self.request}
        )
        data = serializer.data
        self.assertCountEqual(data.keys(), ["images"])

    def test_image_output_contains_expected_thumbnails(self):
        serializer = ImageSerializer(
            instance=self.image, context={"request": self.request}
        )
        data = serializer.data
        expected_thumbnail_sizes = [self.size.height]
        self.assertCountEqual(data["images"].keys(), expected_thumbnail_sizes)

    def test_image_output_depends_on_account_tier(self):
        self.user.tier = self.basic_tier
        serializer = ImageSerializer(
            instance=self.image, context={"request": self.request}
        )
        data = serializer.data
        expected_keys = [self.size.height]
        self.assertCountEqual(data["images"].keys(), expected_keys)

        self.user.tier = self.premium_tier
        serializer = ImageSerializer(
            instance=self.image, context={"request": self.request}
        )
        data = serializer.data
        expected_keys = [
            self.size.height,
            Size.objects.get(id=2).height,
            "orginal",
        ]
        self.assertCountEqual(data["images"].keys(), expected_keys)

    def test_image_input_assigns_right_author(self):
        image = BytesIO()
        img.new("RGB", (100, 100)).save(image, "JPEG")
        image.seek(0)
        image_file = SimpleUploadedFile("test_image.jpg", image.getvalue())

        serializer_data = {"image": image_file}
        serializer = ImageSerializer(
            data=serializer_data, context={"request": self.request}
        )
        self.assertTrue(serializer.is_valid())
        image_obj = serializer.save()
        self.assertEqual(image_obj.author, self.user)

    def test_temporary_link_output_url_is_absolute(self):
        serializer = TemporaryLinkSerializer(
            instance=self.temporary_link, context={"request": self.request}
        )
        data = serializer.data
        expected_url = self.request.build_absolute_uri(
            reverse(
                "temporary-links", kwargs={"link": self.temporary_link.link}
            )
        )
        self.assertEqual(data["link"], expected_url)


class ViewsTestCase(APITestCase, SetUpClass):
    def setUp(self):
        super(ViewsTestCase, self).setUp()
        self.client.force_login(self.user)

    def test_api_is_accessible_only_for_authenticated_users(self):
        self.client.logout()
        response = self.client.get(reverse("image-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(reverse("generate-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_url_accessible_for_specific_account_tier(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("generate-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.tier = self.premium_tier
        self.user.save()
        response = self.client.get(reverse("generate-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_image_api_returns_own_images_for_logged_user(self):
        response = self.client.get(reverse("image-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_expiring_link(self):
        response = self.client.get(
            reverse(
                "temporary-links", kwargs={"link": self.temporary_link.link}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_expiring_link(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(
                reverse(
                    "temporary-links",
                    kwargs={"link": "foobar"},
                )
            )
        response = self.client.get(
            reverse(
                "temporary-links",
                kwargs={"link": "a9bf3872-b701-4e01-a183-e25cf0ac8380"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_expiring_link_is_available_for_everyone(self):
        self.client.logout()
        response = self.client.get(
            reverse(
                "temporary-links", kwargs={"link": self.temporary_link.link}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
