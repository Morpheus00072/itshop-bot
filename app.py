"""
WorldTravel WhatsApp Bot v7.0 — Main application entry point.
Flask + Evolution API webhook + APScheduler.
"""
import logging
import os
import re
import threading
import time

from flask import Flask, request, render_template

from config import (
    EVOLUTION_INSTANCE, BOSS_NUMBER,
    STATE_BOOKING, STATE_CONFIRM,
    BOT_NAMES, BOT_PHONE,
    FOLLOWUP_HOUR_START, FOLLOWUP_HOUR_END,
)
import state
from services.messaging import send_message
from services.client import process_message, check_followups, handle_rate_limit
from services.boss import handle_boss
from utils.debounce import debounce_message, is_rate_limited
from utils.helpers import jid_to_num, norm, is_boss_phone, is_bot_mentioned

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ── Flask ──────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ── Media types handled ────────────────────────────────────────────────────
_MEDIA_TYPES = {
    "imageMessage", "videoMessage", "audioMessage",
    "documentMessage", "stickerMessage", "pttMessage",
}


# ── Webhook message extractor ──────────────────────────────────────────────

def _extract_msg(message: dict, msg_type: str):
    """
    Returns (text, mentioned_jids, quoted_participant).
    Returns (None, [], '') if the message should be ignored.
    """
    mentioned: list[str] = []
    quoted_participant: str = ""
    text: str | None = None

    if msg_type == "conversation":
        text = message.get("conversation", "")

    elif msg_type == "extendedTextMessage":
        ext  = message.get("extendedTextMessage", {})
        text = ext.get("text", "")
        ctx  = ext.get("contextInfo", {})
        mentioned          = ctx.get("mentionedJid", [])
        quoted_participant = ctx.get("participant", "") or ctx.get("quotedParticipant", "")

    elif msg_type in _MEDIA_TYPES:
        for mt in _MEDIA_TYPES:
            if mt in message:
                ctx  = message[mt].get("contextInfo", {})
                mentioned          = ctx.get("mentionedJid", [])
                quoted_participant = ctx.get("participant", "") or ctx.get("quotedParticipant", "")
                text = message[mt].get("caption")
                break
        if text is None:
            return None, [], ""
    else:
        text = ""

    # Expand @mentions embedded in text
    if text:
        for ph in re.findall(r"@(\d+)", text):
            jid = f"{ph}@s.whatsapp.net"
            if jid not in mentioned:
                mentioned.append(jid)

    return text, mentioned, quoted_participant


# ── Webhook ────────────────────────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data or data.get("event") != "messages.upsert":
        return "OK", 200

    msg_data   = data.get("data", {})
    key        = msg_data.get("key", {})
    remote_jid = key.get("remoteJid", "")

    # Messages sent BY the bot → mute that chat for 30 min (manager takeover)
    if key.get("fromMe"):
        if remote_jid and not remote_jid.endswith("@g.us"):
            state.client_states[remote_jid] = {
                "state": "muted",
                "until": time.time() + 1800,
            }
            log.info(f"[MANAGER TAKEOVER] muted {remote_jid} for 30m")
        return "OK", 200

    is_group   = remote_jid.endswith("@g.us")
    chat_id    = remote_jid

    if is_group:
        sender_jid = (
            key.get("participant") or msg_data.get("participant") or
            key.get("participantAlt") or msg_data.get("participantAlt") or ""
        )
        if not sender_jid:
            log.warning(f"[GROUP] no sender for {remote_jid}")
            return "OK", 200
    else:
        sender_jid = remote_jid

    sender_phone = jid_to_num(sender_jid) if sender_jid else ""
    message      = msg_data.get("message", {})
    msg_type     = msg_data.get("messageType", "")

    log.info(f"IN from={sender_phone} chat={remote_jid[:35]} type={msg_type}")

    user_text, mentioned, quoted_participant = _extract_msg(message, msg_type)

    if user_text is None:
        # Non-text media without caption
        if not is_group:
            send_message(chat_id, "Привет! Я понимаю только текст — напишите вопрос! ✈️😊")
        return "OK", 200

    user_text = user_text.strip()
    if not user_text:
        return "OK", 200

    # Group: respond only when bot is mentioned
    if is_group:
        if not is_bot_mentioned(mentioned, user_text, quoted_participant):
            return "OK", 200
        # Strip @mention and bot name prefix
        user_text = re.sub(r"@\S+\s*", "", user_text).strip()
        for name in BOT_NAMES:
            user_text = re.sub(rf"^{re.escape(name)},?\s*", "", user_text, flags=re.I).strip()
        if not user_text:
            return "OK", 200

    # Boss → dedicated handler (bypass rate-limit & debounce)
    if is_boss_phone(sender_phone):
        threading.Thread(
            target=handle_boss, args=(chat_id, user_text), daemon=True
        ).start()
        return "OK", 200

    # Paused bot → silently ignore
    from database.tours import is_bot_paused
    if is_bot_paused():
        return "OK", 200

    if not sender_phone:
        return "OK", 200

    # Rate-limit check
    if is_rate_limited(chat_id):
        cur_state = state.client_states.get(chat_id, {}).get("state", "")
        if cur_state != "rate_limited":
            threading.Thread(
                target=handle_rate_limit, args=(chat_id, sender_phone), daemon=True
            ).start()
        return "OK", 200

    meta = {
        "sender_jid":   sender_jid,
        "sender_phone": sender_phone,
        "is_group":     is_group,
    }

    # BOOKING / CONFIRM states: bypass debounce, handle immediately
    cur_state = state.client_states.get(chat_id, {}).get("state", "")
    if cur_state in (STATE_BOOKING, STATE_CONFIRM):
        threading.Thread(
            target=process_message, args=(chat_id, meta, user_text), daemon=True
        ).start()
        return "OK", 200

    # Default: debounce
    debounce_message(chat_id, user_text, meta, callback=process_message)
    return "OK", 200


# ── Status / index routes ──────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    try:
        return render_template("index.html")
    except Exception:
        return "WorldTravel Bot v7.0 ✈️", 200


@app.route("/status", methods=["GET"])
def status():
    from database.tours import is_bot_paused
    return {
        "status":           "WorldTravel bot v7.0 ✈️",
        "instance":         EVOLUTION_INSTANCE,
        "paused":           is_bot_paused(),
        "active_sessions":  len(state.client_states),
        "pending_confirms": len(state.pending_boss_confirms),
        "rag_ready":        _rag_ready(),
    }, 200


def _rag_ready() -> bool:
    try:
        from ai_core.rag import tour_rag
        return tour_rag.is_ready
    except Exception:
        return False


# ── Startup tasks ──────────────────────────────────────────────────────────

def _init_rag():
    """Build RAG index at startup."""
    try:
        from ai_core.rag import tour_rag
        from database.tours import fetch_all_tours_for_rag
        tours = fetch_all_tours_for_rag()
        if tours:
            tour_rag.build_index(tours)
            log.info(f"RAG: индекс построен ({len(tours)} туров)")
        else:
            log.warning("RAG: каталог пуст — индекс не построен")
    except Exception as e:
        log.error(f"RAG init error: {e}")


def _rebuild_rag():
    """Periodic RAG refresh (every 30 min)."""
    _init_rag()


# ── Scheduler ──────────────────────────────────────────────────────────────

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_followups, "interval", minutes=15, id="followups")
scheduler.add_job(_rebuild_rag, "interval", minutes=30, id="rag_rebuild")


# ── Entry point ────────────────────────────────────────────────────────────

# Build RAG + start scheduler on import (works for gunicorn too)
threading.Thread(target=_init_rag, daemon=True).start()
scheduler.start()
log.info(f"WorldTravel v7.0 started | instance={EVOLUTION_INSTANCE} | boss={BOSS_NUMBER}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
