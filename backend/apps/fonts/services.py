"""Поиск шрифтов и пар по эмбеддингам (pgvector cosine).

LLM-обогащение (rationale, use_cases, mood, sample text) делается отдельно
в apps.fonts.payload — здесь только поиск по векторам и определение intent
через DeepSeek.
"""
from __future__ import annotations

import logging
from typing import TypedDict

from pgvector.django import CosineDistance

from apps.ai.deepseek import DeepSeekClient, DeepSeekError
from apps.fonts.embeddings import embed_query
from apps.fonts.models import Font, FontPair

logger = logging.getLogger(__name__)


VALID_INTENTS = {"pair_search", "match_heading", "match_body", "explain"}


class HistoryPair(TypedDict):
    heading: str
    body: str


REWRITE_SYSTEM_PROMPT = """Ты определяешь намерение пользователя в чате подбора шрифтов.

На вход:
- Текущая реплика пользователя.
- (Опционально) список шрифтовых пар, которые ассистент предложил в прошлом ответе. Каждая пара — это heading-шрифт (для заголовка) и body-шрифт (для основного текста).

Верни СТРОГО валидный JSON по схеме:
{
  "intent": "pair_search" | "match_heading" | "match_body" | "explain",
  "search_text": "очищенный поисковый запрос на русском, ёмко, по сути задачи",
  "keep_font_name": null | "<точное имя шрифта из прошлого ответа>"
}

Правила:
- pair_search — пользователь хочет новую шрифтовую пару (ЭТО ДЕФОЛТ).
- match_heading — пользователь сказал «оставь шрифт X», где X стоял в роли heading в прошлом ответе. keep_font_name=X, search_text описывает желаемый body.
- match_body — пользователь сказал «оставь шрифт X», где X был в роли body. keep_font_name=X, search_text описывает желаемый heading.
- explain — реплика не про подбор шрифтов; search_text пустой.

Подсказки:
- «оставь шрифт заголовка / не меняй heading» → match_heading; ищи в прошлом ответе heading.
- «оставь шрифт основного текста / не меняй body» → match_body.
- «оставь Inter» (имя) → найди роль Inter в прошлом ответе и используй match_heading или match_body.
- Если прошлых пар нет, или роль шрифта непонятна — pair_search, keep_font_name=null.
- search_text — лаконичная сводка задачи: тематика, настроение, стиль, контекст. Без «ищу шрифт».
- Категории/роли в search_text упоминай только если пользователь сам их назвал.

ТОЛЬКО JSON. Без markdown и преамбулы."""


def rewrite_query(user_prompt: str, *, history_pairs: list[HistoryPair] | None = None) -> dict:
    """DeepSeek-rewrite: текст пользователя + история → intent + search_text."""
    history_pairs = history_pairs or []
    history_block = ""
    if history_pairs:
        listed = "\n".join(
            f"- heading: {p['heading']}, body: {p['body']}" for p in history_pairs[:6]
        )
        history_block = f"\n\nПары из прошлого ответа ассистента:\n{listed}"

    user_msg = f"Реплика пользователя:\n{user_prompt.strip()}{history_block}"
    messages = [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    try:
        data = DeepSeekClient().chat_json(messages, temperature=0.2)
    except DeepSeekError:
        logger.exception("Query rewrite failed, falling back to raw text")
        return {"intent": "pair_search", "search_text": user_prompt.strip(), "keep_font_name": None}

    intent = data.get("intent")
    if intent not in VALID_INTENTS:
        intent = "pair_search"
    search_text = (data.get("search_text") or "").strip() or user_prompt.strip()
    keep_name = data.get("keep_font_name")
    if not isinstance(keep_name, str) or not keep_name.strip():
        keep_name = None
    else:
        keep_name = keep_name.strip()
    return {"intent": intent, "search_text": search_text, "keep_font_name": keep_name}


def search_pairs(search_text: str, *, filters: dict | None = None, top_k: int = 10):
    """Семантический поиск шрифтовых пар. Фильтры применяются к heading-шрифту."""
    if not search_text:
        return FontPair.objects.none()
    vec = embed_query(search_text)
    qs = (
        FontPair.objects.filter(embedding__isnull=False)
        .select_related("heading", "body")
        .annotate(distance=CosineDistance("embedding", vec))
        .order_by("distance")
    )
    qs = _apply_pair_filters(qs, filters or {})
    return qs[:top_k]


def search_fonts(search_text: str, *, filters: dict | None = None, top_k: int = 10):
    if not search_text:
        return Font.objects.none()
    vec = embed_query(search_text)
    qs = (
        Font.objects.filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", vec))
        .order_by("distance")
    )
    qs = _apply_font_filters(qs, filters or {})
    return qs[:top_k]


def match_font_to(font: Font, *, search_text: str = "", top_k: int = 10):
    """Подбирает второй шрифт к заданному.

    Сначала пары из таблицы FontPair, где этот шрифт уже встречается;
    если запрос непустой — ранжируем по семантической близости к запросу.
    Добиваем до top_k семантически близкими шрифтами (исключая сам font).
    """
    existing_pair_partners = list(
        FontPair.objects.filter(heading=font)
        .select_related("body")
        .values_list("body_id", flat=True)
    ) + list(
        FontPair.objects.filter(body=font)
        .select_related("heading")
        .values_list("heading_id", flat=True)
    )
    existing_pair_partners = list(dict.fromkeys(existing_pair_partners))

    # ранжируем уже существующих партнёров по близости к font.embedding
    # (если есть search_text — то по нему)
    if search_text:
        ranking_vec = embed_query(search_text)
    elif font.embedding is not None:
        ranking_vec = list(font.embedding)
    else:
        ranking_vec = None

    ranked_partners: list[Font] = []
    if existing_pair_partners and ranking_vec is not None:
        ranked_partners = list(
            Font.objects.filter(id__in=existing_pair_partners, embedding__isnull=False)
            .annotate(distance=CosineDistance("embedding", ranking_vec))
            .order_by("distance")
        )

    if len(ranked_partners) >= top_k:
        return ranked_partners[:top_k]

    # добиваем семантически близкими шрифтами (исключая сам font и уже найденных)
    used_ids = {font.id, *(p.id for p in ranked_partners)}
    if ranking_vec is not None:
        extras = list(
            Font.objects.filter(embedding__isnull=False)
            .exclude(id__in=used_ids)
            .annotate(distance=CosineDistance("embedding", ranking_vec))
            .order_by("distance")[: top_k - len(ranked_partners)]
        )
        ranked_partners.extend(extras)
    return ranked_partners


def _apply_font_filters(qs, filters: dict):
    for field in ("category", "role", "width"):
        if value := filters.get(field):
            qs = qs.filter(**{field: value})
    return qs


def _apply_pair_filters(qs, filters: dict):
    # Для пары категория/ширина обычно касается заголовка
    if cat := filters.get("category"):
        qs = qs.filter(heading__category=cat)
    if width := filters.get("width"):
        qs = qs.filter(heading__width=width)
    return qs


def chat_search(
    user_prompt: str,
    *,
    history_pairs: list[HistoryPair] | None = None,
    top_k: int = 8,
    filters: dict | None = None,
) -> dict:
    """Полный поток: rewrite → semantic search.

    Возвращает:
      {
        "intent": "pair_search" | "match_heading" | "match_body" | "explain",
        "search_text": str,
        "kept_font": Font | None,         # для match_* — шрифт, который пользователь оставляет
        "kept_role": "heading"|"body"|None,
        "pairs": [FontPair],              # для pair_search
        "candidates": [Font],             # для match_* — найденные кандидаты на вторую роль
        "rewrite": {...},
      }
    """
    rewrite = rewrite_query(user_prompt, history_pairs=history_pairs)
    intent = rewrite["intent"]
    search_text = rewrite["search_text"]
    keep_name = rewrite["keep_font_name"]

    kept_font: Font | None = None
    kept_role: str | None = None
    pairs: list[FontPair] = []
    candidates: list[Font] = []

    if intent in ("match_heading", "match_body") and keep_name:
        kept_font = (
            Font.objects.filter(name__iexact=keep_name).first()
            or Font.objects.filter(google_family__iexact=keep_name).first()
        )
        if kept_font is None:
            # Имя не нашли — деградируем к обычному поиску пары.
            logger.info("Couldn't find kept font by name=%r, fallback to pair_search", keep_name)
            intent = "pair_search"
            kept_role = None

    if intent == "match_heading" and kept_font is not None:
        kept_role = "heading"
        candidates = [
            f for f in match_font_to(kept_font, search_text=search_text, top_k=top_k + 1)
            if f.id != kept_font.id
        ][:top_k]
    elif intent == "match_body" and kept_font is not None:
        kept_role = "body"
        candidates = [
            f for f in match_font_to(kept_font, search_text=search_text, top_k=top_k + 1)
            if f.id != kept_font.id
        ][:top_k]
    elif intent == "explain":
        pass
    else:
        intent = "pair_search"
        pairs = list(search_pairs(search_text, filters=filters, top_k=top_k))

    return {
        "intent": intent,
        "search_text": search_text,
        "kept_font": kept_font,
        "kept_role": kept_role,
        "pairs": pairs,
        "candidates": candidates,
        "rewrite": rewrite,
    }
