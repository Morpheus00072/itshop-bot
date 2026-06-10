"""
WorldTravel Bot v7.0 — Global in-memory state.
Хранится в RAM одного процесса gunicorn (один worker = OK для Railway).
"""
from typing import Dict, Set

# chat_id → {"state": str, ...extra booking/mute data...}
client_states: Dict[str, dict] = {}

# booking_id → {client_jid, tour, price, sender_phone, people, date}
pending_boss_confirms: Dict[str, dict] = {}

# chat_ids которым уже отправили follow-up (сбрасывается раз в сутки)
followup_sent: Set[str] = set()

# chat_id → summary string (скользящее окно истории)
history_summaries: Dict[str, str] = {}