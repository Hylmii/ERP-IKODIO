"""
Integration Layer serializers for notifications, webhooks, email, and system services
"""
from rest_framework import serializers
from django.utils import timezone
from apps.core.integration_models import (
    EmailTemplate, EmailLog, Notification, Webhook, WebhookDelivery,
    ExternalService, APILog, ScheduledJob, SystemSetting
)


# ============= Email Template Serializers =============

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates"""
    
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type',
            'subject', 'body_html', 'body_text',
            'variables', 'is_active', 'usage_count',
            'created_at', 'updated_at'
        ]
    
    def get_usage_count(self, obj):
        """Count how many times template was used"""
        return obj.email_logs.count()


# ============= Email Log Serializers =============

class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for email logs"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_email', 'recipient_name',
            'subject', 'body_html', 'body_text',
            'template', 'template_name',
            'status', 'sent_at', 'error_message', 'retry_count',
            'metadata',
            'created_at'
        ]


# ============= Notification Serializers =============

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name',
            'notification_type', 'title', 'message',
            'related_model', 'related_id', 'action_url',
            'is_read', 'read_at', 'is_important',
            'metadata', 'time_ago',
            'created_at'
        ]
    
    def get_time_ago(self, obj):
        """Calculate time ago"""
        now = timezone.now()
        delta = now - obj.created_at
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h ago"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60}m ago"
        else:
            return "just now"


# ============= Webhook Serializers =============

class WebhookListSerializer(serializers.ModelSerializer):
    """List serializer for webhooks"""
    
    total_deliveries = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'description', 'url',
            'events', 'auth_type', 'is_active',
            'last_triggered_at', 'success_count', 'failure_count',
            'total_deliveries', 'success_rate',
            'created_at', 'updated_at'
        ]
    
    def get_total_deliveries(self, obj):
        """Total delivery attempts"""
        return obj.success_count + obj.failure_count
    
    def get_success_rate(self, obj):
        """Calculate success rate"""
        total = obj.success_count + obj.failure_count
        if total == 0:
            return None
        return round((obj.success_count / total) * 100, 2)


class WebhookSerializer(serializers.ModelSerializer):
    """Detail serializer for webhooks"""
    
    total_deliveries = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    recent_deliveries = serializers.SerializerMethodField()
    
    class Meta:
        model = Webhook
        fields = '__all__'
    
    def get_total_deliveries(self, obj):
        """Total deliveries"""
        serializer = WebhookListSerializer()
        return serializer.get_total_deliveries(obj)
    
    def get_success_rate(self, obj):
        """Success rate"""
        serializer = WebhookListSerializer()
        return serializer.get_success_rate(obj)
    
    def get_recent_deliveries(self, obj):
        """Get recent deliveries"""
        deliveries = obj.deliveries.order_by('-created_at')[:10]
        return WebhookDeliverySerializer(deliveries, many=True).data


# ============= Webhook Delivery Serializers =============

class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for webhook deliveries"""
    
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name',
            'event', 'payload',
            'request_url', 'response_status_code',
            'status', 'sent_at', 'duration_ms',
            'retry_count', 'next_retry_at', 'error_message',
            'created_at'
        ]


# ============= External Service Serializers =============

class ExternalServiceSerializer(serializers.ModelSerializer):
    """Serializer for external services"""
    
    health_status = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalService
        fields = [
            'id', 'name', 'service_type', 'description',
            'base_url', 'auth_type', 'config',
            'is_active', 'last_health_check', 'is_healthy',
            'health_check_error', 'health_status',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'auth_config': {'write_only': True}
        }
    
    def get_health_status(self, obj):
        """Get health status with age"""
        if not obj.last_health_check:
            return 'unknown'
        
        # Check if health check is recent (< 5 minutes)
        age = (timezone.now() - obj.last_health_check).total_seconds()
        if age > 300:  # 5 minutes
            return 'stale'
        
        return 'healthy' if obj.is_healthy else 'unhealthy'


# ============= API Log Serializers =============

class APILogSerializer(serializers.ModelSerializer):
    """Serializer for API logs"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = APILog
        fields = [
            'id', 'method', 'path', 'query_params',
            'user', 'user_name',
            'status_code', 'duration_ms',
            'ip_address', 'user_agent',
            'error_message',
            'created_at'
        ]


# ============= Scheduled Job Serializers =============

class ScheduledJobSerializer(serializers.ModelSerializer):
    """Serializer for scheduled jobs"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduledJob
        fields = [
            'id', 'name', 'description', 'job_type',
            'schedule_cron', 'task_name', 'task_params',
            'status', 'last_run_at', 'last_run_status',
            'last_run_duration_seconds', 'last_run_error',
            'next_run_at', 'total_runs', 'success_count', 'failure_count',
            'success_rate',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate"""
        if obj.total_runs == 0:
            return None
        return round((obj.success_count / obj.total_runs) * 100, 2)


# ============= System Setting Serializers =============

class SystemSettingSerializer(serializers.ModelSerializer):
    """Serializer for system settings"""
    
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    display_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'key', 'value', 'category', 'description',
            'value_type', 'is_required', 'is_sensitive',
            'updated_by', 'updated_by_name', 'display_value',
            'created_at', 'updated_at'
        ]
    
    def get_display_value(self, obj):
        """Get display value (hide sensitive values)"""
        if obj.is_sensitive:
            return '***HIDDEN***'
        return obj.value
