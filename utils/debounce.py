"""
WorldTravel v7.0 — Debounce & Rate Limit.
Thread-safe реализации.
"""
import logging
import threading
import time
from collections import deque
from config import DEBOUNCE_SECONDS, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW

log = logging.getLogger(__name__)

# ── Debounce ───────────────────────────────────────────────────────────────
_debounce_buf: dict  = {}
_debounce_lock       = threading.Lock()


def debounce_message(chat_id: str, text: str, meta: dict,
                     callback) -> None:
    """
    Накапливает сообщения из одного чата за DEBOUNCE_SECONDS секунд,
    затем передаёт объединённый текст в callback(chat_id, meta, combined_text).
    """
    with _debounce_lock:
        if chat_id in _debounce_buf:
            _debounce_buf[chat_id]["timer"].cancel()
            _debounce_buf[chat_id]["messages"].append(text)
        else:
            _debounce_buf[chat_id] = {"messages": [text], "meta": meta}

        def _flush():
            with _debounce_lock:
                entry = _debounce_buf.pop(chat_id, None)
            if not entry:
                return
            combined = "\n".join(entry["messages"])
            log.info(f"[DEBOUNCE] {chat_id} — {len(entry['messages'])} msgs: {combined[:80]}")
            threading.Thread(
                target=callback,
                args=(chat_id, entry["meta"], combined),
                daemon=True,
            ).start()

        timer = threading.Timer(DEBOUNCE_SECONDS, _flush)
        timer.daemon = True
        _debounce_buf[chat_id]["timer"] = timer
        timer.start()


# ── Rate limit ─────────────────────────────────────────────────────────────
_rate_counters: dict = {}
_rate_lock           = threading.Lock()


def is_rate_limited(chat_id: str) -> bool:
    """True если клиент превысил лимит сообщений за RATE_LIMIT_WINDOW секунд."""
    now = time.time()
    with _rate_lock:
        if chat_id not in _rate_counters:
            _rate_counters[chat_id] = deque()
        dq = _rate_counters[chat_id]
        while dq and now - dq[0] > RATE_LIMIT_WINDOW:
            dq.popleft()
        dq.append(now)
        if len(dq) > RATE_LIMIT_COUNT:
            log.warning(f"[RATE LIMIT] {chat_id}")
            return True
    return False


def reset_rate_limit(chat_id: str) -> None:
    with _rate_lock:
        _rate_counters.pop(chat_id, None)