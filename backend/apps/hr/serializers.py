"""
HR & Talent Management Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Department, Position, Employee, Attendance, Leave, 
    LeaveBalance, Payroll, PerformanceReview
)

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer"""
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'head', 'head_name',
            'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()


class PositionSerializer(serializers.ModelSerializer):
    """Position serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'code', 'title', 'description', 'department', 'department_name',
            'level', 'min_salary', 'max_salary', 'employee_count', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight employee serializer for list view"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'user_email', 
            'department_name', 'position_title', 'employment_status',
            'join_date', 'photo'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class EmployeeSerializer(serializers.ModelSerializer):
    """Detailed employee serializer"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    manager_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_email', 'employee_id', 'first_name', 'last_name',
            'full_name', 'email', 'phone', 'mobile', 'photo',
            'date_of_birth', 'gender', 'marital_status', 'nationality',
            'id_number', 'tax_id', 'address', 'city', 'state', 'postal_code', 'country',
            'department', 'department_name', 'position', 'position_title',
            'manager', 'manager_name', 'join_date', 'contract_start', 'contract_end',
            'employment_type', 'employment_status', 'work_location',
            'salary', 'bank_name', 'bank_account', 'bpjs_kesehatan',
            'bpjs_ketenagakerjaan', 'npwp', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'salary': {'write_only': True},
            'bank_account': {'write_only': True},
        }
    
    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AttendanceSerializer(serializers.ModelSerializer):
    """Attendance serializer"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_id', 'employee_name', 'date',
            'check_in', 'check_in_location', 'check_in_ip',
            'check_out', 'check_out_location', 'check_out_ip',
            'duration', 'work_hours', 'overtime_hours', 'status',
            'attendance_type', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_duration(self, obj):
        if obj.check_in and obj.check_out:
            delta = obj.check_out - obj.check_in
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return None


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Leave balance serializer"""
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'employee_name', 'year', 'leave_type',
            'total_days', 'used_days', 'remaining_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'remaining_days', 'created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"


class LeaveSerializer(serializers.ModelSerializer):
    """Leave request serializer"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approver_name = serializers.SerializerMethodField()
    total_days = serializers.SerializerMethodField()
    
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_id', 'employee_name',
            'leave_type', 'start_date', 'end_date', 'total_days',
            'reason', 'status', 'approver', 'approver_name',
            'approval_date', 'approval_notes', 'attachment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_approver_name(self, obj):
        if obj.approver:
            return f"{obj.approver.first_name} {obj.approver.last_name}"
        return None
    
    def get_total_days(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return delta.days + 1
        return 0


class PayrollSerializer(serializers.ModelSerializer):
    """Payroll serializer"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    net_salary = serializers.SerializerMethodField()
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_id', 'employee_name',
            'period_year', 'period_month', 'basic_salary',
            'allowances', 'overtime_pay', 'bonuses',
            'deductions', 'tax', 'bpjs_health', 'bpjs_employment',
            'net_salary', 'payment_date', 'payment_method',
            'payment_status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_net_salary(self, obj):
        gross = (
            obj.basic_salary + 
            obj.allowances + 
            obj.overtime_pay + 
            obj.bonuses
        )
        total_deductions = (
            obj.deductions + 
            obj.tax + 
            obj.bpjs_health + 
            obj.bpjs_employment
        )
        return gross - total_deductions


class PerformanceReviewSerializer(serializers.ModelSerializer):
    """Performance review serializer"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'employee', 'employee_id', 'employee_name',
            'reviewer', 'reviewer_name', 'review_period_start',
            'review_period_end', 'review_date', 'review_type',
            'kpi_score', 'competency_score', 'overall_score',
            'strengths', 'areas_for_improvement', 'goals',
            'comments', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return f"{obj.reviewer.first_name} {obj.reviewer.last_name}"
        return None
