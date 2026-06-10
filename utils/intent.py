"""
WorldTravel v7.0 — Intent detection helpers.
"""
import re


def is_photo_req(text: str) -> bool:
    return bool(re.search(
        r"\b(фото|фотк|картинк|покажи|скинь|пикч|изображен)\b",
        text, re.I | re.U
    ))


def is_cancel(text: str) -> bool:
    return bool(re.search(
        r"\b(отмена|отменить|не хочу|передумал|передумала|cancel)\b",
        text, re.I | re.U
    ))


def is_book_related(text: str) -> bool:
    if re.search(r"\b(не хочу|не буду|не надо|не нужно|не требуется)\b", text, re.I):
        return False
    return bool(re.search(
        r"\b(бронир|забронир|хочу поехать|хочу полететь|хочу в|хочу на|"
        r"записаться|оформить|заказать|бронь|поехали|летим|берём тур|"
        r"возьму тур|хочу тур|запишите|запишемся|давайте|едем|оплатить|"
        r"оплата|посчитайте|рассчитайте|берём|берем|купить тур|приобрести|"
        r"интересует бронирование|хотим тур|планируем|отправиться|"
        r"готов ехать|готова ехать)\b",
        text, re.I
    ))


def is_hot_request(text: str) -> bool:
    return bool(re.search(
        r"\b(горящ|горяч|акци|скидк|распродаж|дёшев|дешев|бюджет|"
        r"hot|дешевый|недорог|сэкономить)\b",
        text, re.I | re.U
    ))


def is_payment_request(text: str) -> bool:
    return bool(re.search(
        r"\b(реквизит|оплат|мбанк|mbank|перевод|qr|куда перевест|"
        r"скинь номер|номер счёт|оплачу|заплачу|как оплатить|как платить)\b",
        text, re.I | re.U
    ))