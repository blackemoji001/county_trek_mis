# payments models
import uuid
from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class PaymentMethod(models.TextChoices):
        MPESA = 'MPESA', 'M-Pesa'
        CASH = 'CASH', 'Cash'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MPESA)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=13)
    result_description = models.TextField(blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['status', '-created_at']),
        ]

class MpesaTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='mpesa_transactions')
    transaction_type = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    transaction_time = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=13)
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    result_code = models.IntegerField()
    result_description = models.TextField()
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    raw_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mpesa_transactions'