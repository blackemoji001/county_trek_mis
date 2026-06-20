import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'county_trek_mis.settings.development')
app = Celery('county_trek_mis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'cancel-expired-bookings': {
        'task': 'apps.bookings.tasks.cancel_expired_bookings',
        'schedule': crontab(minute='*/5'),
    },
    'clean-expired-seat-locks': {
        'task': 'apps.bookings.tasks.clean_expired_seat_locks',
        'schedule': crontab(minute='*/2'),
    },
    'send-trip-reminders': {
        'task': 'apps.notifications.tasks.send_trip_reminders',
        'schedule': crontab(hour='*/2'),
    },
}
