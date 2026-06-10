"""
WorldTravel v7.0 — Lightweight RAG on TF-IDF (scikit-learn).

Принцип работы:
  1. При старте (и раз в 30 мин) вызываем build_index() — векторизуем весь каталог.
  2. На каждый запрос пользователя вызываем search() — находим TOP-K туров
     по косинусному сходству, передаём только их в контекст AI.
  3. Полный каталог (~800 токенов) больше НЕ идёт в каждый запрос.

Почему TF-IDF, а не sentence-transformers?
  — Нет зависимости от GPU / тяжёлых моделей.
  — Работает на Railway без доп. ресурсов.
  — Character n-grams (2–4) хорошо покрывают морфологию русского языка.
"""
import logging
import threading
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

log = logging.getLogger(__name__)

# Порог релевантности: если лучший score ниже — тур "не по теме"
_RELEVANCE_THRESHOLD = 0.05


class TourRAG:
    """Thread-safe TF-IDF RAG для каталога туров."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb",     # character n-grams — хорошо для рус. морфологии
            ngram_range=(2, 4),
            max_features=8000,
            sublinear_tf=True,      # log(TF) вместо TF — нивелирует частые слова
        )
        self._matrix = None         # scipy sparse matrix
        self._tours: list[dict] = []
        self._ready = False

    # ── Build ──────────────────────────────────────────────────────────────

    def build_index(self, tours: list[dict]) -> None:
        """
        Строит/перестраивает индекс из списка туров.
        Каждый тур представлен конкатенацией текстовых полей.
        Потокобезопасно — можно вызывать из фонового потока.
        """
        if not tours:
            log.warning("RAG.build_index: пустой каталог, пропускаем")
            return

        corpus = [self._tour_to_text(t) for t in tours]

        with self._lock:
            self._vectorizer.fit(corpus)
            self._matrix = self._vectorizer.transform(corpus)
            self._tours = list(tours)
            self._ready = True

        log.info(f"RAG: проиндексировано {len(tours)} туров "
                 f"({self._matrix.shape[1]} признаков)")

    @staticmethod
    def _tour_to_text(tour: dict) -> str:
        """Собирает поисковый текст одного тура."""
        parts = [
            tour.get("title",       ""),
            tour.get("destination", ""),
            tour.get("country",     ""),
            tour.get("region",      ""),
            tour.get("tour_type",   ""),
            tour.get("description", ""),
            tour.get("includes",    "") or "",
        ]
        return " ".join(filter(None, parts)).lower()

    # ── Search ─────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Семантический поиск TOP-K туров по запросу.
        Возвращает [] если индекс не построен или нет релевантных туров.
        """
        if not self._ready:
            log.warning("RAG: индекс не готов")
            return []

        with self._lock:
            q_vec = self._vectorizer.transform([query.lower()])
            scores = cosine_similarity(q_vec, self._matrix)[0]
            top_idx = np.argsort(scores)[::-1][:top_k]
            results = [
                self._tours[i]
                for i in top_idx
                if scores[i] >= _RELEVANCE_THRESHOLD
            ]

        log.debug(f"RAG search({query!r:.40}): "
                  f"top scores={[round(scores[i], 3) for i in top_idx]}")
        return results

    # ── Format ─────────────────────────────────────────────────────────────

    @staticmethod
    def format_context(tours: list[dict]) -> str:
        """
        Форматирует найденные туры в компактный контекст для промпта.
        Экономия: ~150 токенов вместо ~800 для полного каталога.
        """
        if not tours:
            return "(нет точного совпадения — предложи ближайшие альтернативы из каталога)"
        lines = []
        for t in tours:
            hot = "🔥" if t.get("is_hot") else ""
            price = t.get("price", 0)
            line = (
                f"• {t.get('title','')} {hot} — "
                f"${price:,} | {t.get('duration','')} | "
                f"{t.get('destination','')}, {t.get('country','')}".replace(",", " ")
            )
            desc = (t.get("description") or "")[:120]
            if desc:
                line += f"\n  {desc}"
            incl = (t.get("includes") or "")[:80]
            if incl:
                line += f"\n  Включено: {incl}"
            lines.append(line)
        return "\n".join(lines)

    @property
    def is_ready(self) -> bool:
        return self._ready


# ── Singleton ──────────────────────────────────────────────────────────────
tour_rag = TourRAG()