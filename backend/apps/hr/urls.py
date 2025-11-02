"""
HR & Talent Management URLs
"""
from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.HRDashboardView.as_view(), name='dashboard'),
    
    # Department
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    
    # Position
    path('positions/', views.PositionListView.as_view(), name='position_list'),
    path('positions/<uuid:pk>/', views.PositionDetailView.as_view(), name='position_detail'),
    
    # Employee
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    
    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/<uuid:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    
    # Leave
    path('leaves/', views.LeaveListView.as_view(), name='leave_list'),
    path('leaves/<uuid:pk>/', views.LeaveDetailView.as_view(), name='leave_detail'),
    path('leaves/<uuid:pk>/approval/', views.LeaveApprovalView.as_view(), name='leave_approval'),
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),
    
    # Payroll
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/<uuid:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    
    # Performance Review
    path('performance-reviews/', views.PerformanceReviewListView.as_view(), name='performance_review_list'),
    path('performance-reviews/<uuid:pk>/', views.PerformanceReviewDetailView.as_view(), name='performance_review_detail'),
]
