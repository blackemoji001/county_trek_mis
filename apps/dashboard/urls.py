from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('system-admin/', views.system_admin_dashboard, name='system_admin'),
    path('sacco-manager/', views.sacco_manager_dashboard, name='sacco_manager'),
    path('driver/', views.driver_dashboard, name='driver'),
    path('conductor/', views.conductor_dashboard, name='conductor'),
    path('booking-agent/', views.booking_agent_dashboard, name='booking_agent'),
    path('passenger/', views.passenger_dashboard, name='passenger'),
]