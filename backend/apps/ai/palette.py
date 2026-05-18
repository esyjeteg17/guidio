"""
Извлечение доминирующего цвета из набора картинок и генерация
производной палитры через HLS-сдвиги.
"""

from __future__ import annotations

import colorsys
import logging
from io import BytesIO

import requests
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _fetch(url: str, timeout: float = 8.0) -> bytes | None:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        r.raise_for_status()
        return r.content
    except requests.RequestException as exc:
        logger.debug("image fetch failed %s: %s", url, exc)
        return None


def _dominant_rgb(image_bytes: bytes) -> tuple[int, int, int] | None:
    """Самый «характерный» цвет — после квантизации на 8 кластеров,
    отбрасывая околобелые/чёрные крайности."""
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        return None
    img.thumbnail((120, 120))
    try:
        q = img.quantize(colors=8, kmeans=1)
    except Exception:
        q = img.quantize(colors=8)
    palette = q.getpalette() or []
    counts = sorted(q.getcolors() or [], reverse=True)
    if not counts or not palette:
        return None
    fallback = None
    for count, idx in counts:
        r, g, b = palette[idx * 3 : idx * 3 + 3]
        if fallback is None:
            fallback = (r, g, b)
        # отбрасываем почти-белый (фон студии) и почти-чёрный
        if r + g + b > 720:
            continue
        if r + g + b < 60:
            continue
        # отбрасываем безжизненный серый
        mx = max(r, g, b)
        mn = min(r, g, b)
        if mx - mn < 12 and 80 < (r + g + b) / 3 < 200:
            continue
        return (r, g, b)
    return fallback


def _aggregate(colors: list[tuple[int, int, int]]) -> tuple[int, int, int] | None:
    """Группируем цвета в 32-шаговые корзины и берём центр самой большой."""
    if not colors:
        return None
    buckets: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    for c in colors:
        key = (c[0] // 32, c[1] // 32, c[2] // 32)
        buckets.setdefault(key, []).append(c)
    biggest = max(buckets.values(), key=len)
    r = sum(c[0] for c in biggest) // len(biggest)
    g = sum(c[1] for c in biggest) // len(biggest)
    b = sum(c[2] for c in biggest) // len(biggest)
    return (r, g, b)


def derive_base_color(image_urls: list[str]) -> tuple[int, int, int] | None:
    """Скачать картинки, извлечь доминирующие цвета, выбрать самый частый."""
    colors: list[tuple[int, int, int]] = []
    for url in image_urls:
        if not url:
            continue
        data = _fetch(url)
        if not data:
            continue
        c = _dominant_rgb(data)
        if c:
            colors.append(c)
    return _aggregate(colors)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, int(round(v)))) for v in rgb))


def _hls_hex(h: float, l: float, s: float) -> str:
    h = h % 1.0
    l = max(0.0, min(1.0, l))
    s = max(0.0, min(1.0, s))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return _rgb_to_hex((r * 255, g * 255, b * 255))


def build_palette(base_rgb: tuple[int, int, int]) -> list[dict]:
    """Шесть цветов: primary/secondary/accent/neutral/background/text.

    Primary — исходный (со скорректированной светлотой).
    Secondary — тот же hue, светлее и менее насыщенный.
    Accent — комплементарный (hue + 0.5), насыщенный.
    Neutral / background / text — оттеночные нейтрали под общую гамму.
    """
    r, g, b = base_rgb
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)

    primary = _hls_hex(h, max(0.32, min(0.55, l)), max(0.35, s))
    secondary = _hls_hex(h, min(0.85, l + 0.25), max(0.18, s * 0.6))
    accent = _hls_hex(h + 0.5, max(0.45, min(0.6, l + 0.05)), max(0.55, min(0.9, s + 0.2)))
    neutral = _hls_hex(h, 0.55, max(0.05, s * 0.18))
    background = _hls_hex(h, 0.96, max(0.03, s * 0.12))
    text = _hls_hex(h, 0.13, min(0.4, max(0.12, s * 0.4)))

    return [
        {"hex": primary, "name": "Основной", "role": "primary", "usage_percent": 35},
        {"hex": secondary, "name": "Вторичный", "role": "secondary", "usage_percent": 20},
        {"hex": background, "name": "Фон", "role": "background", "usage_percent": 22},
        {"hex": neutral, "name": "Нейтральный", "role": "neutral", "usage_percent": 12},
        {"hex": accent, "name": "Акцент", "role": "accent", "usage_percent": 7},
        {"hex": text, "name": "Текст", "role": "text", "usage_percent": 4},
    ]
