"""
WorldTravel v7.0 — Groq API client.
"""
import json
import logging
import re
import time

import requests
from config import GROQ_KEY, GROQ_FAST_MODEL, GROQ_SMART_MODEL

log = logging.getLogger(__name__)

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _call(
    system_prompt: str,
    history: list[dict],
    user_text: str,
    *,
    max_tokens: int = 600,
    temperature: float = 0.35,
    fast: bool = True,
    as_json: bool = False,
) -> str:
    """
    Низкоуровневый вызов Groq с двумя попытками (retry при 429).
    Возвращает сырой текст ответа.
    """
    model = GROQ_FAST_MODEL if fast else GROQ_SMART_MODEL
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    payload: dict = {
        "model":       model,
        "messages":    messages,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "top_p":       0.9,
    }
    if as_json:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type":  "application/json",
    }

    for attempt in range(3):
        try:
            r = requests.post(_GROQ_URL, headers=headers, json=payload, timeout=18)

            # Retry 1: rate limit
            if r.status_code == 429 and attempt == 0:
                log.warning("Groq 429 — retrying in 3s")
                time.sleep(3)
                continue

            # Retry 2: json_validate_failed — модель не смогла выдать валидный JSON.
            # Снимаем json-режим и пробуем бесплатным текстом, потом извлечём JSON регексом.
            if r.status_code == 400 and as_json and attempt == 0:
                err_code = r.json().get("error", {}).get("code", "")
                if err_code == "json_validate_failed":
                    log.warning("Groq json_validate_failed — retrying without JSON mode")
                    payload.pop("response_format", None)  # снимаем json_object режим
                    continue

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        except requests.HTTPError as e:
            log.error(f"Groq HTTP {e.response.status_code}: {e.response.text[:200]}")
            break
        except Exception as e:
            log.error(f"Groq error: {e}")
            break

    return "Сервис перегружен, попробуйте через минуту."


def call_json(
    system_prompt: str,
    history: list[dict],
    user_text: str,
    *,
    max_tokens: int = 600,
    temperature: float = 0.35,
    fast: bool = True,
) -> dict:
    """
    Вызывает Groq в JSON-режиме, возвращает распарсенный dict.
    При ошибке парсинга возвращает {"_raw": raw_text}.
    """
    raw = _call(system_prompt, history, user_text,
                max_tokens=max_tokens, temperature=temperature,
                fast=fast, as_json=True)
    raw_clean = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw_clean)
    except Exception:
        # Fallback: извлечь первый JSON-объект из текста
        m = re.search(r"\{.*\}", raw_clean, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        log.warning(f"Groq JSON parse fail: {raw[:120]}")
        return {"_raw": raw}


def call_text(
    system_prompt: str,
    history: list[dict],
    user_text: str,
    *,
    max_tokens: int = 400,
    temperature: float = 0.35,
    fast: bool = True,
) -> str:
    """Простой текстовый вызов Groq."""
    return _call(system_prompt, history, user_text,
                 max_tokens=max_tokens, temperature=temperature,
                 fast=fast, as_json=False)


def summarize_history(messages: list[dict]) -> str:
    """
    Суммаризирует старые сообщения диалога в 2–3 предложения.
    Используется для скользящего окна истории.
    """
    if not messages:
        return ""
    hist_text = "\n".join(
        f"{m['role'].upper()}: {m['content'][:200]}" for m in messages
    )
    return call_text(
        "Ты помощник. Кратко (2–3 предложения, без лишних деталей) "
        "суммаризируй суть этого разговора о туризме.",
        [],
        hist_text,
        max_tokens=150,
        temperature=0.1,
        fast=True,
    )