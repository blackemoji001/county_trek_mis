# bookings tasks
from celery import shared_task
from django.utils import timezone
from apps.bookings.models import Booking, SeatLock
import logging
logger = logging.getLogger(__name__)

@shared_task
def cancel_expired_bookings():
    expired = Booking.objects.filter(status='PENDING', expiry_time__lt=timezone.now())
    count = 0
    for b in expired:
        try:
            b.cancel_booking(reason='Expired')
            count += 1
        except Exception as e:
            logger.error(str(e))
    return f'Cancelled {count}'

@shared_task
def clean_expired_seat_locks():
    expired = SeatLock.objects.filter(expires_at__lt=timezone.now(), is_active=True)
    count = expired.count()
    expired.update(is_active=False)
    return f'Cleaned {count}'