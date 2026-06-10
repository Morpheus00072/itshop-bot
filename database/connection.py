"""
WorldTravel v7.0 — Database connection pool.
Один пул на весь процесс, thread-safe.
"""
import logging
import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

log = logging.getLogger(__name__)
_pool: pooling.MySQLConnectionPool | None = None


def _make_pool() -> pooling.MySQLConnectionPool:
    """Create the connection pool once."""
    pool_cfg = dict(DB_CONFIG)
    return pooling.MySQLConnectionPool(**pool_cfg)


def get_db() -> mysql.connector.MySQLConnection:
    """
    Get a connection from the pool.
    Falls back to a direct connection if the pool is exhausted or fails.
    Always call .close() on the returned connection (returns it to pool).
    """
    global _pool
    if _pool is None:
        _pool = _make_pool()
    try:
        return _pool.get_connection()
    except pooling.PoolError:
        log.warning("DB pool exhausted, opening direct connection")
        direct_cfg = {k: v for k, v in DB_CONFIG.items()
                      if k not in ("pool_name", "pool_size")}
        return mysql.connector.connect(**direct_cfg)
    except Exception as e:
        log.error(f"DB pool error: {e}")
        direct_cfg = {k: v for k, v in DB_CONFIG.items()
                      if k not in ("pool_name", "pool_size")}
        return mysql.connector.connect(**direct_cfg)