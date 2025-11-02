"""
HR Admin
"""
from django.contrib import admin
from .models import (
    Employee, Department, Position, Attendance, Leave, LeaveBalance,
    Payroll, PerformanceReview
)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'department', 'position', 'employment_status')
    list_filter = ('employment_status', 'employment_type', 'department', 'gender')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'head', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'level', 'is_active')
    list_filter = ('level', 'department', 'is_active')
    search_fields = ('code', 'title')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'clock_in', 'clock_out', 'working_hours')
    list_filter = ('status', 'date', 'is_approved')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    date_hierarchy = 'date'


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_date'


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'year', 'annual_remaining', 'sick_remaining')
    list_filter = ('year',)
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period_month', 'period_year', 'gross_salary', 'net_salary', 'status')
    list_filter = ('status', 'period_year', 'period_month')
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'review_type', 'review_date', 'overall_rating', 'status')
    list_filter = ('review_type', 'status', 'review_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'review_date'
