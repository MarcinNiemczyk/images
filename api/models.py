import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class Image(models.Model):
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])]
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


class AccountTier(models.Model):
    name = models.CharField(max_length=50, unique=True)
    thumbnail_sizes = models.ManyToManyField("Size", blank=True)
    orginal_image = models.BooleanField()
    generate_links = models.BooleanField()

    def __str__(self):
        return self.name


class Size(models.Model):
    height = models.IntegerField(
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(2000),
        ],
    )

    def __str__(self):
        return str(self.height)


class Thumbnail(models.Model):
    image = models.ImageField()
    orginal_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)


class TemporaryLink(models.Model):
    link = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expiry_time = models.DateTimeField()
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.link)


class User(AbstractUser):
    tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                self.tier = AccountTier.objects.get(name="Basic")
            except AccountTier.DoesNotExist:
                raise AccountTier.DoesNotExist(
                    "Built-in tiers not found, try to load fixtures first."
                )
        super(User, self).save(*args, **kwargs)
