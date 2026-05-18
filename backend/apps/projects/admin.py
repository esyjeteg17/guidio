from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "kind", "team", "is_favorite", "updated_at")
    list_filter = ("kind", "is_favorite")
    search_fields = ("name", "brief")
