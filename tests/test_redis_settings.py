from src.core.config import RedisSettings


def test_redis_url_without_password():
    settings = RedisSettings(host="redis", port=6380, db=2)
    assert settings.url == "redis://redis:6380/2"


def test_redis_url_with_password():
    settings = RedisSettings(host="redis", port=6379, db=0, password="secret")
    assert settings.url == "redis://:secret@redis:6379/0"
