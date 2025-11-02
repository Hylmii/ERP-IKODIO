"""
Integration Layer URLs for notifications, webhooks, email, and system services
"""
from django.urls import path
from apps.core import integration_views as views

app_name = 'integration'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.integration_dashboard, name='dashboard'),
    
    # Email Templates
    path('email-templates/', views.EmailTemplateListView.as_view(), name='email-template-list'),
    path('email-templates/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='email-template-detail'),
    
    # Email Logs
    path('email-logs/', views.EmailLogListView.as_view(), name='email-log-list'),
    path('send-email/', views.send_email, name='send-email'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification-mark-read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification-mark-all-read'),
    
    # Webhooks
    path('webhooks/', views.WebhookListView.as_view(), name='webhook-list'),
    path('webhooks/<int:pk>/', views.WebhookDetailView.as_view(), name='webhook-detail'),
    path('webhooks/<int:pk>/test/', views.webhook_test, name='webhook-test'),
    
    # Webhook Deliveries
    path('webhook-deliveries/', views.WebhookDeliveryListView.as_view(), name='webhook-delivery-list'),
    
    # External Services
    path('services/', views.ExternalServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', views.ExternalServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:pk>/health-check/', views.external_service_health_check, name='service-health-check'),
    
    # API Logs
    path('api-logs/', views.APILogListView.as_view(), name='api-log-list'),
    
    # Scheduled Jobs
    path('jobs/', views.ScheduledJobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', views.ScheduledJobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:pk>/run/', views.scheduled_job_run, name='job-run'),
    
    # System Settings
    path('settings/', views.SystemSettingListView.as_view(), name='setting-list'),
    path('settings/<str:key>/', views.SystemSettingDetailView.as_view(), name='setting-detail'),
]
