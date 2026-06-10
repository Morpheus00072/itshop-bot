"""
WorldTravel v7.0 — Tour database queries.
"""
import logging
from collections import defaultdict
from database.connection import get_db

log = logging.getLogger(__name__)

# Стоп-слова для fuzzy фото-поиска
_PHOTO_STOP_WORDS = {
    "тур", "путешествие", "поездка", "отдых", "отпуск", "каникулы",
    "пляж", "море", "горы", "природа", "экскурсия", "город",
    "страна", "можно", "хочу", "покажи", "фото", "фотку",
}


# ── Catalog / RAG helpers ──────────────────────────────────────────────────

def fetch_all_tours_for_rag() -> list[dict]:
    """
    Возвращает все доступные туры в виде списка dict для RAG-индекса.
    Вызывается при старте приложения и раз в 30 мин.
    """
    try:
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT id, title, destination, country, region, duration, "
            "       price, old_price, description, includes, hotel_stars, "
            "       tour_type, is_hot, available, photo_url "
            "FROM tours WHERE available = TRUE ORDER BY region, price"
        )
        rows = cur.fetchall()
        db.close()
        return rows
    except Exception as e:
        log.error(f"fetch_all_tours_for_rag: {e}")
        return []


def get_tours_catalog() -> str:
    """
    Компактный каталог туров (для boss-команд и fallback промпта).
    """
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT title, destination, country, region, duration, price, is_hot "
            "FROM tours WHERE available = TRUE ORDER BY region, price"
        )
        rows = cur.fetchall()
        db.close()
        if not rows:
            return "Каталог туров пуст."
        regions: dict = defaultdict(list)
        for title, dest, country, region, dur, price, hot in rows:
            mark = "🔥" if hot else ""
            line = f"  • {title} {mark} ({dest}, {country}) — ${price:,} | {dur}".replace(",", " ")
            regions[region].append(line)
        out = []
        for reg, items in regions.items():
            out.append(f"\n🌐 [{reg}]")
            out.extend(items)
        return "\n".join(out)
    except Exception as e:
        log.error(f"get_tours_catalog: {e}")
        return "Каталог временно недоступен."


def get_tour_by_name(name_q: str) -> dict | None:
    """Найти один тур по названию / направлению."""
    try:
        db = get_db(); cur = db.cursor(dictionary=True)
        q = f"%{name_q.lower()}%"
        cur.execute(
            "SELECT id, title, destination, price, photo_url, duration, description "
            "FROM tours WHERE available=TRUE "
            "AND (LOWER(title) LIKE %s OR LOWER(destination) LIKE %s OR LOWER(country) LIKE %s) "
            "LIMIT 1",
            (q, q, q)
        )
        row = cur.fetchone()
        db.close()
        return row
    except Exception as e:
        log.error(f"get_tour_by_name: {e}")
        return None


def get_hot_tours(n: int = 3) -> str:
    """Возвращает N горящих туров в виде текстовой строки."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT title, destination, price, duration FROM tours "
            "WHERE available=TRUE AND is_hot=TRUE ORDER BY RAND() LIMIT %s", (n,)
        )
        rows = cur.fetchall()
        db.close()
        return "\n".join(
            f"🔥 {t} — ${p:,} ({d})".replace(",", " ") for t, _, p, d in rows
        )
    except Exception:
        return ""


def get_sample_tours(n: int = 3) -> str:
    """Несколько случайных туров (для приветствия)."""
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "SELECT title, price, duration FROM tours "
            "WHERE available=TRUE ORDER BY RAND() LIMIT %s", (n,)
        )
        rows = cur.fetchall()
        db.close()
        return "\n".join(
            f"✈️ {t} — ${p:,} ({d})".replace(",", " ") for t, p, d in rows
        )
    except Exception:
        return ""


def is_bot_paused() -> bool:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("SELECT value FROM bot_settings WHERE key_name='paused'")
        row = cur.fetchone()
        db.close()
        return bool(row and row[0] == "1")
    except Exception:
        return False


def set_bot_paused(val: bool) -> None:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO bot_settings (key_name, value) VALUES ('paused', %s) "
            "ON DUPLICATE KEY UPDATE value=%s",
            ("1" if val else "0", "1" if val else "0")
        )
        db.commit()
        db.close()
    except Exception as e:
        log.error(f"set_bot_paused: {e}")


# ── Photos ─────────────────────────────────────────────────────────────────

def get_tour_photos(tour_name: str, limit: int = 2) -> list[tuple[str, str]]:
    """
    Возвращает список (url, caption) для данного направления.
    Ищет сначала в tour_photos, потом в tours.photo_url.
    Поддерживает нечёткий поиск по отдельным словам.
    """
    results: list[tuple[str, str]] = []
    try:
        db = get_db(); cur = db.cursor()
        q = f"%{tour_name.lower()}%"

        # 1) tour_photos JOIN tours
        cur.execute(
            "SELECT tp.photo_url, t.title, t.price, t.duration "
            "FROM tour_photos tp JOIN tours t ON tp.tour_id = t.id "
            "WHERE t.available=TRUE "
            "  AND (LOWER(t.title) LIKE %s OR LOWER(t.destination) LIKE %s OR LOWER(t.country) LIKE %s) "
            "GROUP BY tp.photo_url, t.title, t.price, t.duration "
            "ORDER BY MIN(tp.sort_order) ASC LIMIT %s",
            (q, q, q, limit)
        )
        for row in cur.fetchall():
            cap = f"{row[1]} — ${row[2]:,} ({row[3]})".replace(",", " ")
            results.append((row[0], cap))

        # 2) Fallback: tours.photo_url
        if not results:
            cur.execute(
                "SELECT title, photo_url, price, duration FROM tours "
                "WHERE photo_url IS NOT NULL AND available=TRUE "
                "  AND (LOWER(title) LIKE %s OR LOWER(destination) LIKE %s OR LOWER(country) LIKE %s) "
                "LIMIT %s",
                (q, q, q, limit)
            )
            for row in cur.fetchall():
                cap = f"{row[0]} — ${row[2]:,} ({row[3]})".replace(",", " ")
                results.append((row[1], cap))

        # 3) Deep fallback: по отдельным словам
        if not results:
            words = [
                w for w in tour_name.lower().split()
                if len(w) > 3 and w not in _PHOTO_STOP_WORDS
            ][:3]
            for word in words:
                wq = f"%{word}%"
                cur.execute(
                    "SELECT title, photo_url, price, duration FROM tours "
                    "WHERE photo_url IS NOT NULL AND available=TRUE "
                    "  AND (LOWER(title) LIKE %s OR LOWER(destination) LIKE %s) LIMIT 1",
                    (wq, wq)
                )
                row = cur.fetchone()
                if row:
                    cap = f"{row[0]} — ${row[2]:,} ({row[3]})".replace(",", " ")
                    results.append((row[1], cap))
                    break

        db.close()
    except Exception as e:
        log.error(f"get_tour_photos({tour_name!r}): {e}")
    return results


# ── Boss admin helpers ─────────────────────────────────────────────────────

def db_add_tour(title, dest, country, region, duration, price,
                description, tour_type, photo_url=None) -> str:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "INSERT INTO tours (title, destination, country, region, duration, "
            "                   price, description, tour_type, photo_url) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (title, dest, country, region, duration, price,
             description, tour_type, photo_url)
        )
        db.commit(); db.close()
        return f"✅ Тур «{title}» добавлен (id={cur.lastrowid})"
    except Exception as e:
        return f"❌ Ошибка добавления: {e}"


def db_remove_tour(name_q: str) -> str:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "UPDATE tours SET available=FALSE "
            "WHERE LOWER(title) LIKE %s OR LOWER(destination) LIKE %s",
            (f"%{name_q.lower()}%", f"%{name_q.lower()}%")
        )
        n = cur.rowcount; db.commit(); db.close()
        return f"✅ Скрыт ({n} тур)" if n else "❌ Не найдено"
    except Exception as e:
        return f"❌ Ошибка: {e}"


def db_update_tour_price(name_q: str, new_price: int) -> str:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute(
            "UPDATE tours SET price=%s "
            "WHERE LOWER(title) LIKE %s OR LOWER(destination) LIKE %s",
            (new_price, f"%{name_q.lower()}%", f"%{name_q.lower()}%")
        )
        n = cur.rowcount; db.commit(); db.close()
        return f"✅ Цена обновлена ({n}): ${new_price:,}".replace(",", " ") if n else "❌ Не найдено"
    except Exception as e:
        return f"❌ Ошибка: {e}"


def get_boss_stats() -> str:
    try:
        db = get_db(); cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM chat_sessions WHERE greeted=TRUE")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM chat_sessions WHERE last_seen >= NOW() - INTERVAL 24 HOUR")
        today = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tours WHERE available=TRUE")
        tours = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tours WHERE is_hot=TRUE AND available=TRUE")
        hot = cur.fetchone()[0]
        db.close()
        status = "⏸️ Пауза" if is_bot_paused() else "▶️ Работает"
        return (
            f"📊 Статистика WorldTravel\n"
            f"👥 Всего клиентов: {total}\n"
            f"🟢 Активны за 24ч: {today}\n"
            f"✈️ Туров в каталоге: {tours}\n"
            f"🔥 Горящих: {hot}\n"
            f"🤖 Бот: {status}"
        )
    except Exception as e:
        return f"Ошибка: {e}"