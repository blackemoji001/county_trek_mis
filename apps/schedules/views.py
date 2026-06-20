# schedules views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import Schedule
from apps.routes.models import Route
from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver
from apps.conductors.models import Conductor

@login_required
def schedule_list(request):
    if request.user.role == 'SACCO_MANAGER':
        schedules = Schedule.objects.filter(route__sacco=request.user.sacco)
    elif request.user.role == 'DRIVER':
        schedules = Schedule.objects.filter(driver__user=request.user)
    else:
        schedules = Schedule.objects.all()
    return render(request, 'schedules/list.html', {'schedules': schedules})

@login_required
@role_required(['SACCO_MANAGER'])
def schedule_create(request):
    if request.method == 'POST':
        Schedule.objects.create(
            route_id=request.POST['route'],
            vehicle_id=request.POST['vehicle'],
            driver_id=request.POST['driver'],
            conductor_id=request.POST.get('conductor'),
            departure_time=request.POST['departure_time'],
            arrival_time=request.POST['arrival_time'],
            day_of_week=request.POST['day_of_week'],
            fare=request.POST['fare'],
            available_seats=Vehicle.objects.get(id=request.POST['vehicle']).capacity
        )
        messages.success(request, 'Schedule created.')
        return redirect('schedules:list')
    ctx = {
        'routes': Route.objects.filter(sacco=request.user.sacco, status='ACTIVE'),
        'vehicles': Vehicle.objects.filter(sacco=request.user.sacco, status='ACTIVE'),
        'drivers': Driver.objects.filter(sacco=request.user.sacco, is_active=True),
        'conductors': Conductor.objects.filter(sacco=request.user.sacco, is_active=True),
    }
    return render(request, 'schedules/create.html', ctx)

@login_required
def schedule_detail(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    return render(request, 'schedules/detail.html', {'schedule': schedule})