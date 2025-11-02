"""
Business Intelligence & Analytics serializers
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.analytics.models import (
    Dashboard, Widget, Report, ReportExecution,
    KPI, KPIValue, DataExport, SavedFilter
)


# ============= Dashboard Serializers =============

class DashboardListSerializer(serializers.ModelSerializer):
    """List serializer for dashboards"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'dashboard_type',
            'owner', 'owner_name',
            'is_public', 'auto_refresh', 'refresh_interval_minutes',
            'display_order', 'is_active', 'is_default',
            'widget_count',
            'created_at', 'updated_at'
        ]
    
    def get_widget_count(self, obj):
        """Count widgets in dashboard"""
        return obj.widgets.filter(deleted_at__isnull=True, is_visible=True).count()


class DashboardSerializer(serializers.ModelSerializer):
    """Detail serializer for dashboards"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    widgets = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = '__all__'
    
    def get_widgets(self, obj):
        """Get dashboard widgets"""
        widgets = obj.widgets.filter(deleted_at__isnull=True, is_visible=True).order_by('display_order')
        return WidgetSerializer(widgets, many=True).data


# ============= Widget Serializers =============

class WidgetSerializer(serializers.ModelSerializer):
    """Serializer for widgets"""
    
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = Widget
        fields = [
            'id', 'dashboard', 'dashboard_name',
            'title', 'description', 'widget_type',
            'data_source', 'query_config', 'display_config',
            'position_x', 'position_y', 'width', 'height',
            'auto_refresh', 'refresh_interval_minutes',
            'display_order', 'is_visible',
            'created_at', 'updated_at'
        ]


# ============= Report Serializers =============

class ReportListSerializer(serializers.ModelSerializer):
    """List serializer for reports"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    execution_count = serializers.SerializerMethodField()
    last_execution_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type',
            'owner', 'owner_name',
            'default_format', 'is_scheduled', 'schedule_cron',
            'is_public', 'is_active',
            'run_count', 'last_run_at',
            'execution_count', 'last_execution_status',
            'created_at', 'updated_at'
        ]
    
    def get_execution_count(self, obj):
        """Count report executions"""
        return obj.executions.count()
    
    def get_last_execution_status(self, obj):
        """Get last execution status"""
        last_execution = obj.executions.order_by('-started_at').first()
        return last_execution.status if last_execution else None


class ReportSerializer(serializers.ModelSerializer):
    """Detail serializer for reports"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    recent_executions = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
    
    def get_recent_executions(self, obj):
        """Get recent executions"""
        executions = obj.executions.order_by('-started_at')[:10]
        return ReportExecutionSerializer(executions, many=True).data


# ============= Report Execution Serializers =============

class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for report executions"""
    
    report_name = serializers.CharField(source='report.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.get_full_name', read_only=True)
    output_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'report', 'report_name',
            'executed_by', 'executed_by_name',
            'parameters', 'status',
            'started_at', 'completed_at', 'duration_seconds',
            'output_format', 'output_file', 'output_size_bytes', 'output_size_mb',
            'row_count', 'error_message',
            'created_at'
        ]
    
    def get_output_size_mb(self, obj):
        """Convert output size to MB"""
        if obj.output_size_bytes:
            return round(obj.output_size_bytes / (1024 * 1024), 2)
        return None


# ============= KPI Serializers =============

class KPIListSerializer(serializers.ModelSerializer):
    """List serializer for KPIs"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    achievement_percentage = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    variance = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = [
            'id', 'name', 'description', 'kpi_type',
            'owner', 'owner_name',
            'department', 'department_name',
            'project', 'project_name',
            'target_value', 'current_value', 'achievement_percentage',
            'threshold_red', 'threshold_yellow', 'threshold_green',
            'unit', 'frequency', 'period_start', 'period_end',
            'last_calculated_at', 'status_color', 'variance',
            'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_achievement_percentage(self, obj):
        """Calculate achievement percentage"""
        if obj.target_value and obj.target_value != 0:
            return round((obj.current_value / obj.target_value) * 100, 2)
        return None
    
    def get_status_color(self, obj):
        """Determine status color based on thresholds"""
        if obj.threshold_green and obj.current_value >= obj.threshold_green:
            return 'green'
        elif obj.threshold_yellow and obj.current_value >= obj.threshold_yellow:
            return 'yellow'
        elif obj.threshold_red:
            return 'red'
        return 'gray'
    
    def get_variance(self, obj):
        """Calculate variance from target"""
        return obj.current_value - obj.target_value


class KPISerializer(serializers.ModelSerializer):
    """Detail serializer for KPIs"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    achievement_percentage = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    variance = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = '__all__'
    
    def get_achievement_percentage(self, obj):
        """Achievement percentage"""
        serializer = KPIListSerializer()
        return serializer.get_achievement_percentage(obj)
    
    def get_status_color(self, obj):
        """Status color"""
        serializer = KPIListSerializer()
        return serializer.get_status_color(obj)
    
    def get_variance(self, obj):
        """Variance from target"""
        serializer = KPIListSerializer()
        return serializer.get_variance(obj)
    
    def get_trend(self, obj):
        """Get recent trend (last 7 values)"""
        values = obj.values.order_by('-period_date')[:7]
        return KPIValueSerializer(values, many=True).data


# ============= KPI Value Serializers =============

class KPIValueSerializer(serializers.ModelSerializer):
    """Serializer for KPI values"""
    
    kpi_name = serializers.CharField(source='kpi.name', read_only=True)
    
    class Meta:
        model = KPIValue
        fields = [
            'id', 'kpi', 'kpi_name',
            'period_date', 'value', 'target_value',
            'variance', 'variance_percentage', 'status',
            'notes',
            'created_at'
        ]


# ============= Data Export Serializers =============

class DataExportSerializer(serializers.ModelSerializer):
    """Serializer for data exports"""
    
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = DataExport
        fields = [
            'id', 'export_type', 'export_format',
            'requested_by', 'requested_by_name',
            'filters', 'status',
            'output_file', 'file_size_bytes', 'file_size_mb',
            'row_count',
            'started_at', 'completed_at', 'expires_at', 'is_expired',
            'error_message',
            'created_at'
        ]
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size_bytes:
            return round(obj.file_size_bytes / (1024 * 1024), 2)
        return None
    
    def get_is_expired(self, obj):
        """Check if export has expired"""
        if obj.expires_at:
            return timezone.now() > obj.expires_at
        return False


# ============= Saved Filter Serializers =============

class SavedFilterSerializer(serializers.ModelSerializer):
    """Serializer for saved filters"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = SavedFilter
        fields = [
            'id', 'name', 'description', 'filter_type',
            'owner', 'owner_name',
            'filter_config', 'is_public',
            'usage_count', 'last_used_at',
            'created_at', 'updated_at'
        ]
