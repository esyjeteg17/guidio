import secrets

from django.conf import settings
from django.db import models


def _project_invite_token():
    return secrets.token_urlsafe(16)


class Project(models.Model):
    class Kind(models.TextChoices):
        FONTS = "fonts", "Шрифты"
        MOODBOARD = "moodboard", "Мудборд"
        COLORS = "colors", "Цветовая палитра"
        MIXED = "mixed", "Смешанный"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.SET_NULL,
        related_name="projects",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MIXED)
    brief = models.TextField(blank=True, help_text="Начальный промпт пользователя")
    cover = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(blank=True, null=True)
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_projects",
        help_text="Приглашённые соавторы (помимо владельца и команды)",
    )
    invite_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        default=_project_invite_token,
    )
    summary_payload = models.JSONField(
        blank=True,
        null=True,
        help_text="Свёрнутая AI-рекомендация по проекту (шрифты, палитра, макет)",
    )
    summary_generated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.name
