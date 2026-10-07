import logging
from functools import lru_cache

import redis

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def _get_client() -> redis.Redis | None:
    url = get_settings().redis_url
    if not url:
        return None
    return redis.Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )


def cache_get(key: str) -> str | None:
    client = _get_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except redis.RedisError as exc:
        logger.warning("cache get failed for %s: %s", key, exc)
        return None


def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.set(key, value, ex=ttl_seconds)
    except redis.RedisError as exc:
        logger.warning("cache set failed for %s: %s", key, exc)


def cache_delete(key: str) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.delete(key)
    except redis.RedisError as exc:
        logger.warning("cache delete failed for %s: %s", key, exc)
