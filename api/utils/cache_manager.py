import asyncio
import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: int
    hit_count: int = 0
    last_accessed: float = None
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl
    
    def access(self):
        self.hit_count += 1
        self.last_accessed = time.time()

class MemoryCache:
    """High-performance in-memory cache with TTL and LRU eviction"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
            'deletes': 0
        }
        self._lock = asyncio.Lock()
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments"""
        # Create a deterministic key from function name and arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    entry.access()
                    self._stats['hits'] += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]
            
            self._stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        async with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self._max_size:
                await self._evict_lru()
            
            ttl = ttl or self._default_ttl
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                last_accessed=time.time()
            )
            
            self._cache[key] = entry
            self._stats['sets'] += 1
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entries"""
        if not self._cache:
            return
        
        # Remove expired entries first
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1
        
        # If still over capacity, remove LRU entries
        while len(self._cache) >= self._max_size:
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed or 0
            )
            del self._cache[lru_key]
            self._stats['evictions'] += 1
    
    async def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Get value from cache or compute and store it"""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Compute value
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # Store in cache
        await self.set(key, result, ttl)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hit_rate': round(hit_rate, 2),
            'stats': self._stats.copy(),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> Dict[str, int]:
        """Estimate memory usage of cache"""
        try:
            import sys
            total_size = sum(
                sys.getsizeof(key) + sys.getsizeof(entry.value) 
                for key, entry in self._cache.items()
            )
            return {
                'estimated_bytes': total_size,
                'estimated_mb': round(total_size / (1024 * 1024), 2)
            }
        except:
            return {'estimated_bytes': 0, 'estimated_mb': 0}

# Global cache instances
default_cache = MemoryCache(default_ttl=300, max_size=1000)  # 5 minutes, 1000 items
long_term_cache = MemoryCache(default_ttl=3600, max_size=500)  # 1 hour, 500 items
short_term_cache = MemoryCache(default_ttl=60, max_size=2000)  # 1 minute, 2000 items

def cached(ttl: int = 300, cache_instance: Optional[MemoryCache] = None, key_prefix: str = ""):
    """Decorator to add caching to functions"""
    cache = cache_instance or default_cache
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}{func.__module__}.{func.__name__}"
            key = cache._generate_key(func_name, args, kwargs)
            
            # Try to get from cache
            result = await cache.get_or_set(key, func, ttl, *args, **kwargs)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle the async cache operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                func_name = f"{key_prefix}{func.__module__}.{func.__name__}"
                key = cache._generate_key(func_name, args, kwargs)
                result = loop.run_until_complete(cache.get_or_set(key, func, ttl, *args, **kwargs))
                return result
            finally:
                loop.close()
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            wrapper = async_wrapper
        else:
            wrapper = sync_wrapper
        
        # Attach cache instance to wrapper for access to stats
        wrapper.cache = cache
        return wrapper
    
    return decorator

# Specialized decorators for different cache types
def cache_short_term(ttl: int = 60):
    """Cache for short-term data (1 minute default)"""
    return cached(ttl=ttl, cache_instance=short_term_cache, key_prefix="short_")

def cache_long_term(ttl: int = 3600):
    """Cache for long-term data (1 hour default)"""
    return cached(ttl=ttl, cache_instance=long_term_cache, key_prefix="long_")

def cache_market_data(ttl: int = 300):
    """Cache specifically for market data (5 minutes default)"""
    return cached(ttl=ttl, cache_instance=default_cache, key_prefix="market_")

async def get_all_cache_stats() -> Dict[str, Any]:
    """Get statistics for all cache instances"""
    return {
        'default_cache': default_cache.get_stats(),
        'long_term_cache': long_term_cache.get_stats(),
        'short_term_cache': short_term_cache.get_stats(),
        'total_memory_estimate': sum([
            cache.get_stats()['memory_usage']['estimated_bytes']
            for cache in [default_cache, long_term_cache, short_term_cache]
        ])
    }

async def clear_all_caches() -> Dict[str, str]:
    """Clear all cache instances"""
    await default_cache.clear()
    await long_term_cache.clear()
    await short_term_cache.clear()
    
    return {
        'status': 'success',
        'message': 'All caches cleared',
        'timestamp': datetime.now().isoformat()
    }

# Cache warming utilities
async def warm_cache_with_common_queries():
    """Pre-populate cache with common queries"""
    try:
        # This would be implemented based on your specific use cases
        # Example: Pre-load popular stock data, common portfolio analyses, etc.
        logging.info("Cache warming started")
        
        # Add your cache warming logic here
        # await cache_popular_stocks()
        # await cache_market_indices()
        
        logging.info("Cache warming completed")
        return {"status": "success", "message": "Cache warmed successfully"}
    
    except Exception as e:
        logging.error(f"Cache warming failed: {e}")
        return {"status": "error", "message": str(e)}
