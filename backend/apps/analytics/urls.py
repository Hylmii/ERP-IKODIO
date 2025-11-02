"""
Business Intelligence & Analytics URLs
"""
from django.urls import path
from apps.analytics import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    
    # Dashboards
    path('dashboards/', views.DashboardListView.as_view(), name='dashboard-list'),
    path('dashboards/<int:pk>/', views.DashboardDetailView.as_view(), name='dashboard-detail'),
    
    # Widgets
    path('widgets/', views.WidgetListView.as_view(), name='widget-list'),
    path('widgets/<int:pk>/', views.WidgetDetailView.as_view(), name='widget-detail'),
    
    # Reports
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/run/', views.report_run, name='report-run'),
    
    # Report Executions
    path('executions/', views.ReportExecutionListView.as_view(), name='execution-list'),
    
    # KPIs
    path('kpis/', views.KPIListView.as_view(), name='kpi-list'),
    path('kpis/<int:pk>/', views.KPIDetailView.as_view(), name='kpi-detail'),
    path('kpis/<int:pk>/update-value/', views.kpi_update_value, name='kpi-update-value'),
    
    # KPI Values
    path('kpi-values/', views.KPIValueListView.as_view(), name='kpi-value-list'),
    
    # Data Exports
    path('exports/', views.DataExportListView.as_view(), name='export-list'),
    path('exports/<int:pk>/', views.DataExportDetailView.as_view(), name='export-detail'),
    
    # Saved Filters
    path('filters/', views.SavedFilterListView.as_view(), name='filter-list'),
    path('filters/<int:pk>/', views.SavedFilterDetailView.as_view(), name='filter-detail'),
]
