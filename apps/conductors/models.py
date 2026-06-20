# conductors models
import uuid
from django.db import models

class Conductor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='conductor_profile')
    sacco = models.ForeignKey('saccos.SACCO', on_delete=models.CASCADE, related_name='conductors')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conductors'

    @property
    def trips_today(self):
        from django.utils import timezone
        return self.user.schedules.filter(departure_time__date=timezone.now().date()).count()