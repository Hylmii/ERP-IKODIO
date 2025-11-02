"""
HR & Talent Management Views
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum, Avg

from .models import (
    Department, Position, Employee, Attendance, Leave,
    LeaveBalance, Payroll, PerformanceReview
)
from .serializers import (
    DepartmentSerializer, PositionSerializer,
    EmployeeSerializer, EmployeeListSerializer,
    AttendanceSerializer, LeaveSerializer, LeaveBalanceSerializer,
    PayrollSerializer, PerformanceReviewSerializer
)
from apps.authentication.permissions import IsAdminOrReadOnly


# Department Views
class DepartmentListView(generics.ListCreateAPIView):
    """List all departments or create new department"""
    queryset = Department.objects.filter(deleted_at__isnull=True).select_related('head')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    @extend_schema(
        summary="List departments",
        description="Get paginated list of departments",
        tags=["HR - Department"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create department",
        description="Create a new department (admin only)",
        tags=["HR - Department"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a department"""
    queryset = Department.objects.filter(deleted_at__isnull=True).select_related('head')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get department details",
        description="Retrieve detailed department information",
        tags=["HR - Department"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update department",
        description="Update department information (admin only)",
        tags=["HR - Department"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update department",
        description="Partially update department (admin only)",
        tags=["HR - Department"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete department",
        description="Soft delete department (admin only)",
        tags=["HR - Department"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Position Views
class PositionListView(generics.ListCreateAPIView):
    """List all positions or create new position"""
    queryset = Position.objects.filter(deleted_at__isnull=True).select_related('department')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'department', 'level']
    search_fields = ['code', 'title', 'description']
    ordering_fields = ['code', 'title', 'level', 'created_at']
    ordering = ['code']
    
    @extend_schema(
        summary="List positions",
        description="Get paginated list of positions",
        tags=["HR - Position"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create position",
        description="Create a new position (admin only)",
        tags=["HR - Position"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a position"""
    queryset = Position.objects.filter(deleted_at__isnull=True).select_related('department')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get position details",
        description="Retrieve detailed position information",
        tags=["HR - Position"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update position",
        description="Update position information (admin only)",
        tags=["HR - Position"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete position",
        description="Soft delete position (admin only)",
        tags=["HR - Position"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Employee Views
class EmployeeListView(generics.ListCreateAPIView):
    """List all employees or create new employee"""
    queryset = Employee.objects.filter(
        deleted_at__isnull=True
    ).select_related('user', 'department', 'position', 'manager')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employment_status', 'employment_type', 'department', 'position', 'gender']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['employee_id', 'first_name', 'join_date', 'created_at']
    ordering = ['employee_id']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeSerializer
        return EmployeeListSerializer
    
    @extend_schema(
        summary="List employees",
        description="Get paginated list of employees",
        tags=["HR - Employee"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create employee",
        description="Create a new employee (admin only)",
        tags=["HR - Employee"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an employee"""
    queryset = Employee.objects.filter(
        deleted_at__isnull=True
    ).select_related('user', 'department', 'position', 'manager')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get employee details",
        description="Retrieve detailed employee information",
        tags=["HR - Employee"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update employee",
        description="Update employee information (admin only)",
        tags=["HR - Employee"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete employee",
        description="Soft delete employee (admin only)",
        tags=["HR - Employee"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.employment_status = 'terminated'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Attendance Views
class AttendanceListView(generics.ListCreateAPIView):
    """List all attendance records or create new record"""
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status', 'attendance_type', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'check_in', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Attendance.objects.all().select_related('employee')
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Non-admin users can only see their own attendance
        if not self.request.user.is_staff:
            try:
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        summary="List attendance",
        description="Get paginated list of attendance records",
        tags=["HR - Attendance"],
        parameters=[
            OpenApiParameter(name='start_date', type=str, description='Filter by start date (YYYY-MM-DD)'),
            OpenApiParameter(name='end_date', type=str, description='Filter by end date (YYYY-MM-DD)'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create attendance",
        description="Create a new attendance record",
        tags=["HR - Attendance"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete attendance record"""
    queryset = Attendance.objects.all().select_related('employee')
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get attendance details",
        tags=["HR - Attendance"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update attendance",
        tags=["HR - Attendance"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete attendance",
        tags=["HR - Attendance"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# Leave Views
class LeaveListView(generics.ListCreateAPIView):
    """List all leave requests or create new request"""
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Leave.objects.filter(
            deleted_at__isnull=True
        ).select_related('employee', 'approver')
        
        # Non-admin users can only see their own leaves
        if not self.request.user.is_staff:
            try:
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        summary="List leave requests",
        description="Get paginated list of leave requests",
        tags=["HR - Leave"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create leave request",
        description="Create a new leave request",
        tags=["HR - Leave"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LeaveDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete leave request"""
    queryset = Leave.objects.filter(deleted_at__isnull=True).select_related('employee', 'approver')
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get leave details",
        tags=["HR - Leave"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update leave request",
        tags=["HR - Leave"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete leave request",
        tags=["HR - Leave"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveApprovalView(APIView):
    """Approve or reject leave request"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Approve/reject leave",
        description="Approve or reject a leave request",
        tags=["HR - Leave"]
    )
    def post(self, request, pk):
        try:
            leave = Leave.objects.get(pk=pk, deleted_at__isnull=True)
            
            action = request.data.get('action')  # 'approve' or 'reject'
            notes = request.data.get('notes', '')
            
            if action not in ['approve', 'reject']:
                return Response(
                    {"detail": "Action must be 'approve' or 'reject'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if leave.status != 'pending':
                return Response(
                    {"detail": "Only pending leaves can be approved or rejected."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                approver = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return Response(
                    {"detail": "Only employees can approve leaves."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            leave.status = 'approved' if action == 'approve' else 'rejected'
            leave.approver = approver
            leave.approval_date = timezone.now()
            leave.approval_notes = notes
            leave.save()
            
            # Update leave balance if approved
            if action == 'approve':
                total_days = (leave.end_date - leave.start_date).days + 1
                leave_balance, created = LeaveBalance.objects.get_or_create(
                    employee=leave.employee,
                    year=leave.start_date.year,
                    leave_type=leave.leave_type,
                    defaults={'total_days': 12, 'used_days': 0}
                )
                leave_balance.used_days += total_days
                leave_balance.save()
            
            serializer = LeaveSerializer(leave)
            return Response(serializer.data)
            
        except Leave.DoesNotExist:
            return Response(
                {"detail": "Leave not found."},
                status=status.HTTP_404_NOT_FOUND
            )


# Leave Balance Views
class LeaveBalanceListView(generics.ListCreateAPIView):
    """List all leave balances or create new balance"""
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'year', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['year', 'created_at']
    ordering = ['-year']
    
    def get_queryset(self):
        queryset = LeaveBalance.objects.filter(
            deleted_at__isnull=True
        ).select_related('employee')
        
        # Non-admin users can only see their own balances
        if not self.request.user.is_staff:
            try:
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        summary="List leave balances",
        tags=["HR - Leave"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create leave balance",
        tags=["HR - Leave"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Payroll Views
class PayrollListView(generics.ListCreateAPIView):
    """List all payroll records or create new record"""
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'period_year', 'period_month', 'payment_status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['period_year', 'period_month', 'payment_date', 'created_at']
    ordering = ['-period_year', '-period_month']
    
    def get_queryset(self):
        queryset = Payroll.objects.filter(
            deleted_at__isnull=True
        ).select_related('employee')
        
        # Non-admin users can only see their own payroll
        if not self.request.user.is_staff:
            try:
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        summary="List payroll records",
        tags=["HR - Payroll"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create payroll record",
        tags=["HR - Payroll"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PayrollDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete payroll record"""
    queryset = Payroll.objects.filter(deleted_at__isnull=True).select_related('employee')
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get payroll details",
        tags=["HR - Payroll"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update payroll",
        tags=["HR - Payroll"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete payroll",
        tags=["HR - Payroll"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Performance Review Views
class PerformanceReviewListView(generics.ListCreateAPIView):
    """List all performance reviews or create new review"""
    serializer_class = PerformanceReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'reviewer', 'review_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['review_date', 'overall_score', 'created_at']
    ordering = ['-review_date']
    
    def get_queryset(self):
        queryset = PerformanceReview.objects.filter(
            deleted_at__isnull=True
        ).select_related('employee', 'reviewer')
        
        # Non-admin users can only see their own reviews
        if not self.request.user.is_staff:
            try:
                employee = Employee.objects.get(user=self.request.user)
                queryset = queryset.filter(employee=employee)
            except Employee.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        summary="List performance reviews",
        tags=["HR - Performance"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create performance review",
        tags=["HR - Performance"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PerformanceReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete performance review"""
    queryset = PerformanceReview.objects.filter(
        deleted_at__isnull=True
    ).select_related('employee', 'reviewer')
    serializer_class = PerformanceReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get performance review details",
        tags=["HR - Performance"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update performance review",
        tags=["HR - Performance"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete performance review",
        tags=["HR - Performance"]
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Dashboard/Statistics Views
class HRDashboardView(APIView):
    """HR dashboard with key metrics"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get HR dashboard metrics",
        description="Get key HR metrics and statistics",
        tags=["HR - Dashboard"]
    )
    def get(self, request):
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        # Employee statistics
        total_employees = Employee.objects.filter(
            employment_status='active',
            deleted_at__isnull=True
        ).count()
        
        new_employees_this_month = Employee.objects.filter(
            join_date__year=current_year,
            join_date__month=current_month,
            deleted_at__isnull=True
        ).count()
        
        # Attendance statistics
        present_today = Attendance.objects.filter(
            date=today,
            status='present',
            deleted_at__isnull=True
        ).count()
        
        # Leave statistics
        pending_leaves = Leave.objects.filter(
            status='pending',
            deleted_at__isnull=True
        ).count()
        
        on_leave_today = Leave.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='approved',
            deleted_at__isnull=True
        ).count()
        
        # Department breakdown
        department_stats = Department.objects.filter(
            deleted_at__isnull=True,
            is_active=True
        ).annotate(
            employee_count=Count('employees', filter=Q(employees__employment_status='active'))
        ).values('name', 'employee_count')
        
        return Response({
            'total_employees': total_employees,
            'new_employees_this_month': new_employees_this_month,
            'present_today': present_today,
            'on_leave_today': on_leave_today,
            'pending_leaves': pending_leaves,
            'department_breakdown': list(department_stats)
        })
