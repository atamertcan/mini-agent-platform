import logging
import time
from functools import lru_cache

import redis

from app.config import get_settings

logger = logging.getLogger(__name__)

_RETRY_AFTER_SECONDS = 30
_down_until = 0.0


def _is_down() -> bool:
    return time.monotonic() < _down_until


def _mark_down() -> None:
    global _down_until
    _down_until = time.monotonic() + _RETRY_AFTER_SECONDS


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
    if client is None or _is_down():
        return None
    try:
        return client.get(key)
    except redis.RedisError as exc:
        _mark_down()
        logger.warning("cache get failed for %s: %s (skipping Redis for %ss)", key, exc, _RETRY_AFTER_SECONDS)
        return None


def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    client = _get_client()
    if client is None or _is_down():
        return
    try:
        client.set(key, value, ex=ttl_seconds)
    except redis.RedisError as exc:
        _mark_down()
        logger.warning("cache set failed for %s: %s (skipping Redis for %ss)", key, exc, _RETRY_AFTER_SECONDS)


def cache_delete(key: str) -> None:
    client = _get_client()
    if client is None:
        return
    # deletes are never skipped while Redis is marked down: a missed invalidation leaves stale data
    try:
        client.delete(key)
    except redis.RedisError as exc:
        _mark_down()
        logger.warning("cache delete failed for %s: %s (skipping Redis for %ss)", key, exc, _RETRY_AFTER_SECONDS)
