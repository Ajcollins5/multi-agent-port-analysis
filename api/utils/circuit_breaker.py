import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Dict, Optional
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

class CircuitBreaker:
    """Circuit breaker pattern implementation for resilient external API calls"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 expected_exception: type = Exception,
                 name: str = "default"):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # State tracking
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0  # For half-open state
        
        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_timeouts = 0
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.total_calls += 1
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logging.info(f"Circuit breaker {self.name}: Transitioning to HALF_OPEN")
            else:
                self.total_timeouts += 1
                raise CircuitBreakerOpenException(
                    f"Circuit breaker {self.name} is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - handle state transitions
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            # Require a few successful calls before fully closing
            if self.success_count >= 3:
                self._reset()
                logging.info(f"Circuit breaker {self.name}: Transitioning to CLOSED")
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure in half-open state immediately opens circuit
            self.state = CircuitState.OPEN
            logging.warning(f"Circuit breaker {self.name}: Transitioning to OPEN (half-open failure)")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logging.warning(f"Circuit breaker {self.name}: Transitioning to OPEN (threshold reached)")
    
    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_timeouts": self.total_timeouts,
            "failure_rate": self.total_failures / max(self.total_calls, 1),
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout
        }
    
    def force_open(self):
        """Manually open the circuit breaker"""
        self.state = CircuitState.OPEN
        self.last_failure_time = time.time()
        logging.warning(f"Circuit breaker {self.name}: Manually opened")
    
    def force_close(self):
        """Manually close the circuit breaker"""
        self._reset()
        logging.info(f"Circuit breaker {self.name}: Manually closed")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

# Decorator for easy circuit breaker usage
def circuit_breaker(failure_threshold: int = 5, 
                   timeout: int = 60,
                   expected_exception: type = Exception,
                   name: Optional[str] = None):
    """Decorator to add circuit breaker protection to functions"""
    
    def decorator(func):
        breaker_name = name or f"{func.__module__}.{func.__name__}"
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
            name=breaker_name
        )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(breaker.call(func, *args, **kwargs))
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            wrapper = async_wrapper
        else:
            wrapper = sync_wrapper
        
        # Attach breaker to wrapper for access to stats
        wrapper.circuit_breaker = breaker
        return wrapper
    
    return decorator

# Pre-configured circuit breakers for common services
yfinance_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    name="yfinance_api"
)

openai_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    name="openai_api"
)

supabase_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    name="supabase_api"
)

# Circuit breaker registry for monitoring
circuit_breaker_registry = {
    "yfinance": yfinance_circuit_breaker,
    "openai": openai_circuit_breaker,
    "supabase": supabase_circuit_breaker
}

def get_all_circuit_breaker_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all registered circuit breakers"""
    return {name: breaker.get_stats() for name, breaker in circuit_breaker_registry.items()}
