from app.core.security import generate_api_key, hash_api_key


def test_generate_api_key_structure():
    raw_key, key_hash, key_prefix = generate_api_key(is_live=True)
    assert raw_key.startswith("sk_live_") or raw_key.startswith("ark_live_")
    assert len(key_prefix) == 13
    assert key_prefix == raw_key[:13]
    assert key_hash != raw_key


def test_generate_test_key_prefix():
    raw_key, _, _ = generate_api_key(is_live=False)
    assert raw_key.startswith("sk_test_") or raw_key.startswith("ark_test_")


def test_api_keys_are_unique():
    keys = {generate_api_key()[0] for _ in range(50)}
    assert len(keys) == 50


def test_hash_api_key_is_deterministic():
    raw_key = "sk_live_test123"
    assert hash_api_key(raw_key) == hash_api_key(raw_key)


def test_hash_api_key_differs_for_different_keys():
    assert hash_api_key("sk_live_aaa") != hash_api_key("sk_live_bbb")


def test_hash_returns_sha256_length():
    h = hash_api_key("any_key")
    assert len(h) == 64
