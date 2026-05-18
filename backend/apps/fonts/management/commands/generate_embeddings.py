from django.conf import settings
from django.core.management.base import BaseCommand

from apps.fonts.models import Font, FontPair


def passage(text: str) -> str:
    """E5-модели требуют префикс passage: для документов."""
    return f"passage: {text.strip()}"


class Command(BaseCommand):
    help = "Генерирует эмбеддинги для шрифтов и пар через multilingual-e5-large"

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            choices=["fonts", "pairs", "all"],
            default="all",
            help="Что эмбеддить: fonts, pairs или all",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перегенерировать даже если embedding уже есть",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=16,
        )

    def handle(self, *args, only: str = "all", force: bool = False, batch_size: int = 16, **opts):
        # Импорт здесь, чтобы команда стартовала быстро даже без модели
        from sentence_transformers import SentenceTransformer

        self.stdout.write(f"Загружаю модель {settings.EMBEDDING_MODEL_NAME}…")
        model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.stdout.write(self.style.SUCCESS("Модель загружена."))

        if only in ("fonts", "all"):
            self._embed_fonts(model, force=force, batch_size=batch_size)
        if only in ("pairs", "all"):
            self._embed_pairs(model, force=force, batch_size=batch_size)

    def _embed_fonts(self, model, *, force: bool, batch_size: int) -> None:
        qs = Font.objects.all()
        if not force:
            qs = qs.filter(embedding__isnull=True)
        items = list(qs)
        if not items:
            self.stdout.write("Шрифты: всё уже эмбеддингнуто, пропуск.")
            return
        self.stdout.write(f"Шрифты: эмбеддинг {len(items)} записей…")
        texts = [passage(f.embedding_text) for f in items]
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        for font, vec in zip(items, vectors):
            font.embedding = vec.tolist()
            font.save(update_fields=["embedding"])
        self.stdout.write(self.style.SUCCESS(f"Шрифты: готово ({len(items)})"))

    def _embed_pairs(self, model, *, force: bool, batch_size: int) -> None:
        qs = FontPair.objects.select_related("heading", "body").all()
        if not force:
            qs = qs.filter(embedding__isnull=True)
        items = list(qs)
        if not items:
            self.stdout.write("Пары: всё уже эмбеддингнуто, пропуск.")
            return
        self.stdout.write(f"Пары: эмбеддинг {len(items)} записей…")
        texts = [
            passage(f"{p.heading.name} + {p.body.name}. {p.context}") for p in items
        ]
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        for pair, vec in zip(items, vectors):
            pair.embedding = vec.tolist()
            pair.save(update_fields=["embedding"])
        self.stdout.write(self.style.SUCCESS(f"Пары: готово ({len(items)})"))
