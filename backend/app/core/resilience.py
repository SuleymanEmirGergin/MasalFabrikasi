from functools import wraps
import asyncio
import logging
from typing import Callable, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} retry attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator

def graceful_degradation(fallback_value: Any = None):
    """
    Decorator to return a fallback value on error instead of raising.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed: {e}. Using fallback.")
                return fallback_value
        
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable (circuit breaker open)"
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        import time
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time > self.timeout
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

# Global circuit breakers for critical services
openai_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=120)
replicate_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=120)
wiro_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

# Export
__all__ = [
    'retry_on_failure',
    'graceful_degradation',
    'CircuitBreaker',
    'openai_circuit_breaker',
    'replicate_circuit_breaker',
    'wiro_circuit_breaker',
]
