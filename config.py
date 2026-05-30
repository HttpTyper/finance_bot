import os


def _normalize_database_url(url: str) -> str:
    """Railway Postgres uses postgresql:// — SQLAlchemy async needs postgresql+asyncpg://."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///finance_sim.db")
)
ADMIN_IDS = (
    list(map(int, filter(None, os.getenv("ADMIN_IDS", "").split(","))))
    if os.getenv("ADMIN_IDS")
    else []
)
