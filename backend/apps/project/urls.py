"""
Project Management URLs
"""
from django.urls import path
from apps.project import views

app_name = 'project'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.project_dashboard, name='project-dashboard'),
    
    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Project Team Members
    path('team-members/', views.ProjectTeamMemberListView.as_view(), name='team-member-list'),
    path('team-members/<int:pk>/', views.ProjectTeamMemberDetailView.as_view(), name='team-member-detail'),
    
    # Tasks
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/move/', views.task_move, name='task-move'),
    
    # Sprints
    path('sprints/', views.SprintListView.as_view(), name='sprint-list'),
    path('sprints/<int:pk>/', views.SprintDetailView.as_view(), name='sprint-detail'),
    
    # Timesheets
    path('timesheets/', views.TimesheetListView.as_view(), name='timesheet-list'),
    path('timesheets/<int:pk>/', views.TimesheetDetailView.as_view(), name='timesheet-detail'),
    path('timesheets/<int:pk>/approve/', views.timesheet_approve, name='timesheet-approve'),
    
    # Milestones
    path('milestones/', views.ProjectMilestoneListView.as_view(), name='milestone-list'),
    path('milestones/<int:pk>/', views.ProjectMilestoneDetailView.as_view(), name='milestone-detail'),
    
    # Task Comments
    path('comments/', views.TaskCommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.TaskCommentDetailView.as_view(), name='comment-detail'),
    
    # Project Risks
    path('risks/', views.ProjectRiskListView.as_view(), name='risk-list'),
    path('risks/<int:pk>/', views.ProjectRiskDetailView.as_view(), name='risk-detail'),
]
