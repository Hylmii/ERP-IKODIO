"""
Serializers for Project Management System
"""
from rest_framework import serializers
from django.db import models
from apps.project.models import (
    Project, ProjectTeamMember, Task, Sprint,
    Timesheet, ProjectMilestone, TaskComment, ProjectRisk
)
from apps.hr.models import Employee
from apps.crm.models import Client


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    task_count = serializers.SerializerMethodField()
    team_size = serializers.SerializerMethodField()
    budget_variance = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'status', 'priority', 
            'client_name', 'project_manager_name',
            'start_date', 'end_date', 'progress_percentage',
            'estimated_budget', 'actual_cost', 'contract_value',
            'task_count', 'team_size', 'budget_variance',
            'created_at', 'updated_at'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.filter(deleted_at__isnull=True).count()
    
    def get_team_size(self, obj):
        return obj.team_assignments.filter(is_active=True).count()
    
    def get_budget_variance(self, obj):
        """Budget variance percentage"""
        if obj.estimated_budget > 0:
            variance = ((obj.actual_cost - obj.estimated_budget) / obj.estimated_budget) * 100
            return round(float(variance), 2)
        return 0


class ProjectSerializer(serializers.ModelSerializer):
    """Full project serializer"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    task_count = serializers.SerializerMethodField()
    team_members_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.filter(deleted_at__isnull=True).count()
    
    def get_team_members_list(self, obj):
        members = obj.team_assignments.filter(is_active=True).select_related('employee')
        return [{
            'id': m.employee.id,
            'name': m.employee.get_full_name(),
            'role': m.role,
            'allocation': m.allocation_percentage
        } for m in members]


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    """Project team member serializer"""
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectTeamMember
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists (kanban)"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True)
    parent_task_number = serializers.CharField(source='parent_task.task_number', read_only=True)
    subtask_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'task_number', 'title', 'status', 'priority',
            'project_name', 'assigned_to_name', 'sprint_name',
            'parent_task_number', 'start_date', 'due_date',
            'estimated_hours', 'actual_hours', 'progress_percentage',
            'story_points', 'display_order', 'subtask_count', 
            'comment_count', 'created_at', 'updated_at'
        ]
    
    def get_subtask_count(self, obj):
        return obj.subtasks.filter(deleted_at__isnull=True).count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True)
    parent_task_number = serializers.CharField(source='parent_task.task_number', read_only=True)
    subtasks_list = serializers.SerializerMethodField()
    time_logged = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_subtasks_list(self, obj):
        subtasks = obj.subtasks.filter(deleted_at__isnull=True)
        return [{
            'id': t.id,
            'task_number': t.task_number,
            'title': t.title,
            'status': t.status
        } for t in subtasks]
    
    def get_time_logged(self, obj):
        """Total approved time logged on this task"""
        total = obj.timesheets.filter(
            deleted_at__isnull=True,
            is_approved=True
        ).aggregate(total=models.Sum('hours'))['total']
        return float(total) if total else 0


class SprintSerializer(serializers.ModelSerializer):
    """Sprint serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    velocity = serializers.SerializerMethodField()
    
    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.filter(deleted_at__isnull=True).count()
    
    def get_completed_task_count(self, obj):
        return obj.tasks.filter(deleted_at__isnull=True, status='done').count()
    
    def get_velocity(self, obj):
        """Sprint velocity (completed story points / planned story points)"""
        if obj.planned_story_points > 0:
            return round((obj.completed_story_points / obj.planned_story_points) * 100, 2)
        return 0


class TimesheetSerializer(serializers.ModelSerializer):
    """Timesheet serializer"""
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    task_number = serializers.CharField(source='task.task_number', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    billable_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Timesheet
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_billable_amount(self, obj):
        """Calculate billable amount"""
        if obj.is_billable and obj.hourly_rate:
            return float(obj.hours * obj.hourly_rate)
        return 0


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """Project milestone serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    is_delayed = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMilestone
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_is_delayed(self, obj):
        """Check if milestone is delayed"""
        from django.utils import timezone
        if obj.status != 'completed' and obj.due_date < timezone.now().date():
            return True
        return False
    
    def get_days_until_due(self, obj):
        """Days until due date"""
        from django.utils import timezone
        if obj.status != 'completed':
            delta = obj.due_date - timezone.now().date()
            return delta.days
        return None


class TaskCommentSerializer(serializers.ModelSerializer):
    """Task comment serializer"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    task_number = serializers.CharField(source='task.task_number', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectRiskSerializer(serializers.ModelSerializer):
    """Project risk serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    risk_score = serializers.SerializerMethodField()
    days_open = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectRisk
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by', 'deleted_at', 'created_at', 'updated_at']
    
    def get_risk_score(self, obj):
        """Calculate risk score (probability * impact)"""
        return obj.probability * obj.impact
    
    def get_days_open(self, obj):
        """Days since identified"""
        from django.utils import timezone
        if obj.status != 'resolved':
            delta = timezone.now().date() - obj.identified_date
            return delta.days
        return None
