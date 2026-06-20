# bookings services
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Booking, BookingSeat, SeatLock
from apps.vehicles.models import Seat
from apps.schedules.models import Schedule

class BookingService:
    @staticmethod
    def check_availability(schedule_id, seat_ids):
        schedule = Schedule.objects.select_for_update().get(id=schedule_id)
        if schedule.status != 'SCHEDULED' or schedule.departure_time < timezone.now():
            raise ValidationError('Schedule not available')
        booked = BookingSeat.objects.filter(booking__schedule=schedule,
            booking__status__in=['CONFIRMED','BOARDED']).values_list('seat_id', flat=True)
        locked = SeatLock.objects.filter(schedule=schedule, seat_id__in=seat_ids,
            is_active=True, expires_at__gt=timezone.now()).values_list('seat_id', flat=True)
        unavailable = set(booked) | set(locked)
        return [s for s in seat_ids if s not in unavailable]

    @staticmethod
    @transaction.atomic
    def create_booking(schedule_id, passenger, seat_ids, passenger_details, booking_type='ONLINE'):
        schedule = Schedule.objects.select_for_update().get(id=schedule_id)
        if schedule.available_seats < len(seat_ids):
            raise ValidationError('Not enough seats')
        total = schedule.fare * len(seat_ids)
        booking = Booking.objects.create(schedule=schedule, passenger=passenger,
            booking_type=booking_type, total_amount=total, number_of_seats=len(seat_ids),
            status='PENDING')
        for i, seat_id in enumerate(seat_ids):
            seat = Seat.objects.select_for_update().get(id=seat_id)
            BookingSeat.objects.create(booking=booking, seat=seat,
                passenger_name=passenger_details[i]['name'],
                passenger_phone=passenger_details[i]['phone'],
                fare=schedule.fare)
        schedule.booked_seats += len(seat_ids)
        schedule.available_seats -= len(seat_ids)
        schedule.save()
        SeatLock.objects.filter(schedule=schedule, seat_id__in=seat_ids).update(is_active=False)
        return booking