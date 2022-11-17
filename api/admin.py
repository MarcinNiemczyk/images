from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from api.models import AccountTier, Image, Size, Thumbnail, User


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "author")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "tier")
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            "Account Plan",
            {
                "fields": ("tier",),
            },
        ),
    )


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    ordering = ("height",)


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("__str__", "size", "get_author")

    def get_author(self, obj):
        return obj.orginal_image.author

    get_author.short_description = "Author"


admin.site.register(AccountTier)
admin.site.unregister(Group)
