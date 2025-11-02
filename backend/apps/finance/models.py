"""
Finance & Accounting models
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel, TimeStampedModel
from decimal import Decimal


class GeneralLedger(BaseModel):
    """Chart of Accounts - General Ledger"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_accounts'
    )
    
    is_active = models.BooleanField(default=True)
    is_header = models.BooleanField(default=False)  # Header accounts cannot have transactions
    
    # Currency
    currency = models.CharField(max_length=3, default='IDR')
    
    # Balance tracking
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'general_ledger'
        verbose_name = 'General Ledger Account'
        verbose_name_plural = 'General Ledger Accounts'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(BaseModel):
    """Journal entries for accounting transactions"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('reversed', 'Reversed'),
    ]
    
    entry_number = models.CharField(max_length=50, unique=True, db_index=True)
    entry_date = models.DateField(db_index=True)
    description = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Posted tracking
    posted_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_journal_entries'
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    
    # Reversal tracking
    reversed_entry = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reversing_entries'
    )
    reversed_at = models.DateTimeField(null=True, blank=True)
    
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'journal_entries'
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ['-entry_date', '-entry_number']
        indexes = [
            models.Index(fields=['entry_number']),
            models.Index(fields=['entry_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date}"


class JournalEntryLine(TimeStampedModel):
    """Journal entry line items (debit/credit)"""
    
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(
        GeneralLedger,
        on_delete=models.PROTECT,
        related_name='journal_lines'
    )
    
    description = models.CharField(max_length=500)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # References
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_lines'
    )
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_lines'
    )
    
    class Meta:
        db_table = 'journal_entry_lines'
        verbose_name = 'Journal Entry Line'
        verbose_name_plural = 'Journal Entry Lines'
        ordering = ['journal_entry', 'id']
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.code}"


class Invoice(BaseModel):
    """Sales invoices"""
    
    TYPE_CHOICES = [
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('proforma', 'Proforma Invoice'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField()
    
    # Client
    client = models.ForeignKey(
        'crm.Client',
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    
    # Project reference
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    currency = models.CharField(max_length=3, default='IDR')
    
    # Tax
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_number = models.CharField(max_length=100, blank=True)  # Nomor Faktur Pajak
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Payment terms
    payment_terms = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    # Documents
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-invoice_date', '-invoice_number']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['client']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


class InvoiceLine(TimeStampedModel):
    """Invoice line items"""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # GL account mapping
    account = models.ForeignKey(
        GeneralLedger,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_lines'
    )
    
    # Display order
    line_number = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'invoice_lines'
        verbose_name = 'Invoice Line'
        verbose_name_plural = 'Invoice Lines'
        ordering = ['invoice', 'line_number']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - Line {self.line_number}"


class Payment(BaseModel):
    """Payment transactions"""
    
    TYPE_CHOICES = [
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
    ]
    
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    payment_date = models.DateField(db_index=True)
    
    # Party
    client = models.ForeignKey(
        'crm.Client',
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True
    )
    
    # Invoice reference
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Amount
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # GL account
    account = models.ForeignKey(
        GeneralLedger,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    notes = models.TextField(blank=True)
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"


class Expense(BaseModel):
    """Company expenses"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    CATEGORY_CHOICES = [
        ('operational', 'Operational'),
        ('travel', 'Travel'),
        ('office', 'Office Supplies'),
        ('utilities', 'Utilities'),
        ('salaries', 'Salaries'),
        ('marketing', 'Marketing'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    expense_number = models.CharField(max_length=50, unique=True, db_index=True)
    expense_date = models.DateField(db_index=True)
    
    # Requester
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    
    # Details
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Project/Department allocation
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    
    # GL account
    account = models.ForeignKey(
        GeneralLedger,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    
    # Status & Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Payment
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Attachments (receipts, etc.)
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_number']),
            models.Index(fields=['expense_date']),
            models.Index(fields=['status']),
            models.Index(fields=['employee']),
        ]
    
    def __str__(self):
        return f"{self.expense_number} - {self.description[:50]}"


class Budget(BaseModel):
    """Budget planning and tracking"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Period
    fiscal_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Department/Project
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='budgets'
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='budgets'
    )
    
    # Amounts
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_committed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    currency = models.CharField(max_length=3, default='IDR')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Approval
    approved_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_budgets'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'budgets'
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-fiscal_year', 'name']
        indexes = [
            models.Index(fields=['fiscal_year']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} - FY{self.fiscal_year}"


class BudgetLine(TimeStampedModel):
    """Budget line items by account"""
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(
        GeneralLedger,
        on_delete=models.PROTECT,
        related_name='budget_lines'
    )
    
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    committed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'budget_lines'
        verbose_name = 'Budget Line'
        verbose_name_plural = 'Budget Lines'
        unique_together = [['budget', 'account']]
        ordering = ['budget', 'account']
    
    def __str__(self):
        return f"{self.budget.name} - {self.account.code}"
    
    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount - self.committed_amount


class Tax(BaseModel):
    """Tax management (PPH & PPN)"""
    
    TAX_TYPE_CHOICES = [
        ('pph21', 'PPH 21 - Income Tax'),
        ('pph23', 'PPH 23 - Service Tax'),
        ('pph25', 'PPH 25 - Corporate Income Tax'),
        ('ppn', 'PPN - VAT'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('calculated', 'Calculated'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
    ]
    
    tax_number = models.CharField(max_length=50, unique=True, db_index=True)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES)
    tax_period_month = models.IntegerField()
    tax_period_year = models.IntegerField()
    
    # Amount
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='calculated')
    
    # Filing
    filing_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Documents
    tax_report = models.FileField(upload_to='taxes/reports/', null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'taxes'
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'
        ordering = ['-tax_period_year', '-tax_period_month']
        indexes = [
            models.Index(fields=['tax_number']),
            models.Index(fields=['tax_type']),
            models.Index(fields=['tax_period_year', 'tax_period_month']),
        ]
    
    def __str__(self):
        return f"{self.tax_number} - {self.get_tax_type_display()}"
