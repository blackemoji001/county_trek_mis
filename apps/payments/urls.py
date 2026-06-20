from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('process/<str:booking_reference>/', views.process_payment, name='process'),
    path('waiting/<uuid:payment_id>/', views.payment_waiting, name='waiting'),
    path('receipt/<uuid:payment_id>/', views.payment_receipt, name='receipt'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('api/status/<uuid:payment_id>/', views.check_payment_status, name='check_status'),
]