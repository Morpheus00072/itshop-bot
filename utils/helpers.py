"""
WorldTravel v7.0 — Common helpers.
"""
import re
from config import BOSS_NUMBER, BOT_PHONE, BOT_NAMES


def norm(phone: str) -> str:
    """Убирает все нецифровые символы из номера/JID."""
    return re.sub(r"\D", "", phone)


def is_boss_phone(phone: str) -> bool:
    return bool(phone) and norm(phone) == norm(BOSS_NUMBER) and bool(BOSS_NUMBER)


def jid_to_num(jid: str) -> str:
    return norm(jid.split("@")[0])


def num_to_jid(phone: str) -> str:
    return f"{norm(phone)}@s.whatsapp.net"


def to_api_number(jid_or_phone: str) -> str:
    return norm(jid_or_phone.split("@")[0])


def is_bot_mentioned(mentioned: list, text: str = "", quoted_participant: str = "") -> bool:
    bot_num = norm(BOT_PHONE) if BOT_PHONE else "996220891639"
    for jid in mentioned:
        if bot_num in norm(jid):
            return True
    if f"@{bot_num}" in text or bot_num in text:
        return True
    if quoted_participant and bot_num in norm(quoted_participant):
        return True
    for name in BOT_NAMES:
        if name in text.lower():
            return True
    return False