import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test",
)


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Session-scoped engine connected to the test database.

    Creates all tables via Base.metadata.create_all at session start.
    Drops all tables at session end.
    """
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)  # Clean slate in case prior run left tables
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_connection(test_engine: Engine) -> Generator[Connection, None, None]:
    """Per-test connection wrapped in a transaction that rolls back."""
    connection = test_engine.connect()
    transaction = connection.begin()
    yield connection
    try:
        # IntegrityError in a test auto-deassociates the transaction; skip
        # rollback in that case to avoid a SAWarning (connection.close() still runs).
        if transaction.is_active:
            transaction.rollback()
    finally:
        connection.close()


@pytest.fixture()
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    """Per-test SQLAlchemy session bound to the transactional connection.

    All writes are rolled back when the test completes — complete isolation.
    """
    session_factory = sessionmaker(bind=db_connection, autocommit=False, autoflush=False)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def actor() -> str:
    """Default test actor identity for audited mutations."""
    return "test-actor"


# --- HTTP client fixture ---------------------------------------------------
# (added for Part 7: wires FastAPI TestClient to the transactional db_session
# fixture so end-to-end tests share the same rollback-isolated transaction.)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the get_db dependency overridden.

    All DB work performed through the client shares the same transactional
    db_session, so writes roll back after the test finishes — complete
    isolation between tests without any cleanup code.
    """
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
