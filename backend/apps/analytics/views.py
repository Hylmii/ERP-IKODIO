"""
Business Intelligence & Analytics views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta

from apps.analytics.models import (
    Dashboard, Widget, Report, ReportExecution,
    KPI, KPIValue, DataExport, SavedFilter
)
from apps.analytics.serializers import (
    DashboardListSerializer, DashboardSerializer,
    WidgetSerializer,
    ReportListSerializer, ReportSerializer,
    ReportExecutionSerializer,
    KPIListSerializer, KPISerializer,
    KPIValueSerializer,
    DataExportSerializer,
    SavedFilterSerializer
)
from apps.core.permissions import IsAdminOrReadOnly


# ============= Dashboard Views =============

class DashboardListView(generics.ListCreateAPIView):
    """List and create dashboards"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['dashboard_type', 'owner', 'is_public', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'created_at']
    ordering = ['display_order']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DashboardSerializer
        return DashboardListSerializer
    
    def get_queryset(self):
        queryset = Dashboard.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) |
                    Q(owner=user.employee) |
                    Q(shared_with_employees=user.employee) |
                    Q(shared_with_departments=user.employee.department)
                ).distinct()
        
        # Filter my dashboards
        if self.request.query_params.get('my_dashboards', None) == 'true':
            if hasattr(user, 'employee'):
                queryset = queryset.filter(owner=user.employee)
        
        return queryset.select_related('owner')


class DashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a dashboard"""
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer
    
    def get_queryset(self):
        queryset = Dashboard.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) |
                    Q(owner=user.employee) |
                    Q(shared_with_employees=user.employee) |
                    Q(shared_with_departments=user.employee.department)
                ).distinct()
        
        return queryset.select_related('owner')
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Widget Views =============

class WidgetListView(generics.ListCreateAPIView):
    """List and create widgets"""
    permission_classes = [IsAuthenticated]
    serializer_class = WidgetSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['dashboard', 'widget_type']
    ordering = ['display_order']
    
    def get_queryset(self):
        queryset = Widget.objects.filter(deleted_at__isnull=True)
        
        # Filter by dashboard
        dashboard_id = self.request.query_params.get('dashboard', None)
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
        
        return queryset.select_related('dashboard')


class WidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a widget"""
    permission_classes = [IsAuthenticated]
    serializer_class = WidgetSerializer
    queryset = Widget.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Report Views =============

class ReportListView(generics.ListCreateAPIView):
    """List and create reports"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'owner', 'is_public', 'is_scheduled', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'last_run_at', 'run_count']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReportSerializer
        return ReportListSerializer
    
    def get_queryset(self):
        queryset = Report.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) | Q(owner=user.employee)
                )
        
        # Filter my reports
        if self.request.query_params.get('my_reports', None) == 'true':
            if hasattr(user, 'employee'):
                queryset = queryset.filter(owner=user.employee)
        
        return queryset.select_related('owner')


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a report"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer
    
    def get_queryset(self):
        queryset = Report.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) | Q(owner=user.employee)
                )
        
        return queryset.select_related('owner')
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_run(request, pk):
    """Run a report"""
    try:
        report = Report.objects.get(pk=pk, deleted_at__isnull=True)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check access
    user = request.user
    if not report.is_public and not user.is_staff:
        if hasattr(user, 'employee') and report.owner != user.employee:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get parameters
    parameters = request.data.get('parameters', {})
    output_format = request.data.get('output_format', report.default_format)
    
    # Create execution record
    execution = ReportExecution.objects.create(
        report=report,
        executed_by=user.employee if hasattr(user, 'employee') else None,
        parameters=parameters,
        output_format=output_format,
        status='running'
    )
    
    # In a real implementation, this would be handled by a background task (Celery)
    # For now, we'll just mark it as completed
    execution.status = 'completed'
    execution.completed_at = timezone.now()
    execution.duration_seconds = 2
    execution.row_count = 100  # Mock data
    execution.save()
    
    # Update report run count
    report.run_count += 1
    report.last_run_at = timezone.now()
    report.save()
    
    serializer = ReportExecutionSerializer(execution)
    return Response(serializer.data)


# ============= Report Execution Views =============

class ReportExecutionListView(generics.ListAPIView):
    """List report executions"""
    permission_classes = [IsAuthenticated]
    serializer_class = ReportExecutionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report', 'executed_by', 'status']
    ordering = ['-started_at']
    
    def get_queryset(self):
        queryset = ReportExecution.objects.all()
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(report__is_public=True) |
                    Q(report__owner=user.employee) |
                    Q(executed_by=user.employee)
                )
        
        return queryset.select_related('report', 'executed_by')


# ============= KPI Views =============

class KPIListView(generics.ListCreateAPIView):
    """List and create KPIs"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['kpi_type', 'owner', 'department', 'project', 'frequency', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'current_value']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KPISerializer
        return KPIListSerializer
    
    def get_queryset(self):
        queryset = KPI.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(owner=user.employee) |
                    Q(department=user.employee.department)
                )
        
        # Filter my KPIs
        if self.request.query_params.get('my_kpis', None) == 'true':
            if hasattr(user, 'employee'):
                queryset = queryset.filter(owner=user.employee)
        
        return queryset.select_related('owner', 'department', 'project')


class KPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a KPI"""
    permission_classes = [IsAuthenticated]
    serializer_class = KPISerializer
    
    def get_queryset(self):
        queryset = KPI.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(owner=user.employee) |
                    Q(department=user.employee.department)
                )
        
        return queryset.select_related('owner', 'department', 'project')
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kpi_update_value(request, pk):
    """Update KPI current value"""
    try:
        kpi = KPI.objects.get(pk=pk, deleted_at__isnull=True)
    except KPI.DoesNotExist:
        return Response({'error': 'KPI not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if owner or admin
    user = request.user
    if not user.is_staff:
        if hasattr(user, 'employee') and kpi.owner != user.employee:
            return Response({'error': 'Only owner can update KPI value'}, status=status.HTTP_403_FORBIDDEN)
    
    new_value = request.data.get('value')
    period_date = request.data.get('period_date', timezone.now().date())
    notes = request.data.get('notes', '')
    
    if new_value is None:
        return Response({'error': 'Value is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update current value
    kpi.current_value = new_value
    kpi.last_calculated_at = timezone.now()
    kpi.save()
    
    # Calculate variance
    variance = new_value - kpi.target_value
    variance_percentage = (variance / kpi.target_value * 100) if kpi.target_value != 0 else 0
    
    # Determine status
    if kpi.threshold_green and new_value >= kpi.threshold_green:
        status_color = 'green'
    elif kpi.threshold_yellow and new_value >= kpi.threshold_yellow:
        status_color = 'yellow'
    else:
        status_color = 'red'
    
    # Create historical value
    KPIValue.objects.create(
        kpi=kpi,
        period_date=period_date,
        value=new_value,
        target_value=kpi.target_value,
        variance=variance,
        variance_percentage=variance_percentage,
        status=status_color,
        notes=notes
    )
    
    serializer = KPISerializer(kpi)
    return Response(serializer.data)


# ============= KPI Value Views =============

class KPIValueListView(generics.ListCreateAPIView):
    """List and create KPI values"""
    permission_classes = [IsAuthenticated]
    serializer_class = KPIValueSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['kpi', 'status']
    ordering = ['-period_date']
    
    def get_queryset(self):
        kpi_id = self.request.query_params.get('kpi', None)
        queryset = KPIValue.objects.all()
        
        if kpi_id:
            queryset = queryset.filter(kpi_id=kpi_id)
        
        return queryset.select_related('kpi')


# ============= Data Export Views =============

class DataExportListView(generics.ListCreateAPIView):
    """List and create data exports"""
    permission_classes = [IsAuthenticated]
    serializer_class = DataExportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['export_type', 'export_format', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = DataExport.objects.all()
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(requested_by=user.employee)
        
        return queryset.select_related('requested_by')
    
    def perform_create(self, serializer):
        # Auto-set requested_by
        if hasattr(self.request.user, 'employee'):
            serializer.save(
                requested_by=self.request.user.employee,
                status='processing',
                started_at=timezone.now()
            )


class DataExportDetailView(generics.RetrieveAPIView):
    """Retrieve a data export"""
    permission_classes = [IsAuthenticated]
    serializer_class = DataExportSerializer
    
    def get_queryset(self):
        queryset = DataExport.objects.all()
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(requested_by=user.employee)
        
        return queryset.select_related('requested_by')


# ============= Saved Filter Views =============

class SavedFilterListView(generics.ListCreateAPIView):
    """List and create saved filters"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavedFilterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['filter_type', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = SavedFilter.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) | Q(owner=user.employee)
                )
        
        return queryset.select_related('owner')
    
    def perform_create(self, serializer):
        # Auto-set owner
        if hasattr(self.request.user, 'employee'):
            serializer.save(owner=self.request.user.employee)


class SavedFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a saved filter"""
    permission_classes = [IsAuthenticated]
    serializer_class = SavedFilterSerializer
    
    def get_queryset(self):
        queryset = SavedFilter.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) | Q(owner=user.employee)
                )
        
        return queryset.select_related('owner')
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Dashboard =============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """Analytics overview dashboard"""
    
    # Dashboard metrics
    all_dashboards = Dashboard.objects.filter(deleted_at__isnull=True)
    active_dashboards = all_dashboards.filter(is_active=True).count()
    
    # Report metrics
    all_reports = Report.objects.filter(deleted_at__isnull=True)
    active_reports = all_reports.filter(is_active=True).count()
    scheduled_reports = all_reports.filter(is_scheduled=True, is_active=True).count()
    
    # Recent executions
    recent_executions = ReportExecution.objects.filter(
        status='completed'
    ).order_by('-completed_at')[:5]
    
    # KPI metrics
    all_kpis = KPI.objects.filter(deleted_at__isnull=True)
    active_kpis = all_kpis.filter(is_active=True).count()
    
    # KPIs by status
    green_kpis = 0
    yellow_kpis = 0
    red_kpis = 0
    
    for kpi in all_kpis.filter(is_active=True):
        if kpi.threshold_green and kpi.current_value >= kpi.threshold_green:
            green_kpis += 1
        elif kpi.threshold_yellow and kpi.current_value >= kpi.threshold_yellow:
            yellow_kpis += 1
        else:
            red_kpis += 1
    
    # Export metrics
    today = timezone.now().date()
    exports_today = DataExport.objects.filter(created_at__date=today).count()
    
    return Response({
        'dashboards': {
            'total': all_dashboards.count(),
            'active': active_dashboards,
        },
        'reports': {
            'total': all_reports.count(),
            'active': active_reports,
            'scheduled': scheduled_reports,
            'recent_executions': ReportExecutionSerializer(recent_executions, many=True).data,
        },
        'kpis': {
            'total': all_kpis.count(),
            'active': active_kpis,
            'green': green_kpis,
            'yellow': yellow_kpis,
            'red': red_kpis,
        },
        'exports': {
            'today': exports_today,
        },
    })
