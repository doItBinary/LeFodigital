from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from app.core.security import create_token, decode_token, hash_password, verify_password


def test_password_hash_is_not_plaintext() -> None:
    encoded = hash_password("a-secure-password")
    assert encoded != "a-secure-password"
    assert encoded.startswith("$argon2id$")
    assert verify_password("a-secure-password", encoded)
    assert not verify_password("wrong-password", encoded)


def test_access_token_contains_required_claims(settings) -> None:
    subject = uuid4()
    token, token_id, expires_at = create_token(subject, "access", settings)
    payload = decode_token(token, "access", settings)
    assert payload["sub"] == str(subject)
    assert payload["jti"] == str(token_id)
    assert payload["iss"] == settings.jwt_issuer
    assert payload["aud"] == settings.jwt_audience
    assert expires_at > datetime.now(UTC)


def test_token_type_and_expiration_are_validated(settings) -> None:
    token, _, _ = create_token(uuid4(), "refresh", settings)
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, "access", settings)
    expired = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "access",
            "jti": str(uuid4()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired, "access", settings)
