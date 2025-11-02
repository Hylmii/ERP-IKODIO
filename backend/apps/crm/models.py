"""
CRM & Sales models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, TimeStampedModel


class Client(BaseModel):
    """Client/Customer master data"""
    
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='Indonesia')
    
    # Company Details (for company type)
    tax_id = models.CharField(max_length=50, blank=True)  # NPWP
    company_registration = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # Contact Person
    contact_person_name = models.CharField(max_length=200, blank=True)
    contact_person_title = models.CharField(max_length=100, blank=True)
    contact_person_email = models.EmailField(blank=True)
    contact_person_phone = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Account Manager
    account_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_clients'
    )
    
    # Financial
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_terms_days = models.IntegerField(default=30)
    
    # Rating
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Lead(BaseModel):
    """Sales leads/prospects"""
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('cold_call', 'Cold Call'),
        ('event', 'Event'),
        ('partner', 'Partner'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted to Opportunity'),
        ('lost', 'Lost'),
    ]
    
    # Basic Information
    lead_number = models.CharField(max_length=50, unique=True, db_index=True)
    company_name = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)
    
    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Address
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Indonesia')
    
    # Lead Details
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    industry = models.CharField(max_length=100, blank=True)
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Qualification
    is_qualified = models.BooleanField(default=False)
    qualified_at = models.DateTimeField(null=True, blank=True)
    
    # Conversion
    converted_opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_lead'
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leads'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lead_number']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.lead_number} - {self.contact_name}"


class Opportunity(BaseModel):
    """Sales opportunities/deals"""
    
    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    PROBABILITY_CHOICES = [
        (10, '10% - Prospecting'),
        (25, '25% - Qualification'),
        (50, '50% - Proposal'),
        (75, '75% - Negotiation'),
        (100, '100% - Closed Won'),
        (0, '0% - Closed Lost'),
    ]
    
    # Basic Information
    opportunity_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Client
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    
    # Sales Details
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    probability = models.IntegerField(choices=PROBABILITY_CHOICES, default=10)
    
    # Value
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2)
    expected_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Timeline
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(null=True, blank=True)
    
    # Assignment
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_opportunities'
    )
    
    # Competitors
    competitors = models.TextField(blank=True)
    
    # Win/Loss
    is_won = models.BooleanField(default=False)
    win_loss_reason = models.TextField(blank=True)
    
    # Project reference (if won)
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunity'
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'opportunities'
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['opportunity_number']),
            models.Index(fields=['stage']),
            models.Index(fields=['owner']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return f"{self.opportunity_number} - {self.name}"


class Contract(BaseModel):
    """Client contracts (MOU, PO, SLA)"""
    
    CONTRACT_TYPE_CHOICES = [
        ('mou', 'MOU - Memorandum of Understanding'),
        ('po', 'PO - Purchase Order'),
        ('sla', 'SLA - Service Level Agreement'),
        ('nda', 'NDA - Non-Disclosure Agreement'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent for Review'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ]
    
    # Basic Information
    contract_number = models.CharField(max_length=50, unique=True, db_index=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Parties
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='contracts'
    )
    
    # Related records
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts'
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts'
    )
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    signed_date = models.DateField(null=True, blank=True)
    
    # Value
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Auto-renewal
    is_auto_renewable = models.BooleanField(default=False)
    renewal_notice_days = models.IntegerField(default=30)
    
    # Terms & Conditions
    payment_terms = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    # Owner
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_contracts'
    )
    
    # Documents
    contract_file = models.FileField(upload_to='contracts/', null=True, blank=True)
    signed_contract_file = models.FileField(upload_to='contracts/signed/', null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'contracts'
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.contract_number} - {self.title}"


class Quotation(BaseModel):
    """Sales quotations"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    # Basic Information
    quotation_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Client
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='quotations'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations'
    )
    
    # Timeline
    quotation_date = models.DateField()
    valid_until = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Tax
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Prepared by
    prepared_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='prepared_quotations'
    )
    
    # Acceptance
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Payment terms
    payment_terms = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    # Documents
    quotation_file = models.FileField(upload_to='quotations/', null=True, blank=True)
    
    class Meta:
        db_table = 'quotations'
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        ordering = ['-quotation_date']
        indexes = [
            models.Index(fields=['quotation_number']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        return f"{self.quotation_number} - {self.title}"


class QuotationLine(TimeStampedModel):
    """Quotation line items"""
    
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Display order
    line_number = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'quotation_lines'
        verbose_name = 'Quotation Line'
        verbose_name_plural = 'Quotation Lines'
        ordering = ['quotation', 'line_number']
    
    def __str__(self):
        return f"{self.quotation.quotation_number} - Line {self.line_number}"


class FollowUp(BaseModel):
    """Follow-up activities for leads/opportunities"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('demo', 'Product Demo'),
        ('visit', 'Site Visit'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Related records
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_ups'
    )
    
    # Activity Details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Schedule
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='assigned_follow_ups'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Outcome
    outcome = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    
    # Reminder
    send_reminder = models.BooleanField(default=True)
    reminder_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'follow_ups'
        verbose_name = 'Follow Up'
        verbose_name_plural = 'Follow Ups'
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.activity_type} - {self.subject}"
