# vehicles views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import Vehicle, Seat

@login_required
@role_required(['SACCO_MANAGER'])
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(sacco=request.user.sacco) if request.user.role == 'SACCO_MANAGER' else Vehicle.objects.all()
    return render(request, 'vehicles/list.html', {'vehicles': vehicles})

@login_required
@role_required(['SACCO_MANAGER'])
def vehicle_create(request):
    if request.method == 'POST':
        vehicle = Vehicle.objects.create(
            sacco=request.user.sacco,
            registration_number=request.POST['registration_number'],
            vehicle_type=request.POST['vehicle_type'],
            make=request.POST['make'],
            model=request.POST['model'],
            year=request.POST['year'],
            capacity=request.POST['capacity'],
            insurance_expiry=request.POST['insurance_expiry'],
            road_worthiness_expiry=request.POST['road_worthiness_expiry'],
        )
        cap = int(request.POST['capacity'])
        for i in range(1, cap+1):
            row = (i-1)//4 + 1
            col = ['A','B','C','D'][(i-1)%4]
            Seat.objects.create(vehicle=vehicle, seat_number=str(i), row=row, column=col,
                                is_window=(col in ['A','D']), is_aisle=(col in ['B','C']))
        messages.success(request, f'Vehicle {vehicle.registration_number} added!')
        return redirect('vehicles:list')
    return render(request, 'vehicles/create.html')

@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, id=pk)
    seats = vehicle.seats.all().order_by('row','column')
    seat_rows = {}
    for s in seats:
        seat_rows.setdefault(s.row, []).append(s)
    return render(request, 'vehicles/detail.html', {'vehicle': vehicle, 'seat_rows': seat_rows})