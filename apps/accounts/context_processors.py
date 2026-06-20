def user_role_context(request):
    context = {'user_role': None}
    if request.user.is_authenticated:
        context['user_role'] = request.user.role
        context['is_system_admin'] = request.user.role == 'SYSTEM_ADMIN'
        context['is_sacco_manager'] = request.user.role == 'SACCO_MANAGER'
        context['is_driver'] = request.user.role == 'DRIVER'
        context['is_conductor'] = request.user.role == 'CONDUCTOR'
        context['is_booking_agent'] = request.user.role == 'BOOKING_AGENT'
        context['is_passenger'] = request.user.role == 'PASSENGER'
    return context
