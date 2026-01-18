import os
from celery import Celery
from kombu import Queue, Exchange
from app.core.config import settings

# Redis URL for Broker and Result Backend
CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "masal_fabrikasi",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.story_tasks"]
)

# Define Exchanges
default_exchange = Exchange('default', type='direct')
dlq_exchange = Exchange('dlq', type='direct')

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="Europe/Istanbul",
    enable_utc=True,
    
    # Queues & Routing (with Dead Letter Queue)
    task_queues=(
        Queue('default', default_exchange, routing_key='default'),
        Queue('story_generation', default_exchange, routing_key='story_generation'),
        Queue('dead_letter', dlq_exchange, routing_key='dead_letter'),
    ),
    task_routes={
        "app.tasks.story_tasks.*": {"queue": "story_generation"},
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',

    # Reliability & Performance
    task_acks_late=True,  # ACK after task completes (prevents task loss)
    worker_prefetch_multiplier=1,  # Fetch 1 task at a time (prevents long queues)
    
    # Result backend optimization
    result_expires=3600,  # Results expire after 1 hour (prevent Redis bloat)
    result_compression="gzip",  # Compress large results
    
    # Task execution limits
    task_time_limit=600,  # Hard limit: 10 minutes
    task_soft_time_limit=540,  # Soft limit: 9 minutes (allows cleanup)
    
    # Rate limiting (prevent external API throttling)
    task_annotations={
        "app.tasks.story_tasks.generate_full_story_task": {
            "rate_limit": "10/m",  # Max 10 story generations per minute
        }
    },
    
    # Worker settings
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,  # Enable rate limiting
    
    # Error handling
    task_reject_on_worker_lost=True,  # Reject tasks if worker crashes
    task_ignore_result=False,  # Keep results for monitoring
)

if __name__ == "__main__":
    celery_app.start()
