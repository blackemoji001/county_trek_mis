# payments views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Payment, MpesaTransaction
from .services import MpesaService
from apps.bookings.models import Booking
import json, logging

logger = logging.getLogger(__name__)

@login_required
def process_payment(request, booking_reference):
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    if booking.status != 'PENDING':
        messages.error(request, 'Cannot pay')
        return redirect('bookings:my_bookings')
    if request.method == 'POST':
        phone = request.POST.get('phone_number', request.user.phone_number)
        payment = Payment.objects.create(booking=booking, amount=booking.total_amount,
            phone_number=phone, payment_method='MPESA', transaction_reference=f'PAY-{booking.booking_reference}')
        mpesa = MpesaService()
        result = mpesa.stk_push(phone, booking.total_amount, booking.booking_reference, 'Ticket')
        if result['success']:
            payment.merchant_request_id = result['merchant_request_id']
            payment.checkout_request_id = result['checkout_request_id']
            payment.status = 'PROCESSING'; payment.save()
            messages.info(request, 'Enter M-Pesa PIN')
            return redirect('payments:waiting', payment_id=payment.id)
        else:
            payment.status = 'FAILED'; payment.save()
            messages.error(request, f'Failed: {result["error"]}')
            return redirect('bookings:booking_detail', booking_reference=booking_reference)
    return render(request, 'payments/process.html', {'booking':booking})

@login_required
def payment_waiting(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/waiting.html', {'payment':payment})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        service = MpesaService()
        result = service.process_callback(data)
        if result['success']:
            payment = Payment.objects.get(checkout_request_id=result['checkout_request_id'])
            MpesaTransaction.objects.create(payment=payment, transaction_type='STK_PUSH',
                transaction_id=result['mpesa_receipt_number'], transaction_time=timezone.now(),
                amount=result['amount'], phone_number=result['phone_number'],
                merchant_request_id=result['merchant_request_id'],
                checkout_request_id=result['checkout_request_id'],
                result_code=0, result_description='Success',
                mpesa_receipt_number=result['mpesa_receipt_number'], raw_response=data)
            payment.status = 'COMPLETED'; payment.mpesa_receipt_number = result['mpesa_receipt_number']
            payment.payment_date = timezone.now(); payment.save()
            payment.booking.status = 'CONFIRMED'; payment.booking.save()
        else:
            payment = Payment.objects.filter(checkout_request_id=result.get('checkout_request_id')).first()
            if payment:
                payment.status = 'FAILED'; payment.save()
                MpesaTransaction.objects.create(payment=payment, transaction_type='STK_PUSH',
                    transaction_id='', transaction_time=timezone.now(), amount=payment.amount,
                    phone_number=payment.phone_number,
                    merchant_request_id=result.get('merchant_request_id',''),
                    checkout_request_id=result.get('checkout_request_id',''),
                    result_code=1, result_description=result.get('result_description',''),
                    raw_response=data)
        return JsonResponse({'ResultCode':0,'ResultDesc':'Success'})
    return JsonResponse({'ResultCode':1,'ResultDesc':'Invalid'})

@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/receipt.html', {'payment':payment, 'booking':payment.booking})

@login_required
def check_payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return JsonResponse({'status': payment.status})