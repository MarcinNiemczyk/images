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
    height = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(2000),
        ],
    )

    def __str__(self):
        return str(self.height)


class User(AbstractUser):
    tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE, null=True)
