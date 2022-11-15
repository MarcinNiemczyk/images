from django.conf import settings
from django.db import models


class Image(models.Model):
    image = models.ImageField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
