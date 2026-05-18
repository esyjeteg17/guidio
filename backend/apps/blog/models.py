from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    class Hue(models.TextChoices):
        CREAM = "cream", "Крем"
        MINT = "mint", "Мята"
        LILAC = "lilac", "Сирень"
        PEACH = "peach", "Персик"
        SKY = "sky", "Небо"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tag = models.CharField(max_length=80, default="Типографика")
    hue = models.CharField(max_length=20, choices=Hue.choices, default=Hue.CREAM)
    cover = models.URLField(blank=True, help_text="URL обложки (опционально)")
    excerpt = models.CharField(max_length=320, blank=True)
    content = models.TextField(help_text="Markdown / обычный текст статьи")
    author = models.CharField(max_length=120, default="Guidio")
    read_minutes = models.PositiveIntegerField(default=4)
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at",)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or "article"
            slug = base
            i = 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
