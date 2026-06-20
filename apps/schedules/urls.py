from django.urls import path
from . import views
app_name = 'schedules'
urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('create/', views.schedule_create, name='create'),
    path('<uuid:pk>/', views.schedule_detail, name='detail'),
]