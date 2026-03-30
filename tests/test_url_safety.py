from src.utils.url_safety import is_safe_public_url


def test_public_https_url_is_allowed():
    assert is_safe_public_url("https://example.com/news") is True


def test_localhost_is_blocked():
    assert is_safe_public_url("http://localhost:8000") is False


def test_private_ip_is_blocked():
    assert is_safe_public_url("http://192.168.1.10/internal") is False
