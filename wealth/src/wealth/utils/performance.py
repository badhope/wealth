"""Performance optimization module with caching for Wealth platform."""

import time
import hashlib
import json
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
import asyncio
from collections import OrderedDict

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

class LRUCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return None
        self.cache.move_to_end(key)
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = CacheEntry(value, time.time(), ttl)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.cache)
        expired = sum(1 for e in self.cache.values() if e.is_expired())
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "max_size": self.max_size,
            "utilization": f"{(total / self.max_size) * 100:.1f}%"
        }

class TimedCache:
    def __init__(self, default_ttl: float = 60.0):
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        self.cache[key] = CacheEntry(value, time.time(), ttl or self.default_ttl)

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def cleanup_expired(self) -> int:
        expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.cache)
        expired = sum(1 for e in self.cache.values() if e.is_expired())
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "default_ttl": self.default_ttl
        }

class RequestCache:
    _instance = None
    _cache: LRUCache
    _timed_cache: TimedCache
    _request_count: int = 0
    _cache_hits: int = 0
    _cache_misses: int = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = LRUCache(max_size=500)
            cls._instance._timed_cache = TimedCache(default_ttl=30.0)
        return cls._instance

    def get_cached(self, key: str) -> Optional[Any]:
        result = self._cache.get(key)
        if result is not None:
            self._cache_hits += 1
            return result
        self._cache_misses += 1
        return None

    def set_cached(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        self._cache.set(key, value, ttl)

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "lru_cache": self._cache.get_stats(),
            "timed_cache": self._timed_cache.get_stats(),
            "request_stats": {
                "total_requests": self._request_count,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_rate": f"{hit_rate:.2f}%"
            }
        }

    def reset_stats(self) -> None:
        self._request_count = 0
        self._cache_hits = 0
        self._cache_misses = 0

def cached(ttl: float = 60.0, key_prefix: str = ""):
    def decorator(func: Callable) -> Callable:
        cache = RequestCache()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = cache.generate_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            cached_result = cache.get_cached(cache_key)
            if cached_result is not None:
                return cached_result

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            cache.set_cached(cache_key, result, ttl)
            cache._request_count += 1
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = cache.generate_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            cached_result = cache.get_cached(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set_cached(cache_key, result, ttl)
            cache._request_count += 1
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.counters: Dict[str, int] = {}

    def record_timing(self, name: str, duration: float) -> None:
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            "duration": duration,
            "timestamp": time.time()
        })
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]

    def increment_counter(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def get_stats(self, name: str) -> Dict[str, Any]:
        if name not in self.metrics or not self.metrics[name]:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "p95": 0}

        durations = [m["duration"] for m in self.metrics[name]]
        durations.sort()
        count = len(durations)

        return {
            "count": count,
            "avg": sum(durations) / count,
            "min": durations[0],
            "max": durations[-1],
            "p50": durations[int(count * 0.5)],
            "p95": durations[int(count * 0.95)],
            "p99": durations[int(count * 0.99)] if count > 100 else durations[-1]
        }

    def get_all_stats(self) -> Dict[str, Any]:
        return {
            "timings": {name: self.get_stats(name) for name in self.metrics},
            "counters": dict(self.counters)
        }

    def reset(self) -> None:
        self.metrics.clear()
        self.counters.clear()

request_cache = RequestCache()
performance_monitor = PerformanceMonitor()

def get_performance_stats() -> Dict[str, Any]:
    return {
        "cache": request_cache.get_stats(),
        "performance": performance_monitor.get_all_stats(),
        "timestamp": datetime.now().isoformat()
    }
