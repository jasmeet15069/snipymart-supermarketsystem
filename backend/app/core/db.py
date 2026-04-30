from collections.abc import Generator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _normalize_mysql_url(raw_url: str) -> tuple[str | URL, dict]:
    if raw_url.startswith("mysql://"):
        raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)

    connect_args: dict = {}
    if raw_url.startswith("mysql+pymysql://"):
        parts = urlsplit(raw_url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        ssl_mode = query.pop("ssl-mode", None) or query.pop("ssl_mode", None)
        if ssl_mode:
            connect_args["ssl"] = {"ssl": {"ssl-mode": ssl_mode}} if False else {"ssl_disabled": False}
            connect_args["ssl"] = {}
        raw_url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return raw_url, connect_args


database_url, engine_connect_args = _normalize_mysql_url(settings.database_url)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=280,
    pool_size=10,
    max_overflow=20,
    connect_args=engine_connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
