from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
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


class Size(models.Model):
    height = models.IntegerField(unique=True)


class User(AbstractUser):
    tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE, null=True)
