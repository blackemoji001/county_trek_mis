from django.urls import path
from . import views
app_name = 'saccos'
urlpatterns = [
    path('', views.sacco_list, name='list'),
    path('create/', views.sacco_create, name='create'),
    path('<uuid:pk>/', views.sacco_detail, name='detail'),
]