"""Сборка payload для FontsResult.vue.

Поток:
1. chat_search → top-N пар (Font/FontPair) по эмбеддингам.
2. enrich_with_llm → DeepSeek получает запрос пользователя + полные описания
   шрифтов и выбирает лучшие, пишет rationale/use_cases/mood/sample-тексты.
3. Сборка JSON в формате, который ждёт фронт.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from apps.ai.deepseek import DeepSeekClient, DeepSeekError
from apps.fonts.models import Font, FontPair
from apps.fonts.services import chat_search

logger = logging.getLogger(__name__)


CATEGORY_TO_FRONT = {
    Font.Category.SERIF: "serif",
    Font.Category.SANS_SERIF: "sans-serif",
    Font.Category.DISPLAY: "display",
    Font.Category.SCRIPT: "handwriting",
    Font.Category.SLAB: "serif",
    Font.Category.MONOSPACE: "monospace",
}

DEFAULT_WEIGHTS = [400, 500, 600, 700]


ENRICH_SYSTEM_PROMPT = """Ты — Guidio, ассистент-дизайнер. На вход — запрос пользователя и набор кандидатов: шрифтовых пар, для каждой из которых есть описание шрифта-заголовка, шрифта основного текста и характеристика самой пары.

Твоя задача:
1. ВЫБРАТЬ РОВНО ОДНУ пару, которая лучше всего подходит под запрос пользователя.
2. Для выбранной пары написать (на русском):
   - rationale: 1-2 предложения, почему эта пара подходит под запрос. Опирайся на характеристики шрифтов из описаний. Если в описаниях нет нужных свойств — не сочиняй их.
   - use_cases: 2-4 коротких варианта применения, согласованных с описаниями (например: «постер концерта», «обложка журнала»).
   - mood: 2-4 прилагательных, описывающих характер пары — берущихся из описаний.
   - sample_title: яркий русский заголовок (3-6 слов), вписанный в тему запроса.
   - sample_body: короткий русский абзац (1-2 предложения) под тему запроса для демонстрации основного шрифта.
3. Напиши reply — 1-2 предложения. Тон — живого дизайнера, который объясняет свой выбор пользователю.

КРИТИЧЕСКИ ВАЖНО:
- Говори как обычный дизайнер. НЕ упоминай: «база данных», «список», «кандидаты», «остальные пары», «найдено», «подобрано из…», «не подошли». Пользователь не знает о внутренней логике подбора.
- Не сравнивай с другими вариантами. Просто рассказывай про выбранную пару.
- НЕ выдумывай свойства шрифтов, которых нет в их описаниях.

Отвечай ТОЛЬКО валидным JSON:
{
  "reply": "...",
  "pairs": [
    {
      "id": <число — id из входного pair_id>,
      "rationale": "...",
      "use_cases": ["...", "..."],
      "mood": ["...", "..."],
      "sample_title": "...",
      "sample_body": "..."
    }
  ]
}

- В pairs ровно ОДНА пара (или 0, если ни один кандидат не подходит совсем — тогда reply вежливо просит уточнить запрос).
- id — точное число из входа.
- Без markdown, без преамбулы."""


@dataclass
class PairItem:
    """Унифицированная пара для LLM-обогащения и сборки финального ответа."""
    key: str  # id пары для frontend (число для реальных FontPair, "match-X-Y" для виртуальных)
    heading: Font
    body: Font
    context: str  # описание из FontPair.context, либо собранное для виртуальной пары


def _gather_pairs(result: dict) -> list[PairItem]:
    """Превращает результат chat_search в плоский список PairItem'ов."""
    items: list[PairItem] = []

    for fp in result.get("pairs") or []:
        items.append(
            PairItem(
                key=str(fp.id),
                heading=fp.heading,
                body=fp.body,
                context=fp.context,
            )
        )

    kept_font: Font | None = result.get("kept_font")
    kept_role: str | None = result.get("kept_role")
    if kept_font is not None and kept_role in ("heading", "body"):
        # match_heading / match_body: формируем пары с kept_font в нужной роли.
        for suggestion in result.get("candidates") or []:
            if suggestion.id == kept_font.id:
                continue
            heading, body = (kept_font, suggestion) if kept_role == "heading" else (suggestion, kept_font)
            existing = (
                FontPair.objects.filter(heading=heading, body=body)
                .select_related("heading", "body")
                .first()
            )
            if existing is not None:
                items.append(
                    PairItem(key=str(existing.id), heading=heading, body=body, context=existing.context)
                )
            else:
                items.append(
                    PairItem(
                        key=f"match-{kept_font.id}-{suggestion.id}-{kept_role}",
                        heading=heading,
                        body=body,
                        context=(
                            f"Сочетание {heading.name} (заголовок) и {body.name} "
                            "(основной текст). Подобрано как дополнение к выбранному пользователем шрифту."
                        ),
                    )
                )

    return items


def _serialize_pairs_for_llm(items: list[PairItem]) -> list[dict[str, Any]]:
    return [
        {
            "pair_id": item.key,
            "heading_name": item.heading.name,
            "heading_category": item.heading.category,
            "heading_role": item.heading.role,
            "heading_description": item.heading.embedding_text,
            "body_name": item.body.name,
            "body_category": item.body.category,
            "body_role": item.body.role,
            "body_description": item.body.embedding_text,
            "pair_context": item.context,
        }
        for item in items
    ]


def enrich_with_llm(
    user_prompt: str,
    items: list[PairItem],
) -> dict[str, Any]:
    """Зовёт DeepSeek; возвращает {reply, pairs_meta: {key: meta}}."""
    if not items:
        return {"reply": "", "pairs_meta": {}}

    user_msg = (
        f"Запрос пользователя:\n{user_prompt.strip()}\n\n"
        f"Найденные пары (отсортированы по эмбеддинговой близости):\n"
        f"{json.dumps(_serialize_pairs_for_llm(items), ensure_ascii=False, indent=2)}"
    )

    messages = [
        {"role": "system", "content": ENRICH_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    try:
        data = DeepSeekClient().chat_json(messages, temperature=0.6)
    except DeepSeekError:
        logger.exception("LLM enrichment failed, returning bare results")
        return {"reply": "", "pairs_meta": {}}

    pairs_meta: dict[str, dict[str, Any]] = {}
    for entry in data.get("pairs") or []:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("id") or "").strip()
        if not key:
            continue
        pairs_meta[key] = {
            "rationale": (entry.get("rationale") or "").strip(),
            "use_cases": [s for s in (entry.get("use_cases") or []) if isinstance(s, str)],
            "mood": [s for s in (entry.get("mood") or []) if isinstance(s, str)],
            "sample_title": (entry.get("sample_title") or "").strip(),
            "sample_body": (entry.get("sample_body") or "").strip(),
        }
    return {
        "reply": (data.get("reply") or "").strip(),
        "pairs_meta": pairs_meta,
    }


def _font_spec(font: Font, *, role: str, request) -> dict[str, Any]:
    is_google = font.source == Font.Source.GOOGLE_FONTS
    file_url = None
    if font.file:
        url = font.file.url
        file_url = request.build_absolute_uri(url) if request else url
    return {
        "id": font.id,
        "family": font.google_family or font.name if is_google else font.name,
        "google_fonts": is_google,
        "category": CATEGORY_TO_FRONT.get(font.category, "sans-serif"),
        "weight": 700 if role == "heading" else 400,
        "style": "normal",
        "available_weights": list(DEFAULT_WEIGHTS),
        "source": font.source,
        "file_url": file_url,
        "preview_link": font.link or None,
    }


def _pair_card(item: PairItem, meta: dict | None, *, request) -> dict[str, Any]:
    meta = meta or {}
    return {
        "id": item.key,
        "name": f"{item.heading.name} + {item.body.name}",
        "heading": _font_spec(item.heading, role="heading", request=request),
        "body": _font_spec(item.body, role="body", request=request),
        "sample_title": meta.get("sample_title") or "Живой заголовок",
        "sample_body": meta.get("sample_body")
        or (
            "Основной текст показывает, как пара работает в длинных текстах — "
            "баланс контраста и читаемости."
        ),
        "use_cases": meta.get("use_cases") or [],
        "mood": meta.get("mood") or [],
        "rationale": meta.get("rationale") or "",
    }


def _merge_prompt_with_filters(user_prompt: str, filters: dict | None) -> str:
    if not filters:
        return user_prompt
    pairs = [f"{k}: {v}" for k, v in filters.items() if v]
    if not pairs:
        return user_prompt
    return f"{user_prompt}\n\nДополнительные пожелания: {', '.join(pairs)}."


def _plural(n: int, one: str, few: str, many: str) -> str:
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return one
    if 2 <= mod10 <= 4 and not (12 <= mod100 <= 14):
        return few
    return many


def _fallback_reply(intent: str, count: int, kept_font: Font | None) -> str:
    if count == 0:
        return "Не нашёл подходящих вариантов. Попробуйте описать задачу иначе."
    if intent in ("match_heading", "match_body") and kept_font is not None:
        word = _plural(count, "пару", "пары", "пар")
        return f"Подобрал {count} {word} к шрифту {kept_font.name}."
    word = _plural(count, "шрифтовую пару", "шрифтовые пары", "шрифтовых пар")
    return f"Подобрал {count} {word}."


def build_fonts_payload(
    user_prompt: str,
    *,
    request=None,
    history_pairs: list | None = None,
    top_k: int = 8,
    filters: dict | None = None,
) -> dict[str, Any]:
    """Главная точка для apps.ai.services.generate_reply."""
    merged_prompt = _merge_prompt_with_filters(user_prompt, filters)
    result = chat_search(merged_prompt, history_pairs=history_pairs, top_k=top_k)

    if result["intent"] == "explain":
        return {
            "reply": "Я помогаю подбирать шрифты и пары шрифтов. Опишите задачу — для какого проекта, какого настроения, какой темы.",
            "intent": "explain",
            "pairs": [],
        }

    items = _gather_pairs(result)

    enriched = enrich_with_llm(merged_prompt, items)
    pairs_meta = enriched["pairs_meta"]

    # Если LLM что-то отобрал — берём только эти пары и в порядке LLM.
    # Иначе (например, LLM упал) — отдаём всё в исходном порядке без enrichment.
    if pairs_meta:
        ordered = []
        seen = set()
        for key in pairs_meta.keys():
            for item in items:
                if item.key == key and key not in seen:
                    ordered.append(item)
                    seen.add(key)
                    break
        if not ordered:  # LLM вернул мусорные id — fallback к исходному порядку
            ordered = items
    else:
        ordered = items

    cards = [_pair_card(item, pairs_meta.get(item.key), request=request) for item in ordered]

    kept_font: Font | None = result.get("kept_font")
    reply = enriched["reply"] or _fallback_reply(result["intent"], len(cards), kept_font)

    return {
        "reply": reply,
        "intent": result["intent"],
        "pairs": cards,
    }
