from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from django.utils.translation import gettext_lazy as _

from .models import User

@admin.register(User)
class UserAdmin(UA):
    fieldsets = (
        (None, {"fields": ("phone",'email', "password")}),
        (_("Personal info"), {"fields": ("fullname", "gender", 'role','address', "image")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone",'email', "usable_password", "password1", "password2"),
            },
        ),
    )
    list_display = ('id',"phone", "email", "fullname", 'gender', "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("phone", "fullname", "email")
    ordering = ('id',)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    