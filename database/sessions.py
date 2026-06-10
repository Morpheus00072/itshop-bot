"""
WorldTravel v7.0 — Chat session & history queries.
"""
import logging
from database.connection import get_db
from config import HISTORY_LIMIT, HISTORY_WINDOW
import state

log = logging.getLogger(__name__)


# ── Sessions ───────────────────────────────────────────────────────────────

def has_greeted(chat_id: str) -> bool:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("SELECT greeted FROM chat_sessions WHERE chat_id=%s", (chat_id,))
        row = cur.fetchone()
        db.close()
        return bool(row and row[0])
    except Exception:
        return False


def mark_greeted(chat_id: str) -> None:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO chat_sessions (chat_id, greeted) VALUES (%s, TRUE) "
            "ON DUPLICATE KEY UPDATE greeted=TRUE, last_seen=CURRENT_TIMESTAMP",
            (chat_id,)
        )
        db.commit(); db.close()
    except Exception as e:
        log.error(f"mark_greeted: {e}")


def update_last_seen(chat_id: str) -> None:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO chat_sessions (chat_id, greeted) VALUES (%s, FALSE) "
            "ON DUPLICATE KEY UPDATE last_seen=CURRENT_TIMESTAMP",
            (chat_id,)
        )
        db.commit(); db.close()
    except Exception as e:
        log.error(f"update_last_seen: {e}")


def get_all_client_jids() -> list[str]:
    from utils.helpers import norm
    from config import BOSS_NUMBER, BOSS_JID
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT chat_id FROM chat_sessions "
            "WHERE greeted=TRUE AND chat_id NOT LIKE '%%@g.us'"
        )
        rows = cur.fetchall(); db.close()
        boss_jid2 = f"{norm(BOSS_NUMBER)}@c.us"
        boss_nums = {norm(BOSS_NUMBER), norm(BOSS_JID), norm(boss_jid2)}
        return [r[0] for r in rows if norm(r[0]) not in boss_nums]
    except Exception as e:
        log.error(f"get_all_client_jids: {e}")
        return []


def get_followup_candidates() -> list[str]:
    """Клиенты, которые были активны 1–2 часа назад (для follow-up)."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT chat_id FROM chat_sessions "
            "WHERE last_seen BETWEEN NOW()-INTERVAL 2 HOUR AND NOW()-INTERVAL 1 HOUR "
            "  AND greeted=TRUE AND chat_id NOT LIKE '%%@g.us'"
        )
        rows = cur.fetchall(); db.close()
        return [r[0] for r in rows]
    except Exception as e:
        log.error(f"get_followup_candidates: {e}")
        return []


# ── History ────────────────────────────────────────────────────────────────

def save_message(chat_id: str, role: str, message: str) -> None:
    """Сохраняет сообщение и удаляет старые сверх лимита."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO chat_history (chat_id, role, message) VALUES (%s, %s, %s)",
            (chat_id, role, message)
        )
        # Оставляем только последние HISTORY_LIMIT*2 записей
        cur.execute(
            "DELETE FROM chat_history WHERE chat_id=%s AND id NOT IN ("
            "  SELECT id FROM (SELECT id FROM chat_history WHERE chat_id=%s "
            "                  ORDER BY created_at DESC LIMIT %s) AS k)",
            (chat_id, chat_id, HISTORY_LIMIT * 2)
        )
        db.commit(); db.close()
    except Exception as e:
        log.error(f"save_message: {e}")


def get_history(chat_id: str) -> list[dict]:
    """
    Возвращает историю для Groq с механизмом скользящего окна:
    — Если в RAM есть саммари старых сообщений — добавляет его первым.
    — Потом идут последние HISTORY_WINDOW полных сообщений.
    """
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT role, message FROM chat_history WHERE chat_id=%s "
            "ORDER BY created_at ASC LIMIT %s",
            (chat_id, HISTORY_LIMIT * 2)
        )
        rows = cur.fetchall(); db.close()
    except Exception:
        return []

    # Дедупликация подряд идущих ролей
    cleaned: list[dict] = []
    for role, msg in rows:
        content = str(msg).strip()
        if not content:
            continue
        if cleaned and cleaned[-1]["role"] == role:
            cleaned[-1]["content"] += "\n" + content
        else:
            cleaned.append({"role": role, "content": content})

    if len(cleaned) <= HISTORY_WINDOW:
        return cleaned

    # Скользящее окно: recent + summary prefix
    recent = cleaned[-HISTORY_WINDOW:]
    summary = state.history_summaries.get(chat_id)
    if summary:
        return [
            {"role": "user",      "content": f"[Краткое содержание предыдущего диалога]: {summary}"},
            {"role": "assistant", "content": "Хорошо, продолжаем."},
            *recent
        ]
    return recent


def get_chat_history_for_boss() -> str:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT chat_id, role, message FROM chat_history "
            "ORDER BY chat_id, created_at DESC LIMIT 60"
        )
        rows = cur.fetchall(); db.close()
        if not rows:
            return "История пуста."
        from utils.helpers import jid_to_num
        lines: list[str] = []
        cur_chat = None
        for chat_id, role, msg in rows:
            phone = jid_to_num(chat_id)
            if phone != cur_chat:
                cur_chat = phone
                lines.append(f"\n📱 +{phone}:")
            icon = "👤" if role == "user" else "🤖"
            lines.append(f"  [{icon}] {str(msg)[:90]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"