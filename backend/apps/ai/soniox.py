"""
Клиент к Soniox Speech-to-Text (async API).

Поток: upload файла → создать transcription job → опросить статус → забрать
transcript. Документация: https://soniox.com/docs/stt/async/async-transcription
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

API_BASE = "https://api.soniox.com"
DEFAULT_MODEL = "stt-async-v4"


class SonioxError(Exception):
    pass


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _upload_file(api_key: str, audio_bytes: bytes, filename: str, mime: str, timeout: float) -> str:
    files = {"file": (filename, audio_bytes, mime)}
    try:
        resp = requests.post(
            f"{API_BASE}/v1/files",
            headers=_auth_headers(api_key),
            files=files,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise SonioxError(f"upload failed: {exc}") from exc
    if resp.status_code >= 400:
        raise SonioxError(f"upload {resp.status_code}: {resp.text[:300]}")
    file_id = (resp.json() or {}).get("id")
    if not file_id:
        raise SonioxError(f"upload response without id: {resp.text[:200]}")
    return file_id


def _create_transcription(api_key: str, file_id: str, language_hints: list[str], timeout: float) -> str:
    body: dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "file_id": file_id,
    }
    if language_hints:
        body["language_hints"] = language_hints
    try:
        resp = requests.post(
            f"{API_BASE}/v1/transcriptions",
            headers={**_auth_headers(api_key), "Content-Type": "application/json"},
            json=body,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise SonioxError(f"create_transcription failed: {exc}") from exc
    if resp.status_code >= 400:
        raise SonioxError(f"create_transcription {resp.status_code}: {resp.text[:300]}")
    tid = (resp.json() or {}).get("id")
    if not tid:
        raise SonioxError(f"create_transcription response without id: {resp.text[:200]}")
    return tid


def _poll_status(api_key: str, transcription_id: str, timeout: float, max_wait: float) -> None:
    deadline = time.time() + max_wait
    delay = 0.5
    while time.time() < deadline:
        try:
            resp = requests.get(
                f"{API_BASE}/v1/transcriptions/{transcription_id}",
                headers=_auth_headers(api_key),
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise SonioxError(f"poll failed: {exc}") from exc
        if resp.status_code >= 400:
            raise SonioxError(f"poll {resp.status_code}: {resp.text[:300]}")
        data = resp.json() or {}
        status = data.get("status")
        if status == "completed":
            return
        if status == "error":
            raise SonioxError(f"transcription failed: {data.get('error_message') or data}")
        time.sleep(delay)
        delay = min(delay * 1.4, 2.0)
    raise SonioxError(f"transcription timed out after {max_wait}s")


def _get_transcript_text(api_key: str, transcription_id: str, timeout: float) -> str:
    try:
        resp = requests.get(
            f"{API_BASE}/v1/transcriptions/{transcription_id}/transcript",
            headers=_auth_headers(api_key),
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise SonioxError(f"get_transcript failed: {exc}") from exc
    if resp.status_code >= 400:
        raise SonioxError(f"get_transcript {resp.status_code}: {resp.text[:300]}")
    data = resp.json() or {}
    # Soniox returns either {"text": "..."} or {"tokens": [{"text": "..."}, ...]}.
    if isinstance(data.get("text"), str) and data["text"].strip():
        return data["text"].strip()
    tokens = data.get("tokens") or []
    if not tokens:
        return ""
    parts: list[str] = []
    for tok in tokens:
        t = (tok.get("text") or "")
        if not t:
            continue
        parts.append(t)
    text = "".join(parts)
    # Soniox often emits tokens with leading space already; collapse double spaces.
    return " ".join(text.split()).strip()


def _delete_resources(api_key: str, file_id: str | None, transcription_id: str | None) -> None:
    """Лучшая попытка зачистить ресурсы Soniox после успешного забора текста."""
    headers = _auth_headers(api_key)
    if transcription_id:
        try:
            requests.delete(f"{API_BASE}/v1/transcriptions/{transcription_id}", headers=headers, timeout=5)
        except requests.RequestException:
            pass
    if file_id:
        try:
            requests.delete(f"{API_BASE}/v1/files/{file_id}", headers=headers, timeout=5)
        except requests.RequestException:
            pass


def transcribe(
    api_key: str,
    audio_bytes: bytes,
    filename: str = "recording.webm",
    mime: str = "audio/webm",
    language_hints: list[str] | None = None,
    request_timeout: float = 30.0,
    poll_max_wait: float = 90.0,
) -> str:
    """End-to-end: upload → start job → poll → return plain text."""
    if not api_key:
        raise SonioxError("SONIOX_API_KEY is not configured")
    if not audio_bytes:
        raise SonioxError("empty audio")

    file_id: str | None = None
    transcription_id: str | None = None
    try:
        file_id = _upload_file(api_key, audio_bytes, filename, mime, request_timeout)
        transcription_id = _create_transcription(
            api_key, file_id, language_hints or ["ru", "en"], request_timeout
        )
        _poll_status(api_key, transcription_id, request_timeout, poll_max_wait)
        text = _get_transcript_text(api_key, transcription_id, request_timeout)
        return text
    finally:
        _delete_resources(api_key, file_id, transcription_id)
