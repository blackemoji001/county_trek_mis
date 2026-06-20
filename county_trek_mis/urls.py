from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('dashboard:index'), name='home'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('saccos/', include('apps.saccos.urls', namespace='saccos')),
    path('vehicles/', include('apps.vehicles.urls', namespace='vehicles')),
    path('drivers/', include('apps.drivers.urls', namespace='drivers')),
    path('conductors/', include('apps.conductors.urls', namespace='conductors')),
    path('routes/', include('apps.routes.urls', namespace='routes')),
    path('schedules/', include('apps.schedules.urls', namespace='schedules')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('tickets/', include('apps.tickets.urls', namespace='tickets')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]