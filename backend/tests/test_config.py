from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/veloiq")
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:5173","http://localhost:3000"]')

    settings = Settings()

    assert settings.database_url == "postgresql://user:pass@localhost:5432/veloiq"
    assert "http://localhost:5173" in settings.cors_origins


def test_settings_has_defaults(monkeypatch):
    # _env_file=None isolates this test from backend/.env which now exists post-Task 6.
    # monkeypatch.delenv isolates from any TEST_DATABASE_URL set in the OS environment
    # (e.g., when pytest is invoked with TEST_DATABASE_URL=... in the shell).
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    settings = Settings(database_url="postgresql://test/test", _env_file=None)

    assert settings.api_v1_prefix == "/api/v1"
    assert settings.test_database_url is None
