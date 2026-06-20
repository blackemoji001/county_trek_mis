# bookings views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, BookingSeat, SeatLock
from .services import BookingService
from apps.schedules.models import Schedule

@login_required
def search_routes(request):
    origin = request.GET.get('origin','')
    destination = request.GET.get('destination','')
    travel_date = request.GET.get('travel_date','')
    schedules = []
    if travel_date and origin and destination:
        schedules = Schedule.objects.filter(
            route__origin__icontains=origin,
            route__destination__icontains=destination,
            departure_time__date=travel_date,
            status='SCHEDULED',
            available_seats__gt=0
        ).select_related('route','vehicle')
    return render(request, 'bookings/search.html', {
        'schedules': schedules,
        'origin': origin,
        'destination': destination,
        'travel_date': travel_date
    })

@login_required
def select_seats(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    seats = schedule.vehicle.seats.all().order_by('row','column')
    booked = set(BookingSeat.objects.filter(booking__schedule=schedule,
        booking__status__in=['CONFIRMED','BOARDED']).values_list('seat_id', flat=True))
    locked = set(SeatLock.objects.filter(schedule=schedule, is_active=True,
        expires_at__gt=timezone.now()).values_list('seat_id', flat=True))
    seat_rows = {}
    for seat in seats:
        row = seat.row
        if row not in seat_rows:
            seat_rows[row] = []
        status = 'booked' if seat.id in booked else ('locked' if seat.id in locked else 'available')
        seat_rows[row].append({'id': seat.id, 'number': seat.seat_number,
                               'type': seat.seat_type, 'status': status, 'column': seat.column})
    return render(request, 'bookings/select_seats.html', {'schedule': schedule, 'seat_rows': seat_rows})

@login_required
def confirm_booking(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        selected = request.POST.getlist('seats')
        if not selected:
            messages.error(request, 'Select seats')
            return redirect('bookings:select_seats', schedule_id=schedule_id)
        passenger_details = [{'name': request.user.get_full_name(),
                              'phone': request.user.phone_number} for _ in selected]
        try:
            booking = BookingService.create_booking(schedule_id, request.user, selected, passenger_details)
            return redirect('payments:process', booking_reference=booking.booking_reference)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('bookings:select_seats', schedule_id=schedule_id)
    return redirect('bookings:select_seats', schedule_id=schedule_id)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(passenger=request.user).order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_reference):
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    return render(request, 'bookings/booking_detail.html', {'booking': booking, 'seats': booking.booking_seats.all()})