import json
import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class DeepSeekError(Exception):
    pass


class DeepSeekClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        if not self.api_key:
            raise DeepSeekError("DEEPSEEK_API_KEY не задан в .env")

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        response_format: dict | None = None,
    ) -> str:
        """Возвращает `content` ассистент-сообщения.

        Никаких ограничений по токенам не передаём — DeepSeek сам выбирает
        потолок для конкретной модели. Это критично, потому что:
          - reasoner отдельно тратит токены на `reasoning_content`;
          - structured-режимы (мудборд / шрифты) с историей предыдущего
            payload + `_chain_of_thought` могут давать большой ответ.
        Любая фиксированная цифра рискует обрезать JSON.
        """
        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=300)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("DeepSeek request failed")
            raise DeepSeekError(f"DeepSeek API error: {exc}") from exc
        data = resp.json()
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError) as exc:
            raise DeepSeekError(f"Некорректный ответ DeepSeek: {data}") from exc
        if finish_reason == "length":
            usage = data.get("usage") or {}
            logger.warning(
                "DeepSeek finish_reason=length (model default cap), usage=%s",
                usage,
            )
        return content

    def chat_json(self, messages: list[dict[str, str]], **kwargs) -> dict:
        raw = self.chat(messages, response_format={"type": "json_object"}, **kwargs)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            tail = "…<обрезано>" if len(raw) > 300 else ""
            raise DeepSeekError(
                f"Не смог распарсить JSON (длина {len(raw)} симв.): {raw[:300]}{tail}"
            ) from exc
