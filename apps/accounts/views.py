from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from .services import UserService
from .decorators import role_required
from apps.saccos.models import SACCO
from apps.drivers.models import Driver
from apps.conductors.models import Conductor
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_account_locked:
                messages.error(request, 'Account locked. Try again later.')
            elif not user.is_active:
                messages.error(request, 'Account deactivated.')
            else:
                login(request, user)
                user.unlock_account()
                if not request.POST.get('remember_me'):
                    request.session.set_expiry(0)
                UserService.log_login_activity(user, request)
                messages.success(request, f'Welcome {user.first_name}!')
                return redirect('dashboard:index')
        else:
            try:
                u = User.objects.get(email=email)
                u.lock_account()
                if u.is_account_locked:
                    messages.error(request, 'Account locked due to multiple failed attempts.')
                else:
                    messages.error(request, 'Invalid credentials.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        UserService.log_logout_activity(request.user)
        logout(request)
    return redirect('accounts:login')

def register_passenger(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_raw = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password1', '')

        # Remove spaces, dashes, etc.
        phone_digits = ''.join(filter(str.isdigit, phone_raw))

        # Validate phone number
        if len(phone_digits) != 9 or not phone_digits.startswith('7'):
            messages.error(request, 'Enter a valid 9‑digit phone number starting with 7 (e.g. 712345678). Do not include +254 or 0.')
            return render(request, 'accounts/register_passenger.html')

        # Format to +254XXXXXXXXX
        formatted_phone = '+254' + phone_digits

        try:
            with transaction.atomic():
                user = UserService.create_passenger(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=formatted_phone,
                    password=password
                )
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('dashboard:index')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'accounts/register_passenger.html')

@login_required
@role_required(['SYSTEM_ADMIN'])
def add_sacco_manager(request):
    saccos = SACCO.objects.filter(status='ACTIVE')
    temp_pwd = UserService.generate_temp_password()
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user = UserService.create_staff_user(
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST['email'],
                    phone_number='+254' + request.POST['phone_number'],
                    role='SACCO_MANAGER',
                    sacco_id=request.POST['sacco_id'],
                    password=temp_pwd,
                    created_by=request.user
                )
                if request.POST.get('send_email'):
                    UserService.send_credentials_email(user, temp_pwd)
                if request.POST.get('send_sms'):
                    UserService.send_credentials_sms(user, temp_pwd)
                messages.success(request, f'Manager created!')
                return redirect('accounts:manage_users')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/admin/add_sacco_manager.html', {'saccos': saccos, 'temp_password': temp_pwd})

@login_required
@role_required(['SYSTEM_ADMIN'])
def manage_users(request):
    users = User.objects.all().select_related('sacco').order_by('-date_joined')
    return render(request, 'accounts/admin/manage_users.html', {'users': users, 'saccos': SACCO.objects.all()})

@login_required
@role_required(['SACCO_MANAGER'])
def add_staff(request):
    sacco = request.user.sacco
    temp_pwd = UserService.generate_temp_password()
    if request.method == 'POST':
        staff_type = request.POST['staff_type']
        try:
            with transaction.atomic():
                user = UserService.create_staff_user(
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST['email'],
                    phone_number='+254' + request.POST['phone_number'],
                    role=staff_type.upper(),
                    sacco_id=sacco.id,
                    password=temp_pwd,
                    created_by=request.user
                )
                if staff_type == 'driver':
                    Driver.objects.create(user=user, sacco=sacco,
                        license_number=request.POST['license_number'],
                        license_expiry=request.POST['license_expiry'],
                        experience_years=request.POST.get('experience_years', 0))
                elif staff_type == 'conductor':
                    Conductor.objects.create(user=user, sacco=sacco,
                        employee_id=request.POST.get('employee_id', ''))
                if request.POST.get('send_credentials'):
                    UserService.send_credentials_sms(user, temp_pwd)
                messages.success(request, f'{staff_type.title()} added!')
                return redirect('accounts:manage_staff')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/sacco/add_staff.html', {
        'sacco': sacco,
        'temp_password': temp_pwd,
        'available_vehicles': sacco.vehicles.filter(status='ACTIVE')
    })

@login_required
@role_required(['SACCO_MANAGER'])
def manage_staff(request):
    sacco = request.user.sacco
    ctx = {
        'sacco': sacco,
        'drivers': Driver.objects.filter(sacco=sacco).select_related('user'),
        'conductors': Conductor.objects.filter(sacco=sacco).select_related('user'),
        'booking_agents': User.objects.filter(sacco=sacco, role='BOOKING_AGENT'),
        'available_vehicles': sacco.vehicles.filter(status='ACTIVE')
    }
    return render(request, 'accounts/sacco/manage_staff.html', ctx)

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            UserService.send_password_reset_otp(user)
            messages.success(request, 'OTP sent.')
            return redirect('accounts:password_reset_confirm')
        except User.DoesNotExist:
            messages.error(request, 'No user with that email.')
    return render(request, 'accounts/password_reset.html')

def password_reset_confirm(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        if UserService.verify_reset_otp(request.user, otp):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password reset.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'accounts/password_reset_confirm.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html')

@login_required
def user_detail_api(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({'id': str(user.id), 'name': user.get_full_name(), 'email': user.email, 'role': user.get_role_display()})

@login_required
@role_required(['SYSTEM_ADMIN'])
def deactivate_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid'}, status=400)

@login_required
@role_required(['SYSTEM_ADMIN'])
def reset_user_password(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        temp_pwd = UserService.generate_temp_password()
        user.set_password(temp_pwd)
        user.save()
        UserService.send_credentials_sms(user, temp_pwd)
        return JsonResponse({'success': True, 'temp_password': temp_pwd})
    return JsonResponse({'error': 'Invalid'}, status=400)