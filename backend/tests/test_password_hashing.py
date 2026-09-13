from app.core.security import hash_password, verify_password


def test_hash_and_verify_password():
    password = "MySecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password

    assert hashed.startswith("$argon2") or hashed.startswith("$2b$")

    assert verify_password(password, hashed) is True

    assert verify_password("WrongPassword", hashed) is False


def test_same_password_produces_different_hashes():
    password = "MySecurePassword123!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2

    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
