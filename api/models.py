from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Image(models.Model):
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])]
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
