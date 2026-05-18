from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    class Mode(models.TextChoices):
        FONTS = "fonts", "Шрифты"
        MOODBOARD = "moodboard", "Мудборд"
        COLORS = "colors", "Цветовая палитра"
        FREE = "free", "Свободный чат"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        null=True,
        blank=True,
    )
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.FREE)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title or f"Chat #{self.pk}"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        ASSISTANT = "assistant", "Ассистент"
        SYSTEM = "system", "Система"

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    class Reaction(models.TextChoices):
        LIKE = "like", "Нравится"
        DISLIKE = "dislike", "Не нравится"

    role = models.CharField(max_length=12, choices=Role.choices)
    content = models.TextField()
    payload = models.JSONField(
        blank=True,
        null=True,
        help_text="Структурированный ответ (шрифты, палитры, изображения)",
    )
    reaction = models.CharField(
        max_length=8,
        choices=Reaction.choices,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.role}: {self.content[:60]}"
