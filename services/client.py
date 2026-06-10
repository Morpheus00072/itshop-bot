"""
WorldTravel v7.0 — Client message processor.
Главная функция process_message() + check_followups() для планировщика.
"""
import logging
import time

import state
from config import (
    STATE_IDLE, STATE_BOOKING, STATE_CONFIRM,
    BOSS_JID, MBANK_QR_URL
)
from ai_core.prompts import ask_ai, ai_check_booking
from database.sessions import (
    save_message, get_history,
    has_greeted, mark_greeted, update_last_seen,
    get_followup_candidates,
)
from database.tours import (
    get_hot_tours, get_tour_by_name, is_bot_paused
)
from services.messaging import (
    send_message, send_photo, send_photos_for_queries
)
from services.booking import (
    notify_boss_booking, process_booking_photos_and_confirm
)
from utils.security import is_injection, is_boss_command_attempt
from utils.intent import (
    is_cancel, is_book_related, is_hot_request, is_payment_request
)
from utils.helpers import is_boss_phone, jid_to_num

log = logging.getLogger(__name__)


# ── Main processor ─────────────────────────────────────────────────────────

def process_message(chat_id: str, meta: dict, user_text: str) -> None:
    """
    Центральный обработчик входящего сообщения от клиента.
    Вызывается из debounce (в отдельном потоке).
    """
    sender_phone = meta.get("sender_phone", "")
    log.info(f"[PROCESS] {sender_phone}: {user_text[:80]}")

    sd    = state.client_states.get(chat_id, {"state": STATE_IDLE})
    cur_state = sd.get("state", STATE_IDLE)

    # ── Muted (менеджер взял чат) ──────────────────────────────────────
    if cur_state == "muted" and time.time() < sd.get("until", 0):
        log.info(f"[MUTED] {sender_phone} — bot silenced")
        return

    # ── Rate limited ───────────────────────────────────────────────────
    if cur_state == "rate_limited":
        return

    # ── STATE: BOOKING (ожидаем «да»/«нет») ───────────────────────────
    if cur_state == STATE_BOOKING:
        t = user_text.lower().strip()
        if t in ("да", "yes", "ок", "ok", "+", "подтверждаю", "ага", "давай"):
            notify_boss_booking(chat_id, sender_phone)
            return
        if is_cancel(user_text):
            state.client_states.pop(chat_id, None)
            send_message(chat_id, "Заявка отменена! Когда соберётесь — пишите 😊✈️")
            return
        # Что-то другое — выходим из режима бронирования
        state.client_states.pop(chat_id, None)

    # ── STATE: CONFIRM (ждём подтверждения от менеджера) ──────────────
    if cur_state == STATE_CONFIRM:
        if is_payment_request(user_text):
            send_message(
                chat_id,
                "⏳ Ваша заявка ещё на проверке у менеджера.\n"
                "Реквизиты придут после подтверждения. Спасибо! 🙏"
            )
        else:
            send_message(chat_id, "Ваша заявка на проверке! Подождите немного 🙏")
        return

    # ── Защита от инъекций ─────────────────────────────────────────────
    if is_injection(user_text):
        send_message(chat_id, "Я консультант WorldTravel — помогу подобрать тур! ✈️😊")
        return

    if is_boss_command_attempt(user_text):
        send_message(chat_id, "Эта функция только для менеджера. Чем помочь с выбором тура? 😊")
        return

    greeted = has_greeted(chat_id)
    update_last_seen(chat_id)

    # ── Отмена ────────────────────────────────────────────────────────
    if is_cancel(user_text):
        state.client_states.pop(chat_id, None)
        send_message(chat_id, "Хорошо! Когда соберётесь в путешествие — пишите! ✈️😊")
        return

    # ── Оплата / реквизиты ────────────────────────────────────────────
    if is_payment_request(user_text):
        save_message(chat_id, "user", user_text)
        if not greeted:
            mark_greeted(chat_id)
        send_message(
            chat_id,
            "💳 Оплата через Mbank:\n📱 +996 555 212 525\n"
            "Получатель: WorldTravel\n\nQR-код для быстрой оплаты:"
        )
        time.sleep(0.3)
        send_photo(chat_id, MBANK_QR_URL, "Отсканируйте QR в приложении Mbank ✅")
        save_message(chat_id, "assistant", "Отправлен QR-код Mbank для оплаты.")
        return

    # ── Горящие туры ──────────────────────────────────────────────────
    if is_hot_request(user_text):
        save_message(chat_id, "user", user_text)
        hot = get_hot_tours(4)
        if hot:
            answer = (
                f"🔥 Горящие туры прямо сейчас:\n\n{hot}\n\n"
                "Интересует что-то конкретное? Расскажу подробнее! 😊"
            )
            if not greeted:
                mark_greeted(chat_id)
            save_message(chat_id, "assistant", answer)
            send_message(chat_id, answer)
            return

    # ── Основной AI-ответ ──────────────────────────────────────────────
    save_message(chat_id, "user", user_text)
    answer, should_respond, aux = ask_ai(chat_id, user_text, is_first=not greeted)

    # Принудительный ответ на короткие фразы (даты, числа, уточнения)
    if not should_respond and len(user_text.split()) <= 6:
        should_respond = True

    if not greeted:
        mark_greeted(chat_id)

    # ── Запрос живого оператора ────────────────────────────────────────
    if aux.get("call_manager"):
        state.client_states[chat_id] = {"state": "muted", "until": time.time() + 1800}
        send_message(chat_id, "Минуточку, переключаю на менеджера! 👨‍💼")
        send_message(BOSS_JID,
                     f"⚠️ Клиент просит живого оператора!\n"
                     f"Чат: +{sender_phone}\nЗапрос: {user_text}")
        return

    # ── Проверка бронирования ──────────────────────────────────────────
    booking_confirmed = False
    if is_book_related(user_text):
        booking = ai_check_booking(user_text, chat_id)
        if booking:
            booking_confirmed = True
            tour_title  = booking.get("tour", "тур")
            price       = int(booking.get("price", 0))
            people      = max(int(booking.get("people", 1) or 1), 1)
            travel_date = booking.get("date", "")
            tour_data   = get_tour_by_name(tour_title)
            # Сохраняем AI-ответ в историю (но не отправляем — отправим карточку)
            save_message(chat_id, "assistant", answer)
            process_booking_photos_and_confirm(
                chat_id, tour_title, price, people, travel_date, tour_data
            )

    # ── Обычный ответ + фото ───────────────────────────────────────────
    if not booking_confirmed:
        save_message(chat_id, "assistant", answer)
        if should_respond and answer:
            send_message(chat_id, answer)
        else:
            log.info(f"[SILENT] {chat_id}")

        # ▼▼▼ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: отправка фото для ВСЕХ направлений ▼▼▼
        photo_queries = aux.get("photo_search_queries", [])
        if photo_queries:
            send_photos_for_queries(chat_id, photo_queries)
        # ▲▲▲ ─────────────────────────────────────────────────────────── ▲▲▲
    else:
        # Ответ AI сохранён выше, но не отправлен клиенту
        pass


# ── Follow-up scheduler ────────────────────────────────────────────────────

def check_followups() -> None:
    """
    Отправляет напоминания клиентам, которые были активны 1–2 часа назад.
    Вызывается планировщиком каждые 15 минут.
    """
    if is_bot_paused():
        return

    # Сброс followup_sent раз в 5000+ записей (антиутечка)
    if len(state.followup_sent) > 5000:
        state.followup_sent.clear()

    # Рабочие часы Бишкека (UTC+6)
    import datetime
    now_local = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    from config import FOLLOWUP_HOUR_START, FOLLOWUP_HOUR_END
    if not (FOLLOWUP_HOUR_START <= now_local.hour < FOLLOWUP_HOUR_END):
        log.debug(f"[FOLLOWUP] вне рабочих часов ({now_local.hour}:00 БШК)")
        return

    candidates = get_followup_candidates()
    for cid in candidates:
        if cid in state.followup_sent:
            continue
        if is_boss_phone(jid_to_num(cid)):
            continue
        cur_state = state.client_states.get(cid, {}).get("state", STATE_IDLE)
        if cur_state in (STATE_BOOKING, STATE_CONFIRM, "rate_limited"):
            continue

        hot = get_hot_tours(3)
        msg = "Привет! ✈️ Ещё думаете над путешествием?"
        if hot:
            msg += f"\n\n🔥 Горящие предложения:\n{hot}"
        msg += "\n\nПишите — подберём идеальный тур! 🌍"
        send_message(cid, msg)
        state.followup_sent.add(cid)
        log.info(f"[FOLLOWUP] sent to {cid}")


# ── Rate limit handler ─────────────────────────────────────────────────────

def handle_rate_limit(chat_id: str, sender_phone: str) -> None:
    state.client_states[chat_id] = {"state": "rate_limited"}
    send_message(
        chat_id,
        "Вы пишете слишком часто. Подождите немного "
        "или свяжитесь с менеджером: +996 755 212 525"
    )
    send_message(
        BOSS_JID,
        f"⚠️ RATE LIMIT\nЧат +{sender_phone} заблокирован.\n"
        f"Для разблокировки: разблокировать {sender_phone}"
    )