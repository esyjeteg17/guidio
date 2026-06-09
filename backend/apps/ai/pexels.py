"""
Клиент к публичному Pexels API.

Один запрос с query + color возвращает до 80 кандидатов; из них
выбираем 6 разных по фотографу для разнообразия мудборда.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_API_BASE = "https://api.pexels.com/v1"
PEXELS_IMG_HOST = "https://images.pexels.com"


def _rewrite_img(url: str | None, image_proxy: str | None) -> str | None:
    """Pexels-картинки гео-заблокированы в РФ. Если задан image_proxy
    (обратный прокси вне РФ), подменяем хост images.pexels.com на него,
    чтобы картинки грузились в браузере у российских пользователей."""
    if url and image_proxy:
        return url.replace(PEXELS_IMG_HOST, image_proxy.rstrip("/"))
    return url


def _normalize_color(color: str | None) -> str | None:
    """Pexels принимает named color или hex БЕЗ решётки (`ffd700`)."""
    if not color:
        return None
    c = color.strip()
    if not c:
        return None
    if c.startswith("#"):
        c = c[1:]
    # if it looks like hex, lowercase it; otherwise pass through (named)
    if re.fullmatch(r"[0-9A-Fa-f]{6}", c):
        return c.lower()
    return c.lower()


def search_photos(
    query: str,
    api_key: str,
    color: str | None = None,
    orientation: str | None = "landscape",
    locale: str = "ru-RU",
    per_page: int = 80,
    timeout: float = 12.0,
    base_url: str | None = None,
    image_proxy: str | None = None,
) -> list[dict[str, Any]]:
    if not api_key:
        logger.warning("Pexels API key missing")
        return []
    if not query or not query.strip():
        return []

    search_url = (base_url or DEFAULT_API_BASE).rstrip("/") + "/search"
    params: dict[str, str | int] = {
        "query": query.strip(),
        "per_page": min(80, max(1, per_page)),
        "locale": locale,
    }
    norm_color = _normalize_color(color)
    if norm_color:
        params["color"] = norm_color
    if orientation:
        params["orientation"] = orientation

    try:
        resp = requests.get(
            search_url,
            params=params,
            headers={"Authorization": api_key, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        logger.warning("Pexels request failed: %s", exc)
        return []

    if resp.status_code != 200:
        logger.warning("Pexels %s: %s", resp.status_code, resp.text[:200])
        return []

    try:
        data = resp.json()
    except ValueError:
        logger.warning("Pexels returned non-JSON")
        return []

    out: list[dict[str, Any]] = []
    for p in data.get("photos") or []:
        src = p.get("src") or {}
        out.append({
            "id": p.get("id"),
            "page_url": p.get("url"),
            "image_url": _rewrite_img(src.get("large") or src.get("large2x") or src.get("medium"), image_proxy),
            "image_url_small": _rewrite_img(src.get("medium") or src.get("small") or src.get("tiny"), image_proxy),
            "alt": p.get("alt") or "",
            "avg_color": p.get("avg_color"),
            "photographer": p.get("photographer"),
            "photographer_id": p.get("photographer_id"),
            "width": p.get("width"),
            "height": p.get("height"),
        })
    return out


def pick_diverse(
    photos: list[dict[str, Any]],
    count: int = 6,
) -> list[dict[str, Any]]:
    """Берёт первые `count` фото без повторов одного фотографа."""
    chosen: list[dict[str, Any]] = []
    used_photographers: set[Any] = set()
    used_ids: set[Any] = set()

    for p in photos:
        if len(chosen) >= count:
            break
        pid = p.get("id")
        photographer = p.get("photographer_id")
        if pid in used_ids:
            continue
        if photographer is not None and photographer in used_photographers:
            continue
        chosen.append(p)
        used_ids.add(pid)
        if photographer is not None:
            used_photographers.add(photographer)

    # Если не добрали 6 — отпускаем уникальность фотографа.
    if len(chosen) < count:
        for p in photos:
            if len(chosen) >= count:
                break
            pid = p.get("id")
            if pid in used_ids:
                continue
            chosen.append(p)
            used_ids.add(pid)

    return chosen
