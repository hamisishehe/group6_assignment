from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"

beat_schedule = {
    "run-monitoring-every-5-minutes": {
        "task": "tasks.run_all_monitors",
        "schedule": crontab(minute="*/5"),  # every 5 minutes
    }
}
