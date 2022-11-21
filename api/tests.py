from io import BytesIO

from django.core.files.images import ImageFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image as img

from api.models import AccountTier, Image, Size, TemporaryLink, Thumbnail, User


class SetUpClass(TestCase):
    def setUp(self):
        image = img.new("RGB", size=(50, 50), color=(256, 0, 0))
        image_bytes = BytesIO()
        image.save(image_bytes, "PNG")
        image_file = ImageFile(image_bytes, name="test_image")
        self.size = Size.objects.create(height=200)
        self.account_tier = AccountTier.objects.create(
            name="Basic",
            orginal_image=False,
            generate_links=False,
        )
        self.account_tier.thumbnail_sizes.add(
            self.size, Size.objects.create(height=100)
        )
        self.user = User.objects.create(
            username="foo", password="bar", tier=self.account_tier
        )
        self.image = Image.objects.create(image=image_file, author=self.user)
        self.temporary_link = TemporaryLink.objects.create(
            seconds=600, image=self.image
        )


class ModelsTestCase(SetUpClass):
    def test_account_tier_name_max_length(self):
        max_length = self.account_tier._meta.get_field("name").max_length
        self.assertEqual(max_length, 50)

    def test_account_tier_object_name_is_tier_name(self):
        expected_object_name = self.account_tier.name
        self.assertEqual(str(self.account_tier), expected_object_name)

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
        self.assertEqual(self.user.tier, self.account_tier)

    def test_user_changed_account_tier_is_not_overridden_by_default_tier(self):
        new_tier = AccountTier.objects.create(
            name="Premium",
            orginal_image=True,
            generate_links=True,
        )
        self.user.tier = new_tier
        self.assertEqual(self.user.tier, new_tier)
        self.assertNotEqual(self.user.tier, self.account_tier)

    def test_user_raise_load_fixtures_exception(self):
        self.account_tier.delete()
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
