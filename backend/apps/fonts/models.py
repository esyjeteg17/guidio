from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Font(models.Model):
    class Category(models.TextChoices):
        SERIF = "Serif", "Serif"
        SANS_SERIF = "Sans-serif", "Sans-serif"
        DISPLAY = "Display", "Display"
        SCRIPT = "Script", "Script"
        SLAB = "Slab", "Slab"
        MONOSPACE = "Monospace", "Monospace"

    class Role(models.TextChoices):
        HEADING = "Заголовок", "Заголовок"
        BODY = "Текст", "Текст"
        UNIVERSAL = "Универсальный", "Универсальный"
        ACCENT = "Только акцент", "Только акцент"

    class Width(models.TextChoices):
        NARROW = "Узкая", "Узкая"
        NORMAL = "Обычная", "Обычная"
        WIDE = "Широкая", "Широкая"

    class Source(models.TextChoices):
        GOOGLE_FONTS = "google_fonts", "Google Fonts"
        LOCAL = "local", "Локальный архив"
        EXTERNAL = "external", "Внешняя ссылка"

    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    role = models.CharField(max_length=20, choices=Role.choices)
    width = models.CharField(max_length=10, choices=Width.choices)
    usage_context = models.TextField(blank=True)
    theme = models.TextField(blank=True)
    character_mood = models.TextField(blank=True)
    style = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices)
    google_family = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="fonts/", blank=True, null=True)
    embedding_text = models.TextField()
    embedding = VectorField(dimensions=settings.EMBEDDING_DIMENSION, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class FontPair(models.Model):
    heading = models.ForeignKey(
        Font, on_delete=models.CASCADE, related_name="pairs_as_heading"
    )
    body = models.ForeignKey(
        Font, on_delete=models.CASCADE, related_name="pairs_as_body"
    )
    context = models.TextField()
    embedding = VectorField(dimensions=settings.EMBEDDING_DIMENSION, null=True)

    class Meta:
        unique_together = ("heading", "body")
        ordering = ["heading__name", "body__name"]

    def __str__(self) -> str:
        return f"{self.heading.name} + {self.body.name}"
