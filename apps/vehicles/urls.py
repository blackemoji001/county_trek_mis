from django.urls import path
from . import views
app_name = 'vehicles'
urlpatterns = [
    path('', views.vehicle_list, name='list'),
    path('create/', views.vehicle_create, name='create'),
    path('<uuid:pk>/', views.vehicle_detail, name='detail'),
]