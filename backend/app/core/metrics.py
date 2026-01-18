"""
Metrics Collection Service - Prometheus compatible metrics
"""
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable


# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Story generation metrics
story_generation_total = Counter(
    'story_generation_total',
    'Total story generations',
    ['language', 'story_type', 'status']
)

story_generation_duration_seconds = Histogram(
    'story_generation_duration_seconds',
    'Story generation duration in seconds',
    ['story_type']
)

# Active users
active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

# Background jobs
background_jobs_total = Counter(
    'background_jobs_total',
    'Total background jobs',
    ['job_type', 'status']
)

background_jobs_duration_seconds = Histogram(
    'background_jobs_duration_seconds',
    'Background job duration in seconds',
    ['job_type']
)

# Database metrics
database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits'
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses'
)


class MetricsCollector:
    """Helper class for metrics collection"""
    
    @staticmethod
    def track_request(method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics"""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def track_story_generation(language: str, story_type: str, status: str, duration: float):
        """Track story generation metrics"""
        story_generation_total.labels(
            language=language,
            story_type=story_type,
            status=status
        ).inc()
        
        story_generation_duration_seconds.labels(
            story_type=story_type
        ).observe(duration)
    
    @staticmethod
    def track_background_job(job_type: str, status: str, duration: float):
        """Track background job metrics"""
        background_jobs_total.labels(
            job_type=job_type,
            status=status
        ).inc()
        
        background_jobs_duration_seconds.labels(
            job_type=job_type
        ).observe(duration)
    
    @staticmethod
    def track_cache_hit(hit: bool):
        """Track cache hit/miss"""
        if hit:
            cache_hits_total.inc()
        else:
            cache_misses_total.inc()


def track_time(metric_histogram, labels: dict = None):
    """
    Decorator to track execution time
    
    Usage:
        @track_time(story_generation_duration_seconds, {'story_type': 'masal'})
        async def generate_story():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric_histogram.labels(**labels).observe(duration)
                else:
                    metric_histogram.observe(duration)
        return wrapper
    return decorator
