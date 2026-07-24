from app.core.config import Settings


def test_cors_origins_accepts_comma_separated_environment_value(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:4200, https://lefodigital.example.com",
    )

    settings = Settings(_env_file=None)

    assert settings.cors_origins == [
        "http://localhost:4200",
        "https://lefodigital.example.com",
    ]


def test_cors_origins_accepts_empty_environment_value(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "")

    settings = Settings(_env_file=None)

    assert settings.cors_origins == []
