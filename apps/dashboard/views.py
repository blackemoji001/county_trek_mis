# dashboard views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from apps.bookings.models import Booking
from apps.saccos.models import SACCO
from apps.schedules.models import Schedule
from apps.payments.models import Payment
from apps.vehicles.models import Vehicle
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@login_required
def index(request):
    role_map = {
        'SYSTEM_ADMIN': 'dashboard:system_admin',
        'SACCO_MANAGER': 'dashboard:sacco_manager',
        'DRIVER': 'dashboard:driver',
        'CONDUCTOR': 'dashboard:conductor',
        'BOOKING_AGENT': 'dashboard:booking_agent',
        'PASSENGER': 'dashboard:passenger',
    }
    return redirect(role_map.get(request.user.role, 'accounts:login'))

@login_required
def system_admin_dashboard(request):
    today = timezone.now().date()
    ctx = {
        'total_saccos': SACCO.objects.count(),
        'total_users': User.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'total_revenue': Payment.objects.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
        'today_bookings': Booking.objects.filter(created_at__date=today).count(),
        'recent_bookings': Booking.objects.select_related('schedule__route','passenger').order_by('-created_at')[:10],
        'booking_trends': json.dumps([Booking.objects.filter(created_at__date=today-timedelta(days=i)).count() for i in range(6,-1,-1)]),
        'recent_activities': [],
    }
    return render(request, 'dashboard/system_admin.html', ctx)

@login_required
def sacco_manager_dashboard(request):
    sacco = request.user.sacco
    today = timezone.now().date()
    ctx = {
        'sacco': sacco,
        'vehicles_count': sacco.vehicles.count(),
        'today_revenue': Payment.objects.filter(booking__schedule__route__sacco=sacco, status='COMPLETED', payment_date__date=today).aggregate(total=Sum('amount'))['total'] or 0,
        'today_bookings': Booking.objects.filter(schedule__route__sacco=sacco, created_at__date=today).count(),
        'active_trips': Schedule.objects.filter(route__sacco=sacco, departure_time__date=today, status__in=['SCHEDULED','IN_PROGRESS']),
    }
    return render(request, 'dashboard/sacco_manager.html', ctx)

@login_required
def driver_dashboard(request):
    return render(request, 'dashboard/driver.html')
@login_required
def conductor_dashboard(request):
    return render(request, 'dashboard/conductor.html')
@login_required
def booking_agent_dashboard(request):
    return render(request, 'dashboard/booking_agent.html')
@login_required
def passenger_dashboard(request):
    upcoming = Booking.objects.filter(passenger=request.user, status__in=['CONFIRMED','PENDING'], schedule__departure_time__gte=timezone.now()).order_by('schedule__departure_time')
    return render(request, 'dashboard/passenger.html', {'upcoming_bookings': upcoming})