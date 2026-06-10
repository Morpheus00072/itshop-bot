"""
WorldTravel v7.0 — Booking persistence.
"""
import logging
import re
import datetime
from database.connection import get_db

log = logging.getLogger(__name__)

_MONTH_MAP = {
    "январ": 1, "феврал": 2, "март": 3, "апрел": 4,
    "ма":    5, "июн":    6, "июл":  7, "август": 8,
    "сентябр": 9, "октябр": 10, "ноябр": 11, "декабр": 12,
}


def _parse_travel_date(travel_date: str) -> datetime.date | None:
    """Пытается разобрать дату из русского текста."""
    m = re.search(
        r'(\d{1,2})[а-яё\s]*(января|февраля|марта|апреля|мая|июня|'
        r'июля|августа|сентября|октября|ноября|декабря)',
        travel_date, re.I
    )
    if not m:
        return None
    day = int(m.group(1))
    mon_str = m.group(2).lower()[:6]
    month = next((v for k, v in _MONTH_MAP.items() if mon_str.startswith(k[:3])), None)
    if not month:
        return None
    year = datetime.date.today().year
    try:
        dt = datetime.date(year, month, day)
        if dt < datetime.date.today():
            dt = datetime.date(year + 1, month, day)
        return dt
    except ValueError:
        return None


def save_booking(chat_id: str, sender_phone: str, tour_id: int,
                 tour_title: str, price: int,
                 num_people: int = 1, travel_date: str = "") -> int | None:
    """Сохраняет заявку в tour_bookings и при наличии даты — в tour_availability."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO tour_bookings "
            "  (chat_id, sender_phone, tour_id, tour_title, price, num_people, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (chat_id, sender_phone, tour_id, tour_title, price, num_people,
             f"Дата: {travel_date}" if travel_date else None)
        )
        db.commit()
        bid = cur.lastrowid

        # Попытка зафиксировать занятость в tour_availability
        if travel_date:
            dt = _parse_travel_date(travel_date)
            if dt:
                try:
                    cur.execute(
                        "INSERT INTO tour_availability "
                        "  (tour_id, travel_date, booked_seats, booking_id) "
                        "VALUES (%s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE booked_seats = booked_seats + %s",
                        (tour_id, dt.isoformat(), num_people, bid, num_people)
                    )
                    db.commit()
                except Exception as e2:
                    log.error(f"tour_availability insert: {e2}")

        db.close()
        return bid
    except Exception as e:
        log.error(f"save_booking: {e}")
        return None