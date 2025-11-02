"""
Project Management System models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel, TimeStampedModel
from decimal import Decimal


class Project(BaseModel):
    """Project master data"""
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Client/Customer
    client = models.ForeignKey(
        'crm.Client',
        on_delete=models.PROTECT,
        related_name='projects'
    )
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Budget & Financials
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='IDR')
    
    # Progress
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Team
    project_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.PROTECT,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(
        'hr.Employee',
        through='ProjectTeamMember',
        related_name='assigned_projects'
    )
    
    # Contract & Documents
    contract_document = models.FileField(upload_to='projects/contracts/', null=True, blank=True)
    
    # Tags & Categories
    tags = models.CharField(max_length=500, blank=True)  # Comma-separated tags
    category = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['project_manager']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectTeamMember(TimeStampedModel):
    """Project team member assignments with roles"""
    
    ROLE_CHOICES = [
        ('project_manager', 'Project Manager'),
        ('tech_lead', 'Tech Lead'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('qa', 'QA Engineer'),
        ('analyst', 'Business Analyst'),
        ('member', 'Team Member'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='team_assignments'
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    allocation_percentage = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'project_team_members'
        verbose_name = 'Project Team Member'
        verbose_name_plural = 'Project Team Members'
        unique_together = [['project', 'employee']]
        ordering = ['project', 'employee']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.project.name} ({self.role})"


class Task(BaseModel):
    """Project tasks/work items"""
    
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('testing', 'Testing'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic Information
    task_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Project & Sprint
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    sprint = models.ForeignKey(
        'Sprint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subtasks'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Estimation & Tracking
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Additional fields
    story_points = models.IntegerField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    attachments = models.JSONField(null=True, blank=True)  # Store file paths/URLs
    
    # Order for kanban board
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['task_number']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.task_number} - {self.title}"


class Sprint(BaseModel):
    """Agile sprint/iteration"""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='sprints'
    )
    name = models.CharField(max_length=100)
    goal = models.TextField()
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Sprint metrics
    planned_story_points = models.IntegerField(default=0)
    completed_story_points = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sprints'
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['project', 'status']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.name}"


class Timesheet(BaseModel):
    """Time tracking for tasks"""
    
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='timesheets'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='timesheets'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='timesheets'
    )
    
    date = models.DateField(db_index=True)
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    
    # Billable tracking
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timesheets'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'timesheets'
        verbose_name = 'Timesheet'
        verbose_name_plural = 'Timesheets'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['project', 'date']),
            models.Index(fields=['task']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.task.task_number} ({self.date})"


class ProjectMilestone(BaseModel):
    """Project milestones/deliverables"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Deliverables
    deliverables = models.TextField(blank=True)
    payment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Order
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'project_milestones'
        verbose_name = 'Project Milestone'
        verbose_name_plural = 'Project Milestones'
        ordering = ['project', 'display_order']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.name}"


class TaskComment(TimeStampedModel):
    """Comments on tasks"""
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    comment = models.TextField()
    attachments = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.task.task_number} - Comment by {self.author.get_full_name()}"


class ProjectRisk(BaseModel):
    """Project risk management"""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('analyzing', 'Analyzing'),
        ('mitigating', 'Mitigating'),
        ('resolved', 'Resolved'),
        ('occurred', 'Occurred'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='risks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    probability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    mitigation_plan = models.TextField()
    contingency_plan = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    
    owner = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_risks'
    )
    
    identified_date = models.DateField()
    resolved_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'project_risks'
        verbose_name = 'Project Risk'
        verbose_name_plural = 'Project Risks'
        ordering = ['-severity', '-probability']
        indexes = [
            models.Index(fields=['project', 'status']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.title}"
