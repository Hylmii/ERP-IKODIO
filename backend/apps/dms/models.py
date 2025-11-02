"""
Document Management System (DMS) models
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.core.models import BaseModel, TimeStampedModel


class Document(BaseModel):
    """Document storage and management"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contract'),
        ('invoice', 'Invoice'),
        ('proposal', 'Proposal'),
        ('report', 'Report'),
        ('policy', 'Policy'),
        ('form', 'Form'),
        ('image', 'Image'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    document_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    
    # File
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    file_extension = models.CharField(max_length=10)
    mime_type = models.CharField(max_length=100)
    
    # Version
    version = models.CharField(max_length=20, default='1.0')
    is_latest_version = models.BooleanField(default=True)
    parent_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )
    
    # Category & Tags
    category = models.ForeignKey(
        'DocumentCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    tags = models.CharField(max_length=500, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    # Owner & Creator
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_documents'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Expiry
    expiry_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    
    # Access control
    is_public = models.BooleanField(default=False)
    is_confidential = models.BooleanField(default=False)
    
    # Department/Project
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    
    # Client
    client = models.ForeignKey(
        'crm.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    
    # Metrics
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Checksum for integrity
    checksum = models.CharField(max_length=64, blank=True)
    
    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_number']),
            models.Index(fields=['status']),
            models.Index(fields=['document_type']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_latest_version']),
        ]
    
    def __str__(self):
        return f"{self.document_number} - {self.title}"


class DocumentCategory(BaseModel):
    """Document categories/folders"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    # Access control
    is_restricted = models.BooleanField(default=False)
    
    # Icon/Color for UI
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)  # Hex color
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'document_categories'
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DocumentVersion(TimeStampedModel):
    """Document version history"""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='version_history'
    )
    
    version_number = models.CharField(max_length=20)
    file = models.FileField(upload_to='documents/versions/%Y/%m/')
    file_size = models.BigIntegerField()
    checksum = models.CharField(max_length=64, blank=True)
    
    # Changes
    change_summary = models.TextField()
    uploaded_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='uploaded_document_versions'
    )
    
    class Meta:
        db_table = 'document_versions'
        verbose_name = 'Document Version'
        verbose_name_plural = 'Document Versions'
        ordering = ['-created_at']
        unique_together = [['document', 'version_number']]
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"


class DocumentApproval(BaseModel):
    """Document approval workflow"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    
    # Approver
    approver = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='document_approvals'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval details
    approval_level = models.IntegerField(default=1)
    due_date = models.DateField(null=True, blank=True)
    
    # Response
    approved_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    
    # Signature
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    
    class Meta:
        db_table = 'document_approvals'
        verbose_name = 'Document Approval'
        verbose_name_plural = 'Document Approvals'
        ordering = ['approval_level', 'created_at']
        indexes = [
            models.Index(fields=['document', 'status']),
            models.Index(fields=['approver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Level {self.approval_level}"


class DocumentAccess(TimeStampedModel):
    """Document access permissions"""
    
    PERMISSION_TYPE_CHOICES = [
        ('view', 'View'),
        ('download', 'Download'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('share', 'Share'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_permissions'
    )
    
    # Grant to employee
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='document_accesses'
    )
    
    # Or grant to department
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='document_accesses'
    )
    
    # Or grant to role
    role = models.ForeignKey(
        'authentication.Role',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='document_accesses'
    )
    
    # Permissions
    can_view = models.BooleanField(default=True)
    can_download = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Granted by
    granted_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='granted_document_accesses'
    )
    
    class Meta:
        db_table = 'document_accesses'
        verbose_name = 'Document Access'
        verbose_name_plural = 'Document Accesses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['employee']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        if self.employee:
            return f"{self.document.title} → {self.employee.get_full_name()}"
        elif self.department:
            return f"{self.document.title} → {self.department.name}"
        elif self.role:
            return f"{self.document.title} → {self.role.name}"
        return f"{self.document.title} - Access"


class DocumentTemplate(BaseModel):
    """Document templates"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('contract', 'Contract Template'),
        ('invoice', 'Invoice Template'),
        ('proposal', 'Proposal Template'),
        ('report', 'Report Template'),
        ('form', 'Form Template'),
        ('other', 'Other Template'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template file
    file = models.FileField(upload_to='templates/')
    file_extension = models.CharField(max_length=10)
    
    # Variables/placeholders in template
    variables = models.JSONField(null=True, blank=True)
    
    # Category
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates'
    )
    
    # Usage
    usage_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'document_templates'
        verbose_name = 'Document Template'
        verbose_name_plural = 'Document Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DocumentActivity(TimeStampedModel):
    """Document activity log (views, downloads, etc.)"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('created', 'Created'),
        ('viewed', 'Viewed'),
        ('downloaded', 'Downloaded'),
        ('edited', 'Edited'),
        ('shared', 'Shared'),
        ('deleted', 'Deleted'),
        ('restored', 'Restored'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    
    user = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_activities'
    )
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_activities'
        verbose_name = 'Document Activity'
        verbose_name_plural = 'Document Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', 'activity_type']),
            models.Index(fields=['user', 'activity_type']),
        ]
    
    def __str__(self):
        return f"{self.activity_type} - {self.document.title}"
