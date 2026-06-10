"""
WorldTravel v7.0 — Evolution API messaging.
"""
import logging
import requests
from config import EVOLUTION_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE
from utils.helpers import to_api_number

log = logging.getLogger(__name__)


def _headers() -> dict:
    return {
        "apikey":       EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }


def send_message(to: str, text: str) -> bool:
    """Отправить текстовое сообщение через Evolution API."""
    number = to_api_number(to)
    try:
        r = requests.post(
            f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}",
            headers=_headers(),
            json={"number": number, "text": text},
            timeout=12,
        )
        ok = r.status_code in (200, 201)
        if ok:
            log.info(f"sendText ✓ → {number}: {text[:55]}")
        else:
            log.error(f"sendText [{r.status_code}] → {number}: {r.text[:200]}")
        return ok
    except Exception as e:
        log.error(f"send_message: {e}")
        return False


def send_photo(to: str, url: str, caption: str = "") -> bool:
    """Отправить фото через Evolution API."""
    number = to_api_number(to)
    try:
        r = requests.post(
            f"{EVOLUTION_URL}/message/sendMedia/{EVOLUTION_INSTANCE}",
            headers=_headers(),
            json={
                "number":    number,
                "mediatype": "image",
                "media":     url,
                "caption":   caption,
            },
            timeout=20,
        )
        ok = r.status_code in (200, 201)
        if ok:
            log.info(f"sendMedia ✓ → {number}: {caption[:40]}")
        else:
            log.error(f"sendMedia [{r.status_code}] → {number}: {r.text[:200]}")
        return ok
    except Exception as e:
        log.error(f"send_photo: {e}")
        return False


def send_photos_for_queries(chat_id: str, photo_queries: list[str]) -> None:
    """
    Отправляет фото для каждого направления из списка.
    Дедуплицирует URL, чтобы один снимок не ушёл дважды.
    Исправляет баг: раньше при нескольких турах отправлялось только первое фото.
    """
    import time
    from database.tours import get_tour_photos

    if not photo_queries:
        return

    sent_urls: set[str] = set()
    first_photo = True

    for query in photo_queries[:3]:          # максимум 3 направления
        query = str(query).strip()
        if len(query) < 2:                   # пропускаем пустые / мусорные строки
            continue
        photos = get_tour_photos(query, limit=2)
        for url, caption in photos:
            if url in sent_urls:
                continue
            sent_urls.add(url)
            delay = 0.3 if first_photo else 0.9
            time.sleep(delay)
            send_photo(chat_id, url, caption)
            first_photo = False

    if not sent_urls and photo_queries:
        # Ни одного фото не нашлось — сообщаем только о первом запросе
        send_message(chat_id, f"(Фото для «{photo_queries[0]}» пока нет в базе 📸)")