from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "kisaanseva",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "process-reminders-daily": {
        "task": "app.tasks.notification_tasks.process_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "sync-external-data-weekly": {
        "task": "app.tasks.sync_tasks.sync_schemes",
        "schedule": crontab(day_of_week="sunday", hour=2, minute=0),
    },
    "expire-stale-sessions": {
        "task": "app.tasks.notification_tasks.expire_stale_sessions",
        "schedule": crontab(minute="*/15"),
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
