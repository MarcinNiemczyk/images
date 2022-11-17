from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from api.models import AccountTier, Image, Size, User


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


admin.site.register(AccountTier)
admin.site.unregister(Group)
