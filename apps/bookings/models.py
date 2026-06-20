# bookings models
import uuid
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Payment'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        BOARDED = 'BOARDED', 'Boarded'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        EXPIRED = 'EXPIRED', 'Expired'

    class BookingType(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        AGENT = 'AGENT', 'Agent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=20, unique=True)
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=BookingType.choices, default=BookingType.ONLINE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_seats = models.IntegerField()
    expiry_time = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['schedule', 'status']),
            models.Index(fields=['status', 'expiry_time']),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random, string
            self.booking_reference = 'CT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not self.expiry_time:
            self.expiry_time = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def cancel_booking(self, reason=''):
        with transaction.atomic():
            self.status = self.Status.CANCELLED
            self.cancelled_at = timezone.now()
            self.cancellation_reason = reason
            self.save()
            self.schedule.booked_seats -= self.number_of_seats
            self.schedule.available_seats += self.number_of_seats
            self.schedule.save()

class BookingSeat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_seats')
    seat = models.ForeignKey('vehicles.Seat', on_delete=models.CASCADE, related_name='booking_seats')
    passenger_name = models.CharField(max_length=255)
    passenger_phone = models.CharField(max_length=13)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    is_boarded = models.BooleanField(default=False)
    boarded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'booking_seats'
        unique_together = ['booking', 'seat']

class SeatLock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE, related_name='seat_locks')
    seat = models.ForeignKey('vehicles.Seat', on_delete=models.CASCADE, related_name='seat_locks')
    session_key = models.CharField(max_length=255)
    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'seat_locks'
        indexes = [models.Index(fields=['schedule','seat']), models.Index(fields=['expires_at'])]