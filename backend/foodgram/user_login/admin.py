from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username",
                    "first_name", "last_name", "is_staff")
    search_fields = ("email", "username")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("username", "first_name", "last_name", "avatar")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")
    list_filter = ("is_staff", "is_superuser", "is_active")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("author", "follower")
    search_fields = (
        "author__username",
        "author__email",
        "follower__username",
        "follower__email",
    )
