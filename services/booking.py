"""
WorldTravel v7.0 — Booking flow.
"""
import logging
import time

import state
from config import STATE_BOOKING, STATE_CONFIRM, PLANE_PHOTO, BOSS_JID
from services.messaging import send_message, send_photo, send_photos_for_queries
from database.sessions import save_message
from database.tours import get_tour_photos
from database.bookings import save_booking

log = logging.getLogger(__name__)


def send_booking_confirmation(chat_id: str, tour_title: str,
                               price: int, num_people: int = 1,
                               travel_date: str = "") -> None:
    """Показывает карточку подтверждения бронирования клиенту."""
    total   = price * num_people
    total_s = f"${total:,}".replace(",", " ")
    state.client_states[chat_id] = {
        "state":  STATE_BOOKING,
        "tour":   tour_title,
        "price":  price,
        "people": num_people,
        "date":   travel_date,
    }
    date_str = f"\n🗓 Дата: {travel_date}" if travel_date else ""
    send_photo(
        chat_id, PLANE_PHOTO,
        f"✈️ Заявка на бронирование\n{tour_title}\n"
        f"{num_people} чел. × ${price:,} = {total_s}{date_str}".replace(",", " ")
    )
    time.sleep(0.5)
    send_message(chat_id,
                 "Для подтверждения напишите «Да» ✅\nДля отмены — «Отмена» ❌")


def notify_boss_booking(chat_id: str, sender_phone: str) -> None:
    """Переводит заявку на ожидание подтверждения боссом."""
    sd          = state.client_states.pop(chat_id, {})
    tour        = sd.get("tour",   "тур")
    price       = sd.get("price",  0)
    people      = sd.get("people", 1)
    travel_date = sd.get("date",   "")
    total_s     = f"${price * people:,}".replace(",", " ")
    pid         = f"{sender_phone}_{int(time.time())}"

    state.pending_boss_confirms[pid] = {
        "client_jid":   chat_id,
        "tour":         tour,
        "price":        total_s,
        "sender_phone": sender_phone,
        "people":       people,
        "date":         travel_date,
    }
    state.client_states[chat_id] = {"state": STATE_CONFIRM}

    date_str = f"\n🗓 Дата: {travel_date}" if travel_date else ""
    send_message(
        BOSS_JID,
        f"🌍 НОВАЯ ЗАЯВКА\nКлиент: +{sender_phone}\nТур: {tour}\n"
        f"Человек: {people}\nСумма: {total_s}{date_str}\nID: {pid}\n\n"
        "да — подтвердить | нет — отклонить"
    )
    send_message(chat_id,
                 "Заявка отправлена менеджеру! Подтверждение в течение 5–15 мин. Спасибо! 🙏")


def process_booking_photos_and_confirm(
    chat_id: str, tour_title: str, price: int,
    people: int, travel_date: str, tour_data: dict | None
) -> None:
    """Отправляет фото тура и карточку бронирования."""
    if tour_data:
        photos = get_tour_photos(tour_data.get("title", tour_title), limit=2)
        if photos:
            time.sleep(0.5)
            for i, (url, cap) in enumerate(photos):
                send_photo(chat_id, url, cap)
                if i == 0 and len(photos) > 1:
                    time.sleep(0.8)
    time.sleep(1)
    send_booking_confirmation(chat_id, tour_title, price, people, travel_date)