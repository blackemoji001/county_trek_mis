# notifications tasks
from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_trip_reminders():
    logger.info("Trip reminders sent.")
    return "Sent"