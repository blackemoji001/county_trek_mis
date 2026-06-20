# routes views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import Route

@login_required
@role_required(['SACCO_MANAGER'])
def route_list(request):
    routes = Route.objects.filter(sacco=request.user.sacco) if request.user.role == 'SACCO_MANAGER' else Route.objects.all()
    return render(request, 'routes/list.html', {'routes': routes})

@login_required
@role_required(['SACCO_MANAGER'])
def route_create(request):
    if request.method == 'POST':
        Route.objects.create(
            sacco=request.user.sacco,
            route_code=request.POST['route_code'],
            route_name=request.POST['route_name'],
            origin=request.POST['origin'],
            destination=request.POST['destination'],
            route_type=request.POST['route_type'],
            distance_km=request.POST['distance_km'],
            estimated_duration=request.POST['estimated_duration'],
            base_fare=request.POST['base_fare'],
        )
        messages.success(request, 'Route created.')
        return redirect('routes:list')
    return render(request, 'routes/create.html')

@login_required
def route_detail(request, pk):
    route = Route.objects.get(pk=pk)
    return render(request, 'routes/detail.html', {'route': route, 'stops': route.stops.order_by('order')})