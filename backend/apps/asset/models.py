"""
IT Asset & Inventory Management models
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel, TimeStampedModel
from decimal import Decimal


class Asset(BaseModel):
    """IT Asset register (hardware, software, licenses)"""
    
    ASSET_TYPE_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('license', 'License'),
        ('accessory', 'Accessory'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    # Basic Information
    asset_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    
    # Category
    category = models.ForeignKey(
        'AssetCategory',
        on_delete=models.PROTECT,
        related_name='assets'
    )
    
    # Manufacturer & Model
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # Purchase Information
    vendor = models.ForeignKey(
        'Vendor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Warranty
    warranty_start = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)
    warranty_provider = models.CharField(max_length=200, blank=True)
    
    # License (for software/license assets)
    license_key = models.CharField(max_length=500, blank=True)
    license_start = models.DateField(null=True, blank=True)
    license_end = models.DateField(null=True, blank=True)
    license_seats = models.IntegerField(null=True, blank=True)
    license_used_seats = models.IntegerField(default=0)
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    assigned_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Depreciation
    depreciation_method = models.CharField(max_length=50, blank=True)
    useful_life_years = models.IntegerField(null=True, blank=True)
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Images & Documents
    image = models.ImageField(upload_to='assets/images/', null=True, blank=True)
    documents = models.JSONField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'assets'
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        ordering = ['asset_number']
        indexes = [
            models.Index(fields=['asset_number']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['serial_number']),
        ]
    
    def __str__(self):
        return f"{self.asset_number} - {self.name}"


class AssetCategory(BaseModel):
    """Asset categories"""
    
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
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'asset_categories'
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Vendor(BaseModel):
    """Vendor/Supplier master data"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    
    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='Indonesia')
    
    # Company Details
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Contact Person
    contact_person_name = models.CharField(max_length=200)
    contact_person_phone = models.CharField(max_length=20)
    contact_person_email = models.EmailField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Rating
    rating = models.IntegerField(null=True, blank=True)
    
    # Payment terms
    payment_terms_days = models.IntegerField(default=30)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Procurement(BaseModel):
    """Procurement/Purchase requests"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    procurement_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Requester
    requested_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='procurement_requests'
    )
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.PROTECT,
        related_name='procurements'
    )
    
    # Vendor
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='procurements'
    )
    
    # Priority & Status
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    request_date = models.DateField()
    required_date = models.DateField()
    ordered_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    
    # Amounts
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Budget
    budget = models.ForeignKey(
        'finance.Budget',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='procurements'
    )
    
    # Approval
    approved_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_procurements'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # PO reference
    po_number = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'procurements'
        verbose_name = 'Procurement'
        verbose_name_plural = 'Procurements'
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['procurement_number']),
            models.Index(fields=['status']),
            models.Index(fields=['requested_by']),
        ]
    
    def __str__(self):
        return f"{self.procurement_number} - {self.title}"


class ProcurementLine(TimeStampedModel):
    """Procurement line items"""
    
    procurement = models.ForeignKey(
        Procurement,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Asset category
    asset_category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='procurement_lines'
    )
    
    # Received tracking
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    line_number = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'procurement_lines'
        verbose_name = 'Procurement Line'
        verbose_name_plural = 'Procurement Lines'
        ordering = ['procurement', 'line_number']
    
    def __str__(self):
        return f"{self.procurement.procurement_number} - Line {self.line_number}"


class AssetMaintenance(BaseModel):
    """Asset maintenance scheduling and tracking"""
    
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('upgrade', 'Upgrade'),
        ('calibration', 'Calibration'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Asset
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='maintenances'
    )
    
    # Maintenance Details
    maintenance_number = models.CharField(max_length=50, unique=True, db_index=True)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Schedule
    scheduled_date = models.DateField()
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_maintenances'
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenances'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Cost
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Work performed
    work_performed = models.TextField(blank=True)
    parts_replaced = models.TextField(blank=True)
    
    # Next maintenance
    next_maintenance_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'asset_maintenances'
        verbose_name = 'Asset Maintenance'
        verbose_name_plural = 'Asset Maintenances'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['maintenance_number']),
            models.Index(fields=['asset']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.maintenance_number} - {self.asset.name}"


class AssetAssignment(TimeStampedModel):
    """Asset assignment history"""
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='asset_assignments'
    )
    
    assigned_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    
    location = models.CharField(max_length=200, blank=True)
    condition_at_assignment = models.TextField()
    condition_at_return = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'asset_assignments'
        verbose_name = 'Asset Assignment'
        verbose_name_plural = 'Asset Assignments'
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['asset', 'is_active']),
            models.Index(fields=['employee', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_number} → {self.employee.get_full_name()}"


class License(BaseModel):
    """Software license management"""
    
    LICENSE_TYPE_CHOICES = [
        ('perpetual', 'Perpetual'),
        ('subscription', 'Subscription'),
        ('trial', 'Trial'),
        ('volume', 'Volume'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    license_number = models.CharField(max_length=50, unique=True, db_index=True)
    software_name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=200)
    
    # License Details
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES)
    license_key = models.CharField(max_length=500, blank=True)
    
    # Seats
    total_seats = models.IntegerField()
    used_seats = models.IntegerField(default=0)
    
    # Dates
    purchase_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Cost
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2)
    annual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Vendor
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licenses'
    )
    
    # Auto-renewal
    is_auto_renewable = models.BooleanField(default=False)
    renewal_notice_days = models.IntegerField(default=30)
    
    # Owner/Manager
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_licenses'
    )
    
    notes = models.TextField(blank=True)
    documents = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'licenses'
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
        ordering = ['software_name']
        indexes = [
            models.Index(fields=['license_number']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.license_number} - {self.software_name}"
    
    @property
    def available_seats(self):
        return self.total_seats - self.used_seats
