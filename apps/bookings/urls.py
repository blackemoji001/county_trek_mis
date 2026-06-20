from django.urls import path
from . import views
app_name = 'bookings'
urlpatterns = [
    path('search/', views.search_routes, name='search'),
    path('select-seats/<uuid:schedule_id>/', views.select_seats, name='select_seats'),
    path('confirm/<uuid:schedule_id>/', views.confirm_booking, name='confirm'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('<str:booking_reference>/', views.booking_detail, name='booking_detail'),
]