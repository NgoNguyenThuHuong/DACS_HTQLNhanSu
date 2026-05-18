import time
from typing import Any, Optional, Dict

class LocalMemoryCache:
    """
    Hệ thống Caching nội bộ bằng RAM làm lớp Abstraction (Cache Layer),
    sẵn sàng thay thế bằng Redis Cache ở giai đoạn Production sau này.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expire_at']:
            del self._cache[key]
            return None
            
        return entry['value']

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        self._cache[key] = {
            'value': value,
            'expire_at': time.time() + ttl_seconds
        }

    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        self._cache.clear()

cache_manager = LocalMemoryCache()
