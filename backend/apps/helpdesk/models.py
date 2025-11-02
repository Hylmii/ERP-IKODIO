"""
Helpdesk/Support/Ticketing System models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, TimeStampedModel


class Ticket(BaseModel):
    """Support tickets/helpdesk requests"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('access', 'Access Request'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('question', 'Question'),
        ('incident', 'Incident'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Category & Priority
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Requester
    requester = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='submitted_tickets'
    )
    requester_email = models.EmailField()
    requester_phone = models.CharField(max_length=20, blank=True)
    
    # Client (if external)
    client = models.ForeignKey(
        'crm.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    assigned_team = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # SLA
    sla_policy = models.ForeignKey(
        'SLAPolicy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    response_due = models.DateTimeField(null=True, blank=True)
    resolution_due = models.DateTimeField(null=True, blank=True)
    
    # Timeline tracking
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    resolution = models.TextField(blank=True)
    resolution_time_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Related records
    related_project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    related_asset = models.ForeignKey(
        'asset.Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    
    # Satisfaction
    satisfaction_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    satisfaction_feedback = models.TextField(blank=True)
    
    # Tags
    tags = models.CharField(max_length=500, blank=True)
    
    # Attachments
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['requester']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"


class TicketComment(TimeStampedModel):
    """Ticket comments/updates"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='ticket_comments'
    )
    
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes not visible to requester
    
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'ticket_comments'
        verbose_name = 'Ticket Comment'
        verbose_name_plural = 'Ticket Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - Comment by {self.author.get_full_name()}"


class SLAPolicy(BaseModel):
    """Service Level Agreement policies"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    
    # Response time (in hours)
    response_time_hours = models.IntegerField()
    
    # Resolution time (in hours)
    resolution_time_hours = models.IntegerField()
    
    # Business hours
    is_business_hours_only = models.BooleanField(default=True)
    business_hours_start = models.TimeField(default='09:00')
    business_hours_end = models.TimeField(default='17:00')
    
    # Days
    include_weekends = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sla_policies'
        verbose_name = 'SLA Policy'
        verbose_name_plural = 'SLA Policies'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.priority})"


class TicketEscalation(TimeStampedModel):
    """Ticket escalation tracking"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='escalations'
    )
    
    escalated_from = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalations_from'
    )
    escalated_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalations_to'
    )
    
    reason = models.TextField()
    escalation_level = models.IntegerField(default=1)
    
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ticket_escalations'
        verbose_name = 'Ticket Escalation'
        verbose_name_plural = 'Ticket Escalations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - Level {self.escalation_level}"


class KnowledgeBase(BaseModel):
    """Knowledge base articles"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('faq', 'FAQ'),
        ('how_to', 'How To'),
        ('troubleshooting', 'Troubleshooting'),
        ('policy', 'Policy'),
        ('guide', 'Guide'),
    ]
    
    # Basic Information
    article_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Category
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Author
    author = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='knowledge_articles'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Metrics
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # SEO & Search
    keywords = models.CharField(max_length=500, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    # Attachments
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = 'Knowledge Base Article'
        verbose_name_plural = 'Knowledge Base Articles'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['article_number']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.article_number} - {self.title}"


class TicketTemplate(BaseModel):
    """Ticket templates for common requests"""
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    
    # Template content
    subject_template = models.CharField(max_length=200)
    description_template = models.TextField()
    
    # Default values
    default_category = models.CharField(max_length=50)
    default_priority = models.CharField(max_length=20)
    default_assigned_team = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_templates'
    )
    
    # SLA
    sla_policy = models.ForeignKey(
        SLAPolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_templates'
    )
    
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'ticket_templates'
        verbose_name = 'Ticket Template'
        verbose_name_plural = 'Ticket Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name
