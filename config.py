"""
WorldTravel Bot v7.0 — Configuration
Все переменные среды и константы в одном месте.
"""
import os

# ── Evolution API ──────────────────────────────────────────────────────────
EVOLUTION_URL      = os.environ.get("EVOLUTION_URL", "")
EVOLUTION_API_KEY  = os.environ.get("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "")
BOT_PHONE          = os.environ.get("BOT_PHONE", "996220891639")
BOSS_NUMBER        = os.environ.get("BOSS_NUMBER", "996755212525")

# ── Groq ───────────────────────────────────────────────────────────────────
GROQ_KEY           = os.environ.get("GROQ_KEY", "")
GROQ_FAST_MODEL    = "llama-3.1-8b-instant"
GROQ_SMART_MODEL   = "llama-3.3-70b-versatile"

# ── Bot behaviour ──────────────────────────────────────────────────────────
HISTORY_LIMIT      = 20      # сколько сообщений хранить в БД на диалог
HISTORY_WINDOW     = 10      # сколько последних сообщений передавать полностью
DEBOUNCE_SECONDS   = 8
RATE_LIMIT_COUNT   = 15
RATE_LIMIT_WINDOW  = 3600    # 1 час

# ── Follow-up (Бишкек UTC+6) ──────────────────────────────────────────────
FOLLOWUP_HOUR_START = int(os.environ.get("FOLLOWUP_HOUR_START", 9))
FOLLOWUP_HOUR_END   = int(os.environ.get("FOLLOWUP_HOUR_END",  20))

# ── Identity ───────────────────────────────────────────────────────────────
BOT_NAMES = ["morpheus", "морфеус", "flest", "флест", "worldtravel", "ворлдтревел"]
BOSS_JID  = f"{BOSS_NUMBER}@s.whatsapp.net"
BOSS_JID2 = f"{BOSS_NUMBER}@c.us"

# ── Photo URLs ─────────────────────────────────────────────────────────────
WELCOME_PHOTO = os.environ.get("WELCOME_PHOTO", "https://i.ibb.co/ccS5J6Xn/world.jpg")
PLANE_PHOTO   = os.environ.get("PLANE_PHOTO",   "https://i.ibb.co/CsnV0prL/plane.jpg")
NATURE_PHOTO  = os.environ.get("NATURE_PHOTO",  "https://i.ibb.co/93VGcwMq/nature.jpg")
MBANK_QR_URL  = os.environ.get("MBANK_QR_URL",
    "https://i.ibb.co/pvm2mPq0/Whats-App-Image-2026-04-28-at-19-32-58.jpg")

# ── MySQL ──────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":      os.environ.get("MYSQLHOST",     "localhost"),
    "port":      int(os.environ.get("MYSQLPORT", 3306)),
    "user":      os.environ.get("MYSQLUSER",     "root"),
    "password":  os.environ.get("MYSQLPASSWORD", ""),
    "database":  os.environ.get("MYSQLDATABASE", "shop_db"),
    "pool_name": "wt_pool",
    "pool_size": 5,
    "connect_timeout": 10,
}

# ── State machine ──────────────────────────────────────────────────────────
STATE_IDLE    = "idle"
STATE_BOOKING = "booking"
STATE_CONFIRM = "confirm"