from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/veloiq")
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:5173","http://localhost:3000"]')

    settings = Settings()

    assert settings.database_url == "postgresql://user:pass@localhost:5432/veloiq"
    assert "http://localhost:5173" in settings.cors_origins


def test_settings_has_defaults():
    # _env_file=None isolates this test from backend/.env which now exists post-Task 6
    # and would otherwise populate test_database_url, breaking the is-None assertion.
    settings = Settings(database_url="postgresql://test/test", _env_file=None)

    assert settings.api_v1_prefix == "/api/v1"
    assert settings.test_database_url is None
