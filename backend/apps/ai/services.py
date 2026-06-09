import hashlib
import json
import logging
from typing import Any

from django.conf import settings

from .deepseek import DeepSeekClient, DeepSeekError
from .models import ChatMessage, ChatSession
from .pexels import pick_diverse, search_photos as pexels_search
from .prompts import SYSTEM_PROMPTS, is_structured

logger = logging.getLogger(__name__)


def _fallback_image(query: str, i: int = 0) -> str:
    """Стабильный URL-заглушка по picsum (надёжнее loremflickr, который часто 500-ит).

    Индекс `i` гарантирует, что 6 картинок мудборда не совпадут между собой.
    """
    seed = hashlib.md5(f"{(query or 'design')}:{i}".encode("utf-8")).hexdigest()[:12]
    return f"https://picsum.photos/seed/{seed}/800/600"


def _filters_block(filters: dict[str, Any] | None) -> str:
    if not filters:
        return ""
    pairs = [f"{k}: {v}" for k, v in filters.items() if v]
    if not pairs:
        return ""
    return "\n\nАктивные фильтры пользователя (учти их при подборе): " + ", ".join(pairs) + "."


def _assistant_history_content(msg: ChatMessage) -> str:
    """Что отдавать LLM как «прошлый ответ ассистента».

    Для structured-режимов (fonts/moodboard/colors) короткое поле `content`
    (это `reply`) НЕ годится — оно не содержит ни предыдущей пары шрифтов, ни
    палитры, ни референсов. Без этих полей в истории модель буквально не
    видит, что генерировала в прошлый раз, и любая просьба «оставь палитру»
    проваливается. Поэтому отдаём весь сохранённый payload, выкинув служебное
    поле `_chain_of_thought` (это размышление прошлого хода — лишний шум).
    """
    if isinstance(msg.payload, dict) and msg.payload:
        clean = {k: v for k, v in msg.payload.items() if k != "_chain_of_thought"}
        return json.dumps(clean, ensure_ascii=False)
    return msg.content


def build_history(
    session: ChatSession,
    limit: int = 20,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    system = SYSTEM_PROMPTS.get(session.mode, SYSTEM_PROMPTS["free"])
    system += _filters_block(filters)
    history: list[dict[str, str]] = [{"role": "system", "content": system}]
    messages = session.messages.all().order_by("-created_at")[:limit]
    for msg in reversed(list(messages)):
        if msg.role == ChatMessage.Role.SYSTEM:
            continue
        if msg.role == ChatMessage.Role.ASSISTANT:
            content = _assistant_history_content(msg)
        else:
            content = msg.content
        history.append({"role": msg.role, "content": content})
    return history


def _photos_to_references(photos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for p in photos:
        refs.append({
            "title": p.get("alt") or "",
            "description": "",
            "image_url": p.get("image_url"),
            "image_fallback": p.get("image_url_small"),
            "source_url": p.get("page_url"),
            "source": "pexels",
            "photographer": p.get("photographer"),
            "avg_color": p.get("avg_color"),
        })
    return refs


def _fallback_references(query: str, count: int = 6) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    base = (query or "design").strip()
    for i in range(count):
        url = _fallback_image(base, i)
        refs.append({
            "title": "",
            "description": "",
            "image_url": url,
            "image_fallback": url,
            "source": "picsum",
        })
    return refs


def enrich_payload(mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Подтягиваем 6 фото с Pexels одним запросом по `moodboard_query` + `moodboard_color`.

    Палитра остаётся той, что сгенерировал DeepSeek (не пересчитываем из фото).
    """
    if mode != "moodboard" or not isinstance(payload, dict):
        return payload

    query = (payload.get("moodboard_query") or "").strip()
    color = (payload.get("moodboard_color") or "").strip()
    theme = (payload.get("theme") or "").strip()
    palette = payload.get("palette") or []

    # Reject-ветка промпта: LLM не поняла запрос и вернула пустые theme/palette.
    # В этом случае не показываем ни заглушки, ни «реальные» референсы — пусть
    # пользователь увидит только текстовый ответ.
    if not theme and not palette:
        payload["references"] = []
        return payload

    api_key = getattr(settings, "PEXELS_API_KEY", "") or ""
    refs: list[dict[str, Any]] = []

    # moodboard_query иногда приходит пустым — тогда ищем по теме, а не уходим
    # сразу в заглушки.
    search_query = query or theme

    if api_key and search_query:
        # Первый прогон — с цветовым фильтром.
        candidates = pexels_search(query=search_query, api_key=api_key, color=color or None)
        chosen = pick_diverse(candidates, count=6)

        # Если на цвет не хватило 6 уникальных кадров — добираем без фильтра.
        if len(chosen) < 6:
            extra = pexels_search(query=search_query, api_key=api_key, color=None)
            seen = {c.get("id") for c in chosen}
            for p in extra:
                if len(chosen) >= 6:
                    break
                if p.get("id") in seen:
                    continue
                chosen.append(p)
                seen.add(p.get("id"))

        refs = _photos_to_references(chosen)
        payload["pexels_meta"] = {
            "query": search_query,
            "color": color or None,
            "found": len(candidates),
            "selected": len(chosen),
        }

    if not refs:
        # Сети нет / ключа нет / Pexels пусто — отдаём picsum-заглушки.
        refs = _fallback_references(search_query or "design")

    payload["references"] = refs
    return payload


def summarise_project(project) -> dict[str, Any]:
    """
    Собрать финальные рекомендации по проекту: лучшая шрифтовая пара,
    палитра, направление, мок-контент. Кеширует результат в project.summary_payload.
    """
    sessions = project.chat_sessions.all().prefetch_related("messages").order_by("created_at")

    font_pairs: list[dict[str, Any]] = []
    moodboards: list[dict[str, Any]] = []

    for s in sessions:
        for msg in s.messages.all():
            if msg.role != ChatMessage.Role.ASSISTANT or not isinstance(msg.payload, dict):
                continue
            p = msg.payload
            reaction = msg.reaction  # "like" | "dislike" | None
            if s.mode == "fonts" and p.get("pairs"):
                for pair in p.get("pairs") or []:
                    font_pairs.append({
                        "name": pair.get("name"),
                        "heading": (pair.get("heading") or {}).get("family"),
                        "body": (pair.get("body") or {}).get("family"),
                        "mood": pair.get("mood"),
                        "reaction": reaction,
                    })
            elif s.mode in {"moodboard", "colors"}:
                moodboards.append({
                    "theme": p.get("theme"),
                    "description": p.get("description"),
                    "mood": p.get("mood"),
                    "palette": [
                        {"hex": c.get("hex"), "role": c.get("role"), "name": c.get("name")}
                        for c in (p.get("palette") or [])[:8]
                    ],
                    "typography": p.get("typography") or {"hint": p.get("typography_hint")},
                    "reaction": reaction,
                })

    context_payload = {
        "project": {
            "name": project.name,
            "description": project.description,
            "brief": project.brief,
            "kind": project.kind,
        },
        "font_pairs": font_pairs[:8],
        "moodboards": moodboards[:4],
    }

    user_msg = (
        "Сведи результаты проекта в финальные рекомендации по JSON-схеме.\n"
        "Контекст проекта:\n"
        f"{json.dumps(context_payload, ensure_ascii=False)}"
    )

    system = SYSTEM_PROMPTS["project_summary"]
    client = DeepSeekClient()
    history = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    try:
        payload = client.chat_json(history, temperature=0.6)
    except DeepSeekError as exc:
        logger.exception("DeepSeek project summary failed")
        raise

    from django.utils import timezone
    project.summary_payload = payload
    project.summary_generated_at = timezone.now()
    project.save(update_fields=["summary_payload", "summary_generated_at", "updated_at"])
    return payload


def _extract_fonts_history_pairs(session: ChatSession) -> list[dict[str, str]]:
    """Достаёт пары из последнего ответа ассистента (для follow-up'ов 'оставь X')."""
    last = (
        session.messages.filter(role=ChatMessage.Role.ASSISTANT)
        .order_by("-created_at")
        .first()
    )
    if not last or not isinstance(last.payload, dict):
        return []
    pairs = last.payload.get("pairs") or []
    result: list[dict[str, str]] = []
    for p in pairs[:6]:
        if not isinstance(p, dict):
            continue
        heading = ((p.get("heading") or {}).get("family") or "").strip()
        body = ((p.get("body") or {}).get("family") or "").strip()
        if heading and body:
            result.append({"heading": heading, "body": body})
    return result


def generate_reply(
    session: ChatSession,
    user_content: str,
    filters: dict[str, Any] | None = None,
    request=None,
) -> ChatMessage:
    ChatMessage.objects.create(
        session=session, role=ChatMessage.Role.USER, content=user_content
    )
    try:
        if session.mode == "fonts":
            # Поиск по нашей БД через эмбеддинги + DeepSeek-переписку запроса.
            from apps.fonts.payload import build_fonts_payload

            history_pairs = _extract_fonts_history_pairs(session)
            payload = build_fonts_payload(
                user_content,
                request=request,
                filters=filters,
                history_pairs=history_pairs,
            )
            text = payload.get("reply") or "Готово"
            assistant = ChatMessage.objects.create(
                session=session,
                role=ChatMessage.Role.ASSISTANT,
                content=text,
                payload=payload,
            )
        elif is_structured(session.mode):
            client = DeepSeekClient()
            history = build_history(session, filters=filters)
            payload = client.chat_json(history, temperature=0.8)
            payload = enrich_payload(session.mode, payload)
            text = payload.get("reply") or "Готово"
            assistant = ChatMessage.objects.create(
                session=session,
                role=ChatMessage.Role.ASSISTANT,
                content=text,
                payload=payload,
            )
        else:
            client = DeepSeekClient()
            history = build_history(session, filters=filters)
            text = client.chat(history, temperature=0.7)
            assistant = ChatMessage.objects.create(
                session=session,
                role=ChatMessage.Role.ASSISTANT,
                content=text,
            )
    except DeepSeekError as exc:
        logger.exception("DeepSeek failed")
        assistant = ChatMessage.objects.create(
            session=session,
            role=ChatMessage.Role.ASSISTANT,
            content=f"Не удалось получить ответ: {exc}",
        )
    session.save(update_fields=["updated_at"])
    if not session.title and user_content:
        session.title = user_content[:80]
        session.save(update_fields=["title"])
    return assistant
