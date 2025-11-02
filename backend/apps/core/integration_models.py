"""
Integration Layer models for notifications, webhooks, and external services
"""
from django.db import models
from django.core.validators import URLValidator
from apps.core.models import BaseModel, TimeStampedModel


class EmailTemplate(BaseModel):
    """Email templates for notifications"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('welcome', 'Welcome Email'),
        ('password_reset', 'Password Reset'),
        ('invoice', 'Invoice Notification'),
        ('leave_approval', 'Leave Approval'),
        ('task_assignment', 'Task Assignment'),
        ('project_update', 'Project Update'),
        ('ticket_update', 'Ticket Update'),
        ('document_shared', 'Document Shared'),
        ('custom', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    subject = models.CharField(max_length=300)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)
    
    # Variables that can be used in template
    variables = models.JSONField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EmailLog(TimeStampedModel):
    """Email sending log"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True)
    
    subject = models.CharField(max_length=300)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)
    
    # Template used
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient_email} - {self.subject}"


class Notification(TimeStampedModel):
    """In-app notifications"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('task', 'Task'),
        ('mention', 'Mention'),
        ('approval', 'Approval Required'),
    ]
    
    recipient = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Link to related object
    related_model = models.CharField(max_length=100, blank=True)  # e.g., 'project.Task'
    related_id = models.IntegerField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    is_important = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"


class Webhook(BaseModel):
    """Webhook configurations"""
    
    EVENT_CHOICES = [
        ('project.created', 'Project Created'),
        ('project.updated', 'Project Updated'),
        ('task.created', 'Task Created'),
        ('task.completed', 'Task Completed'),
        ('invoice.created', 'Invoice Created'),
        ('invoice.paid', 'Invoice Paid'),
        ('ticket.created', 'Ticket Created'),
        ('ticket.resolved', 'Ticket Resolved'),
        ('employee.created', 'Employee Created'),
        ('document.uploaded', 'Document Uploaded'),
        ('all', 'All Events'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Endpoint
    url = models.URLField(max_length=500, validators=[URLValidator()])
    
    # Events to trigger on
    events = models.JSONField()  # List of events
    
    # Authentication
    auth_type = models.CharField(max_length=20, default='none')  # none, basic, bearer, api_key
    auth_credentials = models.JSONField(null=True, blank=True)
    
    # Headers
    custom_headers = models.JSONField(null=True, blank=True)
    
    # Secret for signature verification
    secret = models.CharField(max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Stats
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'webhooks'
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WebhookDelivery(TimeStampedModel):
    """Webhook delivery log"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    
    # Request details
    request_url = models.URLField(max_length=500)
    request_headers = models.JSONField(null=True, blank=True)
    request_body = models.TextField()
    
    # Response details
    response_status_code = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timing
    sent_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    
    # Retry
    retry_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'webhook_deliveries'
        verbose_name = 'Webhook Delivery'
        verbose_name_plural = 'Webhook Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook.name} - {self.event}"


class ExternalService(BaseModel):
    """External service integrations"""
    
    SERVICE_TYPE_CHOICES = [
        ('storage', 'Cloud Storage'),  # S3, Azure Blob, GCS
        ('payment', 'Payment Gateway'),  # Stripe, Midtrans, Xendit
        ('sms', 'SMS Gateway'),
        ('whatsapp', 'WhatsApp Business'),
        ('calendar', 'Calendar'),  # Google Calendar, Outlook
        ('analytics', 'Analytics'),  # Google Analytics, Mixpanel
        ('monitoring', 'Monitoring'),  # Sentry, DataDog
        ('custom', 'Custom API'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Base URL
    base_url = models.URLField(max_length=500, blank=True)
    
    # Authentication
    auth_type = models.CharField(max_length=20)  # api_key, oauth, basic, bearer
    auth_config = models.JSONField(null=True, blank=True)
    
    # Configuration
    config = models.JSONField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Health check
    last_health_check = models.DateTimeField(null=True, blank=True)
    is_healthy = models.BooleanField(default=True)
    health_check_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'external_services'
        verbose_name = 'External Service'
        verbose_name_plural = 'External Services'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.service_type})"


class APILog(TimeStampedModel):
    """API request/response log"""
    
    # Request details
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE, etc.
    path = models.CharField(max_length=500)
    query_params = models.JSONField(null=True, blank=True)
    request_headers = models.JSONField(null=True, blank=True)
    request_body = models.TextField(blank=True)
    
    # User
    user = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_logs'
    )
    
    # Response details
    status_code = models.IntegerField()
    response_headers = models.JSONField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    
    # Timing
    duration_ms = models.IntegerField()
    
    # Client info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'api_logs'
        verbose_name = 'API Log'
        verbose_name_plural = 'API Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['method', 'path']),
            models.Index(fields=['status_code']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code}"


class ScheduledJob(BaseModel):
    """Scheduled background jobs"""
    
    JOB_TYPE_CHOICES = [
        ('email_digest', 'Email Digest'),
        ('report_generation', 'Report Generation'),
        ('data_export', 'Data Export'),
        ('data_cleanup', 'Data Cleanup'),
        ('backup', 'Backup'),
        ('sync', 'Data Sync'),
        ('notification', 'Notification Sender'),
        ('custom', 'Custom Job'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('disabled', 'Disabled'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    
    # Schedule (cron expression)
    schedule_cron = models.CharField(max_length=100)
    
    # Function to execute
    task_name = models.CharField(max_length=200)  # Python path to task function
    task_params = models.JSONField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Last execution
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(max_length=20, blank=True)
    last_run_duration_seconds = models.IntegerField(null=True, blank=True)
    last_run_error = models.TextField(blank=True)
    
    # Next execution
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_runs = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'scheduled_jobs'
        verbose_name = 'Scheduled Job'
        verbose_name_plural = 'Scheduled Jobs'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SystemSetting(TimeStampedModel):
    """System-wide settings/configurations"""
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('email', 'Email'),
        ('notification', 'Notification'),
        ('security', 'Security'),
        ('integration', 'Integration'),
        ('appearance', 'Appearance'),
    ]
    
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    # Data type hint
    value_type = models.CharField(max_length=20, default='string')  # string, integer, boolean, json
    
    # Validation
    is_required = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)  # Hide value in UI
    
    # Last updated by
    updated_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_settings'
    )
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} ({self.category})"
