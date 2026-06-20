from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import role_required
from .models import SACCO

@login_required
@role_required(['SYSTEM_ADMIN'])
def sacco_list(request):
    saccos = SACCO.objects.all()
    return render(request, 'sacco/list.html', {'saccos': saccos})

@login_required
@role_required(['SYSTEM_ADMIN'])
def sacco_create(request):
    if request.method == 'POST':
        SACCO.objects.create(
            name=request.POST['name'],
            registration_number=request.POST['registration_number'],
            email=request.POST['email'],
            phone_number=request.POST['phone_number'],
            address=request.POST['address']
        )
        messages.success(request, 'SACCO created.')
        return redirect('saccos:list')
    return render(request, 'sacco/create.html')

@login_required
def sacco_detail(request, pk):
    sacco = get_object_or_404(SACCO, id=pk)
    return render(request, 'sacco/detail.html', {'sacco': sacco})