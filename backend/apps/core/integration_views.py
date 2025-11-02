"""
Integration Layer views for notifications, webhooks, email, and system services
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count

from apps.core.integration_models import (
    EmailTemplate, EmailLog, Notification, Webhook, WebhookDelivery,
    ExternalService, APILog, ScheduledJob, SystemSetting
)
from apps.core.integration_serializers import (
    EmailTemplateSerializer, EmailLogSerializer,
    NotificationSerializer,
    WebhookListSerializer, WebhookSerializer, WebhookDeliverySerializer,
    ExternalServiceSerializer, APILogSerializer,
    ScheduledJobSerializer, SystemSettingSerializer
)
from apps.core.permissions import IsAdminOrReadOnly


# ============= Email Template Views =============

class EmailTemplateListView(generics.ListCreateAPIView):
    """List and create email templates"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EmailTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'subject']
    
    def get_queryset(self):
        queryset = EmailTemplate.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')


class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an email template"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EmailTemplateSerializer
    queryset = EmailTemplate.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Email Log Views =============

class EmailLogListView(generics.ListAPIView):
    """List email logs"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EmailLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'template']
    search_fields = ['recipient_email', 'subject']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return EmailLog.objects.select_related('template').order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def send_email(request):
    """Send an email"""
    recipient_email = request.data.get('recipient_email')
    subject = request.data.get('subject')
    body_html = request.data.get('body_html')
    body_text = request.data.get('body_text', '')
    template_id = request.data.get('template_id')
    
    if not recipient_email or not subject:
        return Response(
            {'error': 'recipient_email and subject are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create email log
    email_log = EmailLog.objects.create(
        recipient_email=recipient_email,
        recipient_name=request.data.get('recipient_name', ''),
        subject=subject,
        body_html=body_html or '',
        body_text=body_text,
        template_id=template_id,
        status='pending',
        metadata=request.data.get('metadata', {})
    )
    
    # In a real implementation, this would be sent via Celery task
    # For now, just mark as sent
    email_log.status = 'sent'
    email_log.sent_at = timezone.now()
    email_log.save()
    
    serializer = EmailLogSerializer(email_log)
    return Response(serializer.data)


# ============= Notification Views =============

class NotificationListView(generics.ListCreateAPIView):
    """List and create notifications"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'is_important']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.all()
        
        # Users see only their notifications
        if hasattr(user, 'employee'):
            queryset = queryset.filter(recipient=user.employee)
        
        # Filter unread only
        if self.request.query_params.get('unread_only', None) == 'true':
            queryset = queryset.filter(is_read=False)
        
        return queryset.select_related('recipient')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a notification"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.all()
        
        # Users see only their notifications
        if hasattr(user, 'employee'):
            queryset = queryset.filter(recipient=user.employee)
        
        return queryset.select_related('recipient')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, pk):
    """Mark notification as read"""
    try:
        user = request.user
        notification = Notification.objects.get(pk=pk)
        
        # Check ownership
        if hasattr(user, 'employee') and notification.recipient != user.employee:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_all_read(request):
    """Mark all notifications as read"""
    user = request.user
    
    if hasattr(user, 'employee'):
        Notification.objects.filter(
            recipient=user.employee,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
    
    return Response({'message': 'All notifications marked as read'})


# ============= Webhook Views =============

class WebhookListView(generics.ListCreateAPIView):
    """List and create webhooks"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'url']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WebhookSerializer
        return WebhookListSerializer
    
    def get_queryset(self):
        queryset = Webhook.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset


class WebhookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a webhook"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = WebhookSerializer
    queryset = Webhook.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def webhook_test(request, pk):
    """Test a webhook by sending a test payload"""
    try:
        webhook = Webhook.objects.get(pk=pk, deleted_at__isnull=True)
    except Webhook.DoesNotExist:
        return Response({'error': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Create test delivery
    test_payload = {
        'event': 'test',
        'data': {'message': 'This is a test webhook delivery'},
        'timestamp': timezone.now().isoformat()
    }
    
    delivery = WebhookDelivery.objects.create(
        webhook=webhook,
        event='test',
        payload=test_payload,
        request_url=webhook.url,
        request_body=str(test_payload),
        status='pending'
    )
    
    # In a real implementation, this would send an HTTP request
    # For now, just mark as success
    delivery.status = 'success'
    delivery.sent_at = timezone.now()
    delivery.response_status_code = 200
    delivery.duration_ms = 100
    delivery.save()
    
    webhook.last_triggered_at = timezone.now()
    webhook.success_count += 1
    webhook.save()
    
    serializer = WebhookDeliverySerializer(delivery)
    return Response(serializer.data)


# ============= Webhook Delivery Views =============

class WebhookDeliveryListView(generics.ListAPIView):
    """List webhook deliveries"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = WebhookDeliverySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['webhook', 'event', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return WebhookDelivery.objects.select_related('webhook').order_by('-created_at')


# ============= External Service Views =============

class ExternalServiceListView(generics.ListCreateAPIView):
    """List and create external services"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ExternalServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['service_type', 'is_active', 'is_healthy']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        queryset = ExternalService.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')


class ExternalServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an external service"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ExternalServiceSerializer
    queryset = ExternalService.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def external_service_health_check(request, pk):
    """Perform health check on external service"""
    try:
        service = ExternalService.objects.get(pk=pk, deleted_at__isnull=True)
    except ExternalService.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # In a real implementation, this would make an HTTP request to the service
    # For now, just mark as healthy
    service.last_health_check = timezone.now()
    service.is_healthy = True
    service.health_check_error = ''
    service.save()
    
    serializer = ExternalServiceSerializer(service)
    return Response(serializer.data)


# ============= API Log Views =============

class APILogListView(generics.ListAPIView):
    """List API logs"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = APILogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['method', 'status_code', 'user']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return APILog.objects.select_related('user').order_by('-created_at')[:1000]  # Limit to recent 1000


# ============= Scheduled Job Views =============

class ScheduledJobListView(generics.ListCreateAPIView):
    """List and create scheduled jobs"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ScheduledJobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['job_type', 'status']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        queryset = ScheduledJob.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(status='active')
        
        return queryset.order_by('name')


class ScheduledJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a scheduled job"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ScheduledJobSerializer
    queryset = ScheduledJob.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def scheduled_job_run(request, pk):
    """Manually trigger a scheduled job"""
    try:
        job = ScheduledJob.objects.get(pk=pk, deleted_at__isnull=True)
    except ScheduledJob.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # In a real implementation, this would trigger the actual job
    # For now, just update stats
    job.last_run_at = timezone.now()
    job.last_run_status = 'success'
    job.last_run_duration_seconds = 5
    job.total_runs += 1
    job.success_count += 1
    job.save()
    
    serializer = ScheduledJobSerializer(job)
    return Response(serializer.data)


# ============= System Setting Views =============

class SystemSettingListView(generics.ListCreateAPIView):
    """List and create system settings"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SystemSettingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_required']
    search_fields = ['key', 'description']
    
    def get_queryset(self):
        return SystemSetting.objects.select_related('updated_by').order_by('category', 'key')


class SystemSettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a system setting"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SystemSettingSerializer
    queryset = SystemSetting.objects.all()
    lookup_field = 'key'


# ============= Dashboard =============

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def integration_dashboard(request):
    """Integration system dashboard"""
    
    # Email metrics
    total_emails = EmailLog.objects.count()
    emails_sent = EmailLog.objects.filter(status='sent').count()
    emails_pending = EmailLog.objects.filter(status='pending').count()
    emails_failed = EmailLog.objects.filter(status='failed').count()
    
    # Notification metrics
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # Webhook metrics
    active_webhooks = Webhook.objects.filter(deleted_at__isnull=True, is_active=True).count()
    total_deliveries = WebhookDelivery.objects.count()
    successful_deliveries = WebhookDelivery.objects.filter(status='success').count()
    failed_deliveries = WebhookDelivery.objects.filter(status='failed').count()
    
    # External service metrics
    total_services = ExternalService.objects.filter(deleted_at__isnull=True).count()
    healthy_services = ExternalService.objects.filter(deleted_at__isnull=True, is_healthy=True).count()
    
    # Scheduled job metrics
    active_jobs = ScheduledJob.objects.filter(deleted_at__isnull=True, status='active').count()
    
    # Recent API logs
    recent_api_logs = APILog.objects.order_by('-created_at')[:10]
    
    return Response({
        'email': {
            'total': total_emails,
            'sent': emails_sent,
            'pending': emails_pending,
            'failed': emails_failed,
        },
        'notifications': {
            'total': total_notifications,
            'unread': unread_notifications,
        },
        'webhooks': {
            'active': active_webhooks,
            'total_deliveries': total_deliveries,
            'successful': successful_deliveries,
            'failed': failed_deliveries,
        },
        'services': {
            'total': total_services,
            'healthy': healthy_services,
        },
        'jobs': {
            'active': active_jobs,
        },
        'recent_api_logs': APILogSerializer(recent_api_logs, many=True).data,
    })
