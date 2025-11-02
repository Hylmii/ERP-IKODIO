"""
Views for Project Management System
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from apps.project.models import (
    Project, ProjectTeamMember, Task, Sprint,
    Timesheet, ProjectMilestone, TaskComment, ProjectRisk
)
from apps.project.serializers import (
    ProjectSerializer, ProjectListSerializer,
    ProjectTeamMemberSerializer, TaskSerializer, TaskListSerializer,
    SprintSerializer, TimesheetSerializer, ProjectMilestoneSerializer,
    TaskCommentSerializer, ProjectRiskSerializer
)
from apps.authentication.permissions import IsAdminOrReadOnly


# ===== PROJECT VIEWS =====

class ProjectListView(generics.ListCreateAPIView):
    """List all projects or create new project"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'client', 'project_manager']
    search_fields = ['code', 'name', 'description', 'tags']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'progress_percentage']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Project.objects.filter(deleted_at__isnull=True).select_related(
            'client', 'project_manager'
        )
        
        # Non-admin users see only their assigned projects
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project_manager__user=user) | Q(team_members__user=user)
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        queryset = Project.objects.filter(deleted_at__isnull=True).select_related(
            'client', 'project_manager'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project_manager__user=user) | Q(team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


# ===== PROJECT TEAM MEMBER VIEWS =====

class ProjectTeamMemberListView(generics.ListCreateAPIView):
    """List all project team members or add new member"""
    serializer_class = ProjectTeamMemberSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'employee', 'role', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering_fields = ['start_date', 'allocation_percentage']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = ProjectTeamMember.objects.all().select_related('project', 'employee')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(employee__user=user)
            )
        
        return queryset


class ProjectTeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project team member"""
    serializer_class = ProjectTeamMemberSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = ProjectTeamMember.objects.all().select_related('project', 'employee')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(employee__user=user)
            )
        
        return queryset


# ===== TASK VIEWS =====

class TaskListView(generics.ListCreateAPIView):
    """List all tasks or create new task (Kanban)"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'sprint', 'status', 'priority', 'assigned_to', 'parent_task']
    search_fields = ['task_number', 'title', 'description', 'tags']
    ordering_fields = ['created_at', 'due_date', 'priority', 'display_order']
    ordering = ['display_order', '-created_at']
    
    def get_queryset(self):
        queryset = Task.objects.filter(deleted_at__isnull=True).select_related(
            'project', 'sprint', 'assigned_to', 'parent_task'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | 
                Q(project__team_members__user=user) |
                Q(assigned_to__user=user)
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a task"""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        queryset = Task.objects.filter(deleted_at__isnull=True).select_related(
            'project', 'sprint', 'assigned_to', 'parent_task'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | 
                Q(project__team_members__user=user) |
                Q(assigned_to__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def task_move(request, pk):
    """Move task to different status/sprint (for kanban drag & drop)"""
    try:
        task = Task.objects.get(pk=pk, deleted_at__isnull=True)
        
        # Check permission
        user = request.user
        if not user.is_staff:
            if not (task.project.project_manager.user == user or 
                    task.project.team_members.filter(user=user).exists() or
                    task.assigned_to and task.assigned_to.user == user):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update status and/or sprint
        if 'status' in request.data:
            task.status = request.data['status']
        if 'sprint' in request.data:
            task.sprint_id = request.data['sprint']
        if 'display_order' in request.data:
            task.display_order = request.data['display_order']
        
        task.updated_by = user
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


# ===== SPRINT VIEWS =====

class SprintListView(generics.ListCreateAPIView):
    """List all sprints or create new sprint"""
    serializer_class = SprintSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'status']
    search_fields = ['name', 'goal']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = Sprint.objects.filter(deleted_at__isnull=True).select_related('project')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a sprint"""
    serializer_class = SprintSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Sprint.objects.filter(deleted_at__isnull=True).select_related('project')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


# ===== TIMESHEET VIEWS =====

class TimesheetListView(generics.ListCreateAPIView):
    """List all timesheets or create new timesheet"""
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'project', 'task', 'is_billable', 'is_approved']
    search_fields = ['description']
    ordering_fields = ['date', 'hours']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Timesheet.objects.filter(deleted_at__isnull=True).select_related(
            'employee', 'project', 'task', 'approved_by'
        )
        
        user = self.request.user
        if not user.is_staff:
            # Users can see their own timesheets and timesheets of their projects
            queryset = queryset.filter(
                Q(employee__user=user) | 
                Q(project__project_manager__user=user) |
                Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TimesheetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a timesheet"""
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Timesheet.objects.filter(deleted_at__isnull=True).select_related(
            'employee', 'project', 'task', 'approved_by'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(employee__user=user) | 
                Q(project__project_manager__user=user) |
                Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def timesheet_approve(request, pk):
    """Approve or reject timesheet"""
    try:
        timesheet = Timesheet.objects.get(pk=pk, deleted_at__isnull=True)
        
        # Only project managers can approve timesheets
        user = request.user
        if not (user.is_staff or timesheet.project.project_manager.user == user):
            return Response({'error': 'Only project managers can approve timesheets'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action == 'approve':
            timesheet.is_approved = True
            timesheet.approved_by = timesheet.project.project_manager
            timesheet.approved_at = timezone.now()
            timesheet.save()
            
            # Update task actual hours
            task = timesheet.task
            total_hours = task.timesheets.filter(
                deleted_at__isnull=True,
                is_approved=True
            ).aggregate(total=Sum('hours'))['total'] or 0
            task.actual_hours = total_hours
            task.save()
            
            return Response({'message': 'Timesheet approved successfully'})
        elif action == 'reject':
            timesheet.is_approved = False
            timesheet.approved_by = None
            timesheet.approved_at = None
            timesheet.save()
            return Response({'message': 'Timesheet rejected'})
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Timesheet.DoesNotExist:
        return Response({'error': 'Timesheet not found'}, status=status.HTTP_404_NOT_FOUND)


# ===== PROJECT MILESTONE VIEWS =====

class ProjectMilestoneListView(generics.ListCreateAPIView):
    """List all milestones or create new milestone"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['due_date', 'display_order']
    ordering = ['display_order']
    
    def get_queryset(self):
        queryset = ProjectMilestone.objects.filter(deleted_at__isnull=True).select_related('project')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectMilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a milestone"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = ProjectMilestone.objects.filter(deleted_at__isnull=True).select_related('project')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


# ===== TASK COMMENT VIEWS =====

class TaskCommentListView(generics.ListCreateAPIView):
    """List all comments or create new comment"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['task', 'author']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        queryset = TaskComment.objects.all().select_related('task', 'author')
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(task__project__project_manager__user=user) | 
                Q(task__project__team_members__user=user) |
                Q(task__assigned_to__user=user)
            ).distinct()
        
        return queryset


class TaskCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a comment"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TaskComment.objects.all().select_related('task', 'author')
        
        user = self.request.user
        if not user.is_staff:
            # Users can only edit/delete their own comments
            queryset = queryset.filter(author__user=user)
        
        return queryset


# ===== PROJECT RISK VIEWS =====

class ProjectRiskListView(generics.ListCreateAPIView):
    """List all risks or create new risk"""
    serializer_class = ProjectRiskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'severity', 'status', 'owner']
    search_fields = ['title', 'description']
    ordering_fields = ['severity', 'probability', 'impact', 'identified_date']
    ordering = ['-severity', '-probability']
    
    def get_queryset(self):
        queryset = ProjectRisk.objects.filter(deleted_at__isnull=True).select_related(
            'project', 'owner'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectRiskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a risk"""
    serializer_class = ProjectRiskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = ProjectRisk.objects.filter(deleted_at__isnull=True).select_related(
            'project', 'owner'
        )
        
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(project__project_manager__user=user) | Q(project__team_members__user=user)
            ).distinct()
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()


# ===== PROJECT DASHBOARD =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_dashboard(request):
    """Get project management dashboard metrics"""
    user = request.user
    
    # Base querysets
    if user.is_staff:
        projects = Project.objects.filter(deleted_at__isnull=True)
        tasks = Task.objects.filter(deleted_at__isnull=True)
        timesheets = Timesheet.objects.filter(deleted_at__isnull=True)
    else:
        projects = Project.objects.filter(
            Q(project_manager__user=user) | Q(team_members__user=user),
            deleted_at__isnull=True
        ).distinct()
        tasks = Task.objects.filter(
            Q(project__project_manager__user=user) | 
            Q(project__team_members__user=user) |
            Q(assigned_to__user=user),
            deleted_at__isnull=True
        ).distinct()
        timesheets = Timesheet.objects.filter(
            Q(employee__user=user) | 
            Q(project__project_manager__user=user) |
            Q(project__team_members__user=user),
            deleted_at__isnull=True
        ).distinct()
    
    # Project metrics
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    delayed_projects = projects.filter(
        status__in=['active', 'on_hold'],
        end_date__lt=timezone.now().date()
    ).count()
    
    # Task metrics
    total_tasks = tasks.count()
    tasks_by_status = {
        'backlog': tasks.filter(status='backlog').count(),
        'todo': tasks.filter(status='todo').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'review': tasks.filter(status='review').count(),
        'testing': tasks.filter(status='testing').count(),
        'done': tasks.filter(status='done').count(),
        'blocked': tasks.filter(status='blocked').count(),
    }
    overdue_tasks = tasks.filter(
        status__in=['backlog', 'todo', 'in_progress', 'review', 'testing'],
        due_date__lt=timezone.now().date()
    ).count()
    
    # My tasks (for non-admin)
    my_tasks = 0
    if not user.is_staff:
        try:
            employee = user.employee
            my_tasks = tasks.filter(assigned_to=employee).count()
        except:
            pass
    
    # Timesheet metrics
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    hours_this_week = timesheets.filter(
        date__range=[week_start, week_end]
    ).aggregate(total=Sum('hours'))['total'] or 0
    
    pending_approval = timesheets.filter(is_approved=False).count()
    
    # Budget metrics
    budget_data = projects.aggregate(
        total_budget=Sum('estimated_budget'),
        total_cost=Sum('actual_cost'),
        total_contract=Sum('contract_value')
    )
    
    # Project by status
    projects_by_status = {
        'planning': projects.filter(status='planning').count(),
        'active': projects.filter(status='active').count(),
        'on_hold': projects.filter(status='on_hold').count(),
        'completed': projects.filter(status='completed').count(),
        'cancelled': projects.filter(status='cancelled').count(),
    }
    
    # Recent activities
    recent_tasks = tasks.order_by('-updated_at')[:5].values(
        'id', 'task_number', 'title', 'status', 'priority', 'updated_at'
    )
    
    return Response({
        'projects': {
            'total': total_projects,
            'active': active_projects,
            'completed': completed_projects,
            'delayed': delayed_projects,
            'by_status': projects_by_status,
        },
        'tasks': {
            'total': total_tasks,
            'by_status': tasks_by_status,
            'overdue': overdue_tasks,
            'my_tasks': my_tasks,
        },
        'timesheets': {
            'hours_this_week': float(hours_this_week),
            'pending_approval': pending_approval,
        },
        'budget': {
            'total_budget': float(budget_data['total_budget'] or 0),
            'total_cost': float(budget_data['total_cost'] or 0),
            'total_contract': float(budget_data['total_contract'] or 0),
            'variance': float((budget_data['total_cost'] or 0) - (budget_data['total_budget'] or 0)),
        },
        'recent_activities': list(recent_tasks),
    })
