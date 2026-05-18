from django.contrib import admin

from apps.fonts.models import Font, FontPair


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "role", "width", "source", "has_embedding", "has_file")
    list_filter = ("category", "role", "width", "source")
    search_fields = ("name", "embedding_text")

    @admin.display(boolean=True, description="Эмбеддинг")
    def has_embedding(self, obj: Font) -> bool:
        return obj.embedding is not None

    @admin.display(boolean=True, description="Файл")
    def has_file(self, obj: Font) -> bool:
        return bool(obj.file)


@admin.register(FontPair)
class FontPairAdmin(admin.ModelAdmin):
    list_display = ("heading", "body", "has_embedding")
    list_filter = ("heading__category", "body__category")
    search_fields = ("heading__name", "body__name", "context")
    autocomplete_fields = ("heading", "body")

    @admin.display(boolean=True, description="Эмбеддинг")
    def has_embedding(self, obj: FontPair) -> bool:
        return obj.embedding is not None
