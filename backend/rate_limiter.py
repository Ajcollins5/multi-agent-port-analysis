"""
Advanced Rate Limiter for News Intelligence Pipeline
Implements token bucket and sliding window algorithms for API protection
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import json

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    burst_capacity: int
    cooldown_seconds: int = 60

class TokenBucket:
    """Token bucket rate limiter for burst handling"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket, return True if successful"""
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on time elapsed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait before tokens are available"""
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

class SlidingWindowRateLimiter:
    """Sliding window rate limiter for precise rate control"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size  # seconds
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> Tuple[bool, float]:
        """Check if request is allowed, return (allowed, wait_time)"""
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True, 0.0
            
            # Calculate wait time until oldest request expires
            oldest_request = self.requests[0]
            wait_time = (oldest_request + self.window_size) - now
            return False, max(0.0, wait_time)

class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on API responses"""
    
    def __init__(self, base_config: RateLimitConfig):
        self.base_config = base_config
        self.current_rate = base_config.requests_per_minute
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 300  # 5 minutes
        
        # Token bucket for burst handling
        self.token_bucket = TokenBucket(
            capacity=base_config.burst_capacity,
            refill_rate=base_config.requests_per_minute / 60.0
        )
        
        # Sliding window for precise control
        self.sliding_window = SlidingWindowRateLimiter(
            window_size=60,  # 1 minute
            max_requests=self.current_rate
        )
        
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire permission to make request"""
        # Check token bucket first (for burst handling)
        if not await self.token_bucket.consume():
            return False
        
        # Check sliding window (for precise rate control)
        allowed, wait_time = await self.sliding_window.is_allowed()
        if not allowed:
            # Return token to bucket if sliding window rejects
            self.token_bucket.tokens = min(
                self.token_bucket.capacity,
                self.token_bucket.tokens + 1
            )
            return False
        
        return True
    
    async def record_success(self):
        """Record successful API call"""
        async with self._lock:
            self.success_count += 1
            await self._maybe_adjust_rate()
    
    async def record_error(self, is_rate_limit_error: bool = False):
        """Record failed API call"""
        async with self._lock:
            self.error_count += 1
            
            if is_rate_limit_error:
                # Immediately reduce rate on rate limit errors
                self.current_rate = max(1, int(self.current_rate * 0.5))
                self._update_limiters()
                logger.warning(f"Rate limit hit, reducing rate to {self.current_rate}/min")
            
            await self._maybe_adjust_rate()
    
    async def _maybe_adjust_rate(self):
        """Adjust rate based on success/error ratio"""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_interval:
            return
        
        total_requests = self.success_count + self.error_count
        if total_requests < 10:  # Need minimum sample size
            return
        
        success_rate = self.success_count / total_requests
        
        if success_rate > 0.95:  # Very high success rate
            # Gradually increase rate
            new_rate = min(
                self.base_config.requests_per_minute,
                int(self.current_rate * 1.1)
            )
        elif success_rate < 0.8:  # Low success rate
            # Decrease rate
            new_rate = max(1, int(self.current_rate * 0.8))
        else:
            new_rate = self.current_rate
        
        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self._update_limiters()
            logger.info(f"Adjusted rate to {self.current_rate}/min (success rate: {success_rate:.2%})")
        
        # Reset counters
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = now
    
    def _update_limiters(self):
        """Update internal limiters with new rate"""
        self.token_bucket.refill_rate = self.current_rate / 60.0
        self.sliding_window.max_requests = self.current_rate
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            "current_rate_per_minute": self.current_rate,
            "base_rate_per_minute": self.base_config.requests_per_minute,
            "tokens_available": self.token_bucket.tokens,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "requests_in_window": len(self.sliding_window.requests)
        }

class NewsAPIRateLimiter:
    """Specialized rate limiter for news APIs"""
    
    def __init__(self):
        # Different rate limits for different APIs
        self.limiters = {
            "financial_modeling_prep": AdaptiveRateLimiter(
                RateLimitConfig(
                    requests_per_minute=250,  # FMP free tier limit
                    requests_per_hour=1000,
                    burst_capacity=10,
                    cooldown_seconds=60
                )
            ),
            "grok_ai": AdaptiveRateLimiter(
                RateLimitConfig(
                    requests_per_minute=60,   # Conservative for AI API
                    requests_per_hour=1000,
                    burst_capacity=5,
                    cooldown_seconds=120
                )
            ),
            "supabase": AdaptiveRateLimiter(
                RateLimitConfig(
                    requests_per_minute=1000,  # High limit for database
                    requests_per_hour=10000,
                    burst_capacity=50,
                    cooldown_seconds=30
                )
            )
        }
    
    async def acquire(self, api_name: str) -> bool:
        """Acquire permission for specific API"""
        if api_name not in self.limiters:
            logger.warning(f"Unknown API: {api_name}")
            return True
        
        return await self.limiters[api_name].acquire()
    
    async def record_success(self, api_name: str):
        """Record successful API call"""
        if api_name in self.limiters:
            await self.limiters[api_name].record_success()
    
    async def record_error(self, api_name: str, is_rate_limit_error: bool = False):
        """Record failed API call"""
        if api_name in self.limiters:
            await self.limiters[api_name].record_error(is_rate_limit_error)
    
    async def wait_if_needed(self, api_name: str) -> float:
        """Wait if rate limit would be exceeded, return wait time"""
        if api_name not in self.limiters:
            return 0.0
        
        limiter = self.limiters[api_name]
        
        # Check if we can proceed immediately
        if await limiter.acquire():
            return 0.0
        
        # Calculate wait time
        token_wait = limiter.token_bucket.get_wait_time()
        window_allowed, window_wait = await limiter.sliding_window.is_allowed()
        
        wait_time = max(token_wait, window_wait)
        
        if wait_time > 0:
            logger.info(f"Rate limit reached for {api_name}, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        return wait_time
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all rate limiters"""
        return {
            api_name: limiter.get_stats()
            for api_name, limiter in self.limiters.items()
        }

# Global rate limiter instance
news_rate_limiter = NewsAPIRateLimiter()

# Decorator for automatic rate limiting
def rate_limited(api_name: str):
    """Decorator to automatically apply rate limiting to functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Wait if needed
            await news_rate_limiter.wait_if_needed(api_name)
            
            try:
                result = await func(*args, **kwargs)
                await news_rate_limiter.record_success(api_name)
                return result
            except Exception as e:
                # Check if it's a rate limit error
                is_rate_limit = any(phrase in str(e).lower() for phrase in [
                    'rate limit', 'too many requests', '429', 'quota exceeded'
                ])
                await news_rate_limiter.record_error(api_name, is_rate_limit)
                raise
        
        return wrapper
    return decorator
