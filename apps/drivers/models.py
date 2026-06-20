# drivers models
import uuid
from django.db import models

class Driver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='driver_profile')
    sacco = models.ForeignKey('saccos.SACCO', on_delete=models.CASCADE, related_name='drivers')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    experience_years = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'drivers'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"