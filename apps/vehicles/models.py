# vehicles models
import uuid
from django.db import models

class Vehicle(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        IN_MAINTENANCE = 'IN_MAINTENANCE', 'In Maintenance'
        OUT_OF_SERVICE = 'OUT_OF_SERVICE', 'Out of Service'

    class VehicleType(models.TextChoices):
        BUS = 'BUS', 'Bus'
        MINIBUS = 'MINIBUS', 'Minibus'
        VAN = 'VAN', 'Van'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sacco = models.ForeignKey('saccos.SACCO', on_delete=models.CASCADE, related_name='vehicles')
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    insurance_expiry = models.DateField()
    road_worthiness_expiry = models.DateField()
    photo = models.ImageField(upload_to='vehicle_photos/', null=True, blank=True)
    assigned_driver = models.OneToOneField('drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vehicle')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'
        indexes = [models.Index(fields=['sacco', 'status']), models.Index(fields=['registration_number'])]

    def __str__(self):
        return f"{self.registration_number} - {self.make} {self.model}"

class Seat(models.Model):
    class SeatType(models.TextChoices):
        REGULAR = 'REGULAR', 'Regular'
        VIP = 'VIP', 'VIP'
        WHEELCHAIR = 'WHEELCHAIR', 'Wheelchair'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20, choices=SeatType.choices, default=SeatType.REGULAR)
    floor = models.IntegerField(default=1)
    row = models.IntegerField()
    column = models.CharField(max_length=1)
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    price_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)

    class Meta:
        db_table = 'seats'
        unique_together = ['vehicle', 'seat_number']
        ordering = ['floor', 'row', 'column']
