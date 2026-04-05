from sqlalchemy import text
from sqlalchemy.orm import Session


def test_db_session_fixture_yields_working_session(db_session: Session) -> None:
    """Smoke test: the db_session fixture yields a working SQLAlchemy session."""
    result = db_session.execute(text("SELECT 1 AS ok"))
    assert result.scalar() == 1


def test_db_session_fixture_can_execute_transactional_writes(db_session: Session) -> None:
    """First test: create a temporary table and insert a row within the transaction."""
    db_session.execute(
        text("CREATE TEMPORARY TABLE _isolation_test (val INT) ON COMMIT DROP")
    )
    db_session.execute(text("INSERT INTO _isolation_test (val) VALUES (42)"))
    result = db_session.execute(text("SELECT val FROM _isolation_test"))
    assert result.scalar() == 42


def test_actor_fixture_returns_string(actor: str) -> None:
    """The actor fixture yields a non-empty string."""
    assert isinstance(actor, str)
    assert len(actor) > 0
