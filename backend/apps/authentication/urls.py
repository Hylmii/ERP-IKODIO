"""
Authentication & Authorization URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # JWT Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Management
    path('register/', views.RegisterView.as_view(), name='register'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Password Management
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Role & Permission Management
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/<uuid:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    
    # Session Management
    path('sessions/', views.UserSessionListView.as_view(), name='session_list'),
    path('sessions/<uuid:pk>/revoke/', views.RevokeSessionView.as_view(), name='revoke_session'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
]
