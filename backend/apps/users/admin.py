from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "full_name", "is_staff")
    search_fields = ("email", "username", "full_name")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("full_name", "avatar", "role", "bio")}),
    )
