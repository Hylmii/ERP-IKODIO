"""
Business Intelligence & Analytics models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, TimeStampedModel


class Dashboard(BaseModel):
    """Custom dashboards"""
    
    DASHBOARD_TYPE_CHOICES = [
        ('executive', 'Executive Dashboard'),
        ('sales', 'Sales Dashboard'),
        ('hr', 'HR Dashboard'),
        ('project', 'Project Dashboard'),
        ('finance', 'Finance Dashboard'),
        ('operations', 'Operations Dashboard'),
        ('custom', 'Custom Dashboard'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dashboard_type = models.CharField(max_length=50, choices=DASHBOARD_TYPE_CHOICES)
    
    # Owner
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_dashboards'
    )
    
    # Access control
    is_public = models.BooleanField(default=False)
    shared_with_departments = models.ManyToManyField(
        'hr.Department',
        blank=True,
        related_name='shared_dashboards'
    )
    shared_with_employees = models.ManyToManyField(
        'hr.Employee',
        blank=True,
        related_name='shared_dashboards'
    )
    
    # Layout configuration (JSON)
    layout_config = models.JSONField(null=True, blank=True)
    
    # Refresh settings
    auto_refresh = models.BooleanField(default=False)
    refresh_interval_minutes = models.IntegerField(default=5)
    
    # Display order
    display_order = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dashboards'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['dashboard_type']),
        ]
    
    def __str__(self):
        return self.name


class Widget(BaseModel):
    """Dashboard widgets"""
    
    WIDGET_TYPE_CHOICES = [
        ('kpi_card', 'KPI Card'),
        ('line_chart', 'Line Chart'),
        ('bar_chart', 'Bar Chart'),
        ('pie_chart', 'Pie Chart'),
        ('table', 'Data Table'),
        ('gauge', 'Gauge'),
        ('progress', 'Progress Bar'),
        ('list', 'List'),
        ('map', 'Map'),
    ]
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPE_CHOICES)
    
    # Data source configuration
    data_source = models.CharField(max_length=100)  # e.g., 'projects', 'employees', 'sales'
    query_config = models.JSONField(null=True, blank=True)  # Filters, aggregations, etc.
    
    # Display configuration
    display_config = models.JSONField(null=True, blank=True)  # Colors, size, etc.
    
    # Position & Size
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    
    # Refresh
    auto_refresh = models.BooleanField(default=True)
    refresh_interval_minutes = models.IntegerField(default=5)
    
    # Display order
    display_order = models.IntegerField(default=0)
    
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'widgets'
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
        ordering = ['dashboard', 'display_order']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class Report(BaseModel):
    """Custom reports"""
    
    REPORT_TYPE_CHOICES = [
        ('project_status', 'Project Status Report'),
        ('financial', 'Financial Report'),
        ('hr_metrics', 'HR Metrics Report'),
        ('sales_pipeline', 'Sales Pipeline Report'),
        ('timesheet', 'Timesheet Report'),
        ('expense', 'Expense Report'),
        ('asset_inventory', 'Asset Inventory Report'),
        ('ticket_summary', 'Ticket Summary Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    
    # Owner
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_reports'
    )
    
    # Query configuration
    data_source = models.CharField(max_length=100)
    query_config = models.JSONField(null=True, blank=True)
    
    # Report template
    template_config = models.JSONField(null=True, blank=True)
    
    # Columns/fields to include
    columns_config = models.JSONField(null=True, blank=True)
    
    # Filters
    filters_config = models.JSONField(null=True, blank=True)
    
    # Grouping & Sorting
    grouping_config = models.JSONField(null=True, blank=True)
    sorting_config = models.JSONField(null=True, blank=True)
    
    # Default format
    default_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)  # Cron expression
    
    # Recipients for scheduled reports
    email_recipients = models.JSONField(null=True, blank=True)  # List of emails
    
    # Access control
    is_public = models.BooleanField(default=False)
    
    # Usage tracking
    run_count = models.IntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['report_type']),
        ]
    
    def __str__(self):
        return self.name


class ReportExecution(TimeStampedModel):
    """Report execution history"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    executed_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='report_executions'
    )
    
    # Parameters used
    parameters = models.JSONField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    
    # Execution timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Output
    output_format = models.CharField(max_length=10)
    output_file = models.FileField(upload_to='reports/output/', null=True, blank=True)
    output_size_bytes = models.BigIntegerField(null=True, blank=True)
    
    # Row count
    row_count = models.IntegerField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'report_executions'
        verbose_name = 'Report Execution'
        verbose_name_plural = 'Report Executions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['report', 'status']),
            models.Index(fields=['executed_by']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.started_at}"


class KPI(BaseModel):
    """Key Performance Indicators"""
    
    KPI_TYPE_CHOICES = [
        ('revenue', 'Revenue'),
        ('profit', 'Profit'),
        ('project_completion', 'Project Completion Rate'),
        ('client_satisfaction', 'Client Satisfaction'),
        ('employee_utilization', 'Employee Utilization'),
        ('sales_conversion', 'Sales Conversion Rate'),
        ('ticket_resolution', 'Ticket Resolution Time'),
        ('custom', 'Custom KPI'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    kpi_type = models.CharField(max_length=50, choices=KPI_TYPE_CHOICES)
    
    # Owner
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='owned_kpis'
    )
    
    # Department/Project scope
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpis'
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpis'
    )
    
    # Calculation
    calculation_method = models.TextField()  # Description of how to calculate
    data_source = models.CharField(max_length=100)
    query_config = models.JSONField(null=True, blank=True)
    
    # Target values
    target_value = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Thresholds for status
    threshold_red = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    threshold_yellow = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    threshold_green = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Unit
    unit = models.CharField(max_length=20, blank=True)  # %, IDR, hours, etc.
    
    # Frequency
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Period
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    
    # Last update
    last_calculated_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'kpis'
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
        ordering = ['name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['kpi_type']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return self.name


class KPIValue(TimeStampedModel):
    """KPI historical values"""
    
    kpi = models.ForeignKey(
        KPI,
        on_delete=models.CASCADE,
        related_name='values'
    )
    
    period_date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Comparison with target
    target_value = models.DecimalField(max_digits=15, decimal_places=2)
    variance = models.DecimalField(max_digits=15, decimal_places=2)
    variance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Status based on thresholds
    status = models.CharField(max_length=20)  # 'red', 'yellow', 'green'
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'kpi_values'
        verbose_name = 'KPI Value'
        verbose_name_plural = 'KPI Values'
        ordering = ['-period_date']
        unique_together = [['kpi', 'period_date']]
        indexes = [
            models.Index(fields=['kpi', 'period_date']),
        ]
    
    def __str__(self):
        return f"{self.kpi.name} - {self.period_date}: {self.value}"


class DataExport(TimeStampedModel):
    """Data export history"""
    
    EXPORT_TYPE_CHOICES = [
        ('employees', 'Employees'),
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('invoices', 'Invoices'),
        ('expenses', 'Expenses'),
        ('clients', 'Clients'),
        ('tickets', 'Tickets'),
        ('assets', 'Assets'),
        ('custom', 'Custom Export'),
    ]
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    export_type = models.CharField(max_length=50, choices=EXPORT_TYPE_CHOICES)
    export_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    
    # User who requested export
    requested_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_exports'
    )
    
    # Filters applied
    filters = models.JSONField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    # Output
    output_file = models.FileField(upload_to='exports/', null=True, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Expiry (auto-delete old exports)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'data_exports'
        verbose_name = 'Data Export'
        verbose_name_plural = 'Data Exports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requested_by']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.export_type} Export - {self.created_at}"


class SavedFilter(BaseModel):
    """Saved filters for quick access"""
    
    FILTER_TYPE_CHOICES = [
        ('employees', 'Employees'),
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('clients', 'Clients'),
        ('invoices', 'Invoices'),
        ('tickets', 'Tickets'),
        ('assets', 'Assets'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    filter_type = models.CharField(max_length=50, choices=FILTER_TYPE_CHOICES)
    
    # Owner
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='saved_filters'
    )
    
    # Filter configuration
    filter_config = models.JSONField()
    
    # Sharing
    is_public = models.BooleanField(default=False)
    
    # Usage
    usage_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'saved_filters'
        verbose_name = 'Saved Filter'
        verbose_name_plural = 'Saved Filters'
        ordering = ['name']
    
    def __str__(self):
        return self.name
