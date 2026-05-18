"""Тонкая обёртка над sentence-transformers с ленивой загрузкой модели."""
from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer  # noqa: F401

logger = logging.getLogger(__name__)

_model: "SentenceTransformer | None" = None
_lock = threading.Lock()


def get_model():
    """Возвращает singleton модели. Грузит при первом обращении."""
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s", settings.EMBEDDING_MODEL_NAME)
            _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def embed_query(text: str) -> list[float]:
    """Эмбеддинг запроса. E5-модели требуют префикс query:."""
    model = get_model()
    vec = model.encode(
        [f"query: {text.strip()}"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return vec.tolist()


def embed_passage(text: str) -> list[float]:
    """Эмбеддинг документа. E5 требует префикс passage:."""
    model = get_model()
    vec = model.encode(
        [f"passage: {text.strip()}"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return vec.tolist()
