# routes models
import uuid
from django.db import models
from django.core.validators import MinValueValidator

class Route(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'

    class RouteType(models.TextChoices):
        EXPRESS = 'EXPRESS', 'Express'
        NORMAL = 'NORMAL', 'Normal'
        INTER_COUNTY = 'INTER_COUNTY', 'Inter-County'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sacco = models.ForeignKey('saccos.SACCO', on_delete=models.CASCADE, related_name='routes')
    route_code = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    route_type = models.CharField(max_length=20, choices=RouteType.choices, default=RouteType.NORMAL)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_duration = models.DurationField()
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes'
        indexes = [
            models.Index(fields=['sacco', 'status']),
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['route_code']),
        ]

    def __str__(self):
        return f"{self.route_name} ({self.origin} - {self.destination})"

class Stop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    distance_from_origin = models.DecimalField(max_digits=10, decimal_places=2)
    fare_from_origin = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_pickup = models.BooleanField(default=True)
    is_dropoff = models.BooleanField(default=True)

    class Meta:
        db_table = 'stops'
        ordering = ['route', 'order']
        unique_together = ['route', 'order']