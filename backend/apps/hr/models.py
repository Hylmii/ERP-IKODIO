"""
HR & Talent Management models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, TimeStampedModel
from decimal import Decimal


class Employee(BaseModel):
    """Employee master data"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('probation', 'Probation'),
        ('intern', 'Intern'),
        ('freelance', 'Freelance'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    # Link to user account
    user = models.OneToOneField(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    
    # Personal Information
    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    nationality = models.CharField(max_length=100, default='Indonesian')
    
    # Identity Documents
    id_card_number = models.CharField(max_length=50, unique=True)  # KTP
    tax_id = models.CharField(max_length=50, unique=True, blank=True)  # NPWP
    passport_number = models.CharField(max_length=50, blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    join_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    resign_date = models.DateField(null=True, blank=True)
    
    # Organization
    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    reporting_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    
    # Salary Information
    base_salary = models.DecimalField(max_digits=15, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=50)
    bank_account_holder = models.CharField(max_length=200)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_relationship = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    
    # Profile
    photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Department(BaseModel):
    """Company departments/divisions"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    head = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Position(BaseModel):
    """Job positions/titles"""
    
    LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('c_level', 'C-Level'),
    ]
    
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    min_salary = models.DecimalField(max_digits=15, decimal_places=2)
    max_salary = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'positions'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Attendance(TimeStampedModel):
    """Daily attendance records"""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('leave', 'On Leave'),
        ('holiday', 'Holiday'),
        ('sick', 'Sick'),
        ('remote', 'Remote Work'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Clock in/out
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    clock_in_location = models.CharField(max_length=500, blank=True)
    clock_out_location = models.CharField(max_length=500, blank=True)
    
    # Working hours
    working_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendances'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendances'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = [['employee', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date}"


class Leave(BaseModel):
    """Leave/time-off requests"""
    
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('emergency', 'Emergency Leave'),
        ('compensatory', 'Compensatory Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField()
    attachment = models.FileField(upload_to='leaves/attachments/', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leaves'
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.start_date})"


class LeaveBalance(BaseModel):
    """Employee leave balance tracking"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    year = models.IntegerField()
    annual_quota = models.IntegerField(default=12)
    annual_used = models.IntegerField(default=0)
    sick_quota = models.IntegerField(default=12)
    sick_used = models.IntegerField(default=0)
    compensatory_quota = models.IntegerField(default=0)
    compensatory_used = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'leave_balances'
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'
        unique_together = [['employee', 'year']]
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.year}"
    
    @property
    def annual_remaining(self):
        return self.annual_quota - self.annual_used
    
    @property
    def sick_remaining(self):
        return self.sick_quota - self.sick_used


class Payroll(BaseModel):
    """Monthly payroll records"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    period_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    period_year = models.IntegerField()
    
    # Earnings
    basic_salary = models.DecimalField(max_digits=15, decimal_places=2)
    allowances = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Deductions
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pension = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Totals
    gross_salary = models.DecimalField(max_digits=15, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2)
    net_salary = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Working days
    working_days = models.IntegerField()
    present_days = models.IntegerField()
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    calculated_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    payslip_file = models.FileField(upload_to='payrolls/payslips/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payrolls'
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        unique_together = [['employee', 'period_month', 'period_year']]
        ordering = ['-period_year', '-period_month']
        indexes = [
            models.Index(fields=['employee', 'period_year', 'period_month']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.period_month}/{self.period_year}"


class PerformanceReview(BaseModel):
    """Employee performance reviews/KPIs"""
    
    REVIEW_TYPE_CHOICES = [
        ('probation', 'Probation Review'),
        ('quarterly', 'Quarterly Review'),
        ('annual', 'Annual Review'),
        ('project', 'Project Review'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    reviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_reviews'
    )
    
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    review_date = models.DateField()
    
    # Ratings (1-5 scale)
    technical_skills = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    teamwork = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    leadership = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    productivity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    quality_of_work = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    attendance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Overall
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)
    
    # Comments
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals = models.TextField()
    reviewer_comments = models.TextField()
    employee_comments = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'performance_reviews'
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'
        ordering = ['-review_date']
        indexes = [
            models.Index(fields=['employee', 'review_type']),
            models.Index(fields=['review_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.review_type} ({self.review_date})"
