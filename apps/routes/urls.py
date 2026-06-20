from django.urls import path
from . import views
app_name = 'routes'
urlpatterns = [
    path('', views.route_list, name='list'),
    path('create/', views.route_create, name='create'),
    path('<uuid:pk>/', views.route_detail, name='detail'),
]