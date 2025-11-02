"""
IT Asset & Inventory Management URLs
"""
from django.urls import path
from apps.asset import views

app_name = 'asset'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.asset_dashboard, name='asset-dashboard'),
    
    # Asset Categories
    path('categories/', views.AssetCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.AssetCategoryDetailView.as_view(), name='category-detail'),
    
    # Vendors
    path('vendors/', views.VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', views.VendorDetailView.as_view(), name='vendor-detail'),
    
    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset-list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset-detail'),
    path('assets/<int:pk>/assign/', views.asset_assign, name='asset-assign'),
    path('assets/<int:pk>/return/', views.asset_return, name='asset-return'),
    
    # Procurement
    path('procurements/', views.ProcurementListView.as_view(), name='procurement-list'),
    path('procurements/<int:pk>/', views.ProcurementDetailView.as_view(), name='procurement-detail'),
    path('procurements/<int:pk>/approve/', views.procurement_approve, name='procurement-approve'),
    
    # Asset Maintenance
    path('maintenances/', views.AssetMaintenanceListView.as_view(), name='maintenance-list'),
    path('maintenances/<int:pk>/', views.AssetMaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenances/<int:pk>/complete/', views.maintenance_complete, name='maintenance-complete'),
    
    # Licenses
    path('licenses/', views.LicenseListView.as_view(), name='license-list'),
    path('licenses/<int:pk>/', views.LicenseDetailView.as_view(), name='license-detail'),
]
