# schedules models
import uuid
from django.db import models
from django.utils import timezone

class Schedule(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        DELAYED = 'DELAYED', 'Delayed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey('routes.Route', on_delete=models.CASCADE, related_name='schedules')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='schedules')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, null=True, related_name='schedules')
    conductor = models.ForeignKey('conductors.Conductor', on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    day_of_week = models.CharField(max_length=3)
    is_recurring = models.BooleanField(default=False)
    available_seats = models.IntegerField()
    booked_seats = models.IntegerField(default=0)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'schedules'
        indexes = [
            models.Index(fields=['route', 'departure_time']),
            models.Index(fields=['vehicle', 'departure_time']),
            models.Index(fields=['status', 'departure_time']),
        ]

    def save(self, *args, **kwargs):
        if not self.available_seats:
            self.available_seats = self.vehicle.capacity
        super().save(*args, **kwargs)

    def start_trip(self):
        self.status = self.Status.IN_PROGRESS
        self.actual_departure = timezone.now()
        self.save()

    def complete_trip(self):
        self.status = self.Status.COMPLETED
        self.actual_arrival = timezone.now()
        self.save()