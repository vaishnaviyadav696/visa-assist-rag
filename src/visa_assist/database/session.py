"""Database engine and transactional session management."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker


def create_database_engine(
    database_url: str | URL,
    *,
    echo: bool = False,
    **engine_options: Any,
) -> Engine:
    """Create an engine with adapter-specific setup isolated at this boundary."""
    url = make_url(database_url)
    options = dict(engine_options)

    if url.get_backend_name() == "sqlite":
        connect_args = dict(options.pop("connect_args", {}))
        connect_args.setdefault("check_same_thread", False)
        options["connect_args"] = connect_args

    engine = create_engine(url, echo=echo, **options)

    if url.get_backend_name() == "sqlite":
        _enable_sqlite_foreign_keys(engine)

    return engine


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """Enable SQLite foreign keys without leaking SQLite logic to repositories."""

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a reusable SQLAlchemy 2 session factory."""
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Commit a unit of work or roll it back when an exception occurs."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
