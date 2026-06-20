from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_passenger, name='register_passenger'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('admin/add-sacco-manager/', views.add_sacco_manager, name='add_sacco_manager'),
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('sacco/add-staff/', views.add_staff, name='add_staff'),
    path('sacco/manage-staff/', views.manage_staff, name='manage_staff'),
    path('api/users/<uuid:user_id>/details/', views.user_detail_api, name='user_detail_api'),
    path('api/users/<uuid:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('api/users/<uuid:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
]