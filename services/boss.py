"""
WorldTravel v7.0 — Boss command handler.
"""
import logging
import time

import state
from config import BOSS_JID, STATE_CONFIRM, STATE_IDLE
from ai_core.prompts import ask_ai, ai_parse_boss_cmd
from database.sessions import save_message, get_all_client_jids, get_chat_history_for_boss
from database.tours import (
    is_bot_paused, set_bot_paused,
    db_add_tour, db_remove_tour, db_update_tour_price,
    get_tour_by_name, get_boss_stats,
)
from database.bookings import save_booking
from services.messaging import send_message, send_photo
from utils.helpers import norm, num_to_jid, jid_to_num

log = logging.getLogger(__name__)

BOSS_HELP = """📋 Команды WorldTravel Bot v7.0

🔔 РАССЫЛКА: рассылка [текст]
✉️ НАПИСАТЬ КЛИЕНТУ: написать 996XXX [текст]
✈️ ТУРЫ:
  добавить тур [данные]
  убрать тур [название]
  цена [название] [новая цена]
✅ ЗАЯВКИ: да / нет / заявки
📊 ИНФО: статистика, история
⚙️ БОТ: пауза, запустить
🔓 разблокировать [номер]
❓ помощь"""


def handle_boss(chat_id: str, text: str) -> None:
    """Обрабатывает входящее сообщение от владельца агентства."""
    text_lower = text.lower().strip()

    # ── Быстрые текстовые команды ──────────────────────────────────────
    is_yes = text_lower in ("да", "yes", "ок", "ok", "подтвердить", "+")
    is_no  = text_lower in ("нет", "no", "отклонить", "-", "отмена")

    if is_yes and state.pending_boss_confirms:
        _confirm_booking(chat_id, text)
        return

    if is_no and state.pending_boss_confirms:
        _reject_booking(chat_id)
        return

    # ── AI-парсинг команды ─────────────────────────────────────────────
    cmd = ai_parse_boss_cmd(text)
    c   = cmd.get("cmd", "chat")

    if c == "confirm":
        _confirm_booking(chat_id, text); return
    if c == "reject":
        _reject_booking(chat_id); return

    if c == "pending":
        if not state.pending_boss_confirms:
            send_message(chat_id, "Нет ожидающих заявок."); return
        lines = ["⏳ Ожидают подтверждения:"]
        for pid, d in state.pending_boss_confirms.items():
            lines.append(f"• +{d['sender_phone']} — {d['tour']} ({d['price']})")
        send_message(chat_id, "\n".join(lines)); return

    if c == "broadcast":
        _broadcast(chat_id, cmd.get("message", "").strip()); return

    if c == "write_client":
        phone = norm(cmd.get("phone", ""))
        msg   = cmd.get("message", "").strip()
        if not phone or not msg:
            send_message(chat_id, "❓ Укажите номер и текст."); return
        send_message(num_to_jid(phone), msg)
        send_message(chat_id, f"✅ Отправлено +{phone}"); return

    if c == "add_tour":
        r = db_add_tour(
            cmd.get("title", ""), cmd.get("destination", ""),
            cmd.get("country", ""), cmd.get("region", "Мир"),
            cmd.get("duration", "7 дней"), int(cmd.get("price", 0)),
            cmd.get("description", ""), cmd.get("tour_type", "Классический")
        )
        send_message(chat_id, r)
        # Обновляем RAG после добавления тура
        _refresh_rag()
        return

    if c == "update_price":
        r = db_update_tour_price(cmd.get("name", ""), int(cmd.get("price", 0)))
        send_message(chat_id, r)
        _refresh_rag()
        return

    if c == "remove_tour":
        send_message(chat_id, db_remove_tour(cmd.get("name", "")))
        _refresh_rag()
        return

    if c == "stats":
        send_message(chat_id, get_boss_stats()); return

    if c == "history":
        send_message(chat_id, "⏳ Загружаю историю...")
        h = get_chat_history_for_boss()
        for i in range(0, len(h), 3000):
            send_message(chat_id, h[i:i + 3000])
            time.sleep(0.3)
        return

    if c == "pause":
        set_bot_paused(True)
        send_message(chat_id, "⏸️ Бот остановлен.")
        return

    if c == "resume":
        set_bot_paused(False)
        send_message(chat_id, "▶️ Бот запущен!")
        return

    if c == "unblock":
        phone = norm(cmd.get("phone", ""))
        if not phone:
            send_message(chat_id, "❓ Укажите номер.")
            return
        target = f"{phone}@s.whatsapp.net"
        state.client_states.pop(target, None)
        from utils.debounce import reset_rate_limit
        reset_rate_limit(target)
        send_message(chat_id, f"✅ +{phone} разблокирован"); return

    if c == "help":
        send_message(chat_id, BOSS_HELP); return

    # ── Свободный чат с AI ─────────────────────────────────────────────
    time.sleep(0.3)
    answer, _, _ = ask_ai(chat_id, text, is_first=False, is_boss=True)
    save_message(chat_id, "assistant", answer)
    send_message(chat_id, answer)


# ── Private helpers ────────────────────────────────────────────────────────

def _confirm_booking(chat_id: str, text: str) -> None:
    if not state.pending_boss_confirms:
        send_message(chat_id, "Нет ожидающих заявок.")
        return
    pid = next(iter(state.pending_boss_confirms))
    d   = state.pending_boss_confirms.pop(pid)

    tour_data = get_tour_by_name(d["tour"])
    tour_id   = tour_data["id"] if tour_data else 0
    tour_price = tour_data["price"] if tour_data else 0

    save_booking(
        d["client_jid"], d["sender_phone"],
        tour_id, d["tour"], tour_price,
        d.get("people", 1), d.get("date", "")
    )
    send_message(
        d["client_jid"],
        f"✅ Ваша заявка подтверждена! Тур «{d['tour']}» забронирован.\n"
        "Менеджер свяжется для уточнения. Счастливого путешествия! 🎉✈️"
    )
    answer = (
        f"✅ Подтверждено!\n"
        f"Клиент: +{d['sender_phone']}\n"
        f"Тур: {d['tour']}\nСумма: {d['price']}"
    )
    save_message(chat_id, "assistant", answer)
    send_message(chat_id, answer)
    state.client_states.pop(d["client_jid"], None)


def _reject_booking(chat_id: str) -> None:
    if not state.pending_boss_confirms:
        send_message(chat_id, "Нет ожидающих заявок.")
        return
    pid = next(iter(state.pending_boss_confirms))
    d   = state.pending_boss_confirms.pop(pid)
    send_message(
        d["client_jid"],
        "❌ К сожалению, бронирование не подтверждено.\n"
        "Свяжитесь с менеджером: +996 755 212 525"
    )
    answer = f"❌ Отклонено.\nКлиент: +{d['sender_phone']}\nТур: {d['tour']}"
    save_message(chat_id, "assistant", answer)
    send_message(chat_id, answer)
    state.client_states.pop(d["client_jid"], None)


def _broadcast(chat_id: str, msg: str) -> None:
    if not msg:
        send_message(chat_id, "❓ Укажите текст рассылки.")
        return
    jids = get_all_client_jids()
    send_message(chat_id, f"📢 Рассылка {len(jids)} клиентам...\n{msg}")
    sent = 0
    for j in jids:
        if send_message(j, msg):
            sent += 1
        time.sleep(0.8)
    send_message(chat_id, f"✅ Рассылка завершена: {sent}/{len(jids)}")


def _refresh_rag() -> None:
    """Обновляет RAG-индекс после изменения каталога."""
    try:
        from ai_core.rag import tour_rag
        from database.tours import fetch_all_tours_for_rag
        tours = fetch_all_tours_for_rag()
        tour_rag.build_index(tours)
        log.info("RAG: индекс обновлён после изменения каталога")
    except Exception as e:
        log.error(f"RAG refresh after catalog change: {e}")