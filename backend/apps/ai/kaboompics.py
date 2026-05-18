"""
Парсер галереи kaboompics.com.

Сайт отдаёт классический SSR-HTML, у каждой фотографии есть блок
<figure class="photo-tile" id="photo-{ID}" data-href="...">
    <img src="/cache_1/.../preview.jpeg"
         data-popup-image="/cache_1/.../1x.jpeg"
         srcset="/cache_1/.../1x.jpeg 1x, /cache_1/.../2x.jpeg 2x">
</figure>
Внутри секции #gallery > section.photos.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://kaboompics.com"
GALLERY_URL = f"{BASE_URL}/gallery"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

_FIGURE_RE = re.compile(
    r'<figure\b(?P<attrs>[^>]*?class="[^"]*\bphoto-tile\b[^"]*"[^>]*?)>'
    r'(?P<body>.*?)</figure>',
    re.DOTALL,
)
_IMG_RE = re.compile(r'<img\b[^>]*>', re.DOTALL)
_ATTR_RE_TPL = r'\b{name}="([^"]*)"'


def _attr(tag: str, name: str) -> str | None:
    m = re.search(_ATTR_RE_TPL.format(name=re.escape(name)), tag)
    return m.group(1) if m else None


def _absolutise(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return BASE_URL + url
    return url


def _parse_srcset(srcset: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not srcset:
        return out
    for part in srcset.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split()
        if not bits:
            continue
        url = _absolutise(bits[0])
        density = bits[1] if len(bits) > 1 else "1x"
        if url:
            out[density] = url
    return out


def parse_photos(html: str) -> list[dict]:
    photos: list[dict] = []
    for m in _FIGURE_RE.finditer(html):
        attrs = m.group("attrs") or ""
        body = m.group("body") or ""

        figure_id = _attr(attrs, "id") or ""
        photo_id = figure_id.replace("photo-", "") if figure_id.startswith("photo-") else figure_id
        page_url = _absolutise(_attr(attrs, "data-href"))

        img_match = _IMG_RE.search(body)
        if not img_match:
            continue
        img_tag = img_match.group(0)
        srcset = _parse_srcset(_attr(img_tag, "srcset") or "")
        popup = _absolutise(_attr(img_tag, "data-popup-image"))
        src = _absolutise(_attr(img_tag, "src"))
        alt = _attr(img_tag, "alt") or ""

        url_1x = srcset.get("1x") or popup or src
        url_2x = srcset.get("2x") or url_1x
        if not url_1x:
            continue

        photos.append({
            "id": photo_id,
            "page_url": page_url,
            "image_url": url_2x,
            "image_url_small": url_1x,
            "alt": alt,
        })
    return photos


def _fetch_search(query: str, timeout: float) -> list[dict]:
    try:
        url = f"{GALLERY_URL}?{urlencode({'search': query})}"
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("kaboompics fetch failed for %r: %s", query, exc)
        return []
    try:
        return parse_photos(resp.text)
    except Exception:
        logger.exception("kaboompics parse failed")
        return []


def search_photos(query: str, limit: int = 1, timeout: float = 10.0) -> list[dict]:
    """Каскадный поиск: полный запрос → 2 слова → 1 слово.

    Kaboompics ищет по точному совпадению тегов/названий; 4+ слов почти
    всегда возвращают 0 результатов. Поэтому если ничего не нашлось —
    укорачиваем запрос и пробуем снова.
    """
    if not query or not query.strip():
        return []
    words = query.strip().split()
    candidates: list[str] = [" ".join(words)]
    if len(words) >= 3:
        candidates.append(" ".join(words[:2]))
    if len(words) >= 2:
        candidates.append(words[0])
    seen: set[str] = set()
    for q in candidates:
        if q in seen:
            continue
        seen.add(q)
        photos = _fetch_search(q, timeout)
        if photos:
            return photos[:limit] if limit else photos
    return []
