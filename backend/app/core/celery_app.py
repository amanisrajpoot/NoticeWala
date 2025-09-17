"""
Celery configuration for NoticeWala Backend
"""

from celery import Celery
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Create Celery instance
celery_app = Celery(
    "noticewala",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.crawler_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.maintenance_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.crawler_tasks.*": {"queue": "crawler"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
        "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },
    
    # Task execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Task time limits
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "crawl-sources": {
            "task": "app.tasks.crawler_tasks.crawl_all_sources",
            "schedule": 3600.0,  # Every hour
        },
        "send-deadline-reminders": {
            "task": "app.tasks.notification_tasks.send_deadline_reminders",
            "schedule": 86400.0,  # Every day
        },
        "cleanup-old-notifications": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_notifications",
            "schedule": 604800.0,  # Every week
        },
        "update-source-stats": {
            "task": "app.tasks.maintenance_tasks.update_source_statistics",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Task error handler
@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")

# Log Celery configuration
logger.info(
    "Celery configured",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    queues=["crawler", "notifications", "maintenance"]
)
