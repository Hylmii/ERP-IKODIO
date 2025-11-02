"""
Document Management System URLs
"""
from django.urls import path
from apps.dms import views

app_name = 'dms'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dms_dashboard, name='dashboard'),
    
    # Document Categories
    path('categories/', views.DocumentCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.DocumentCategoryDetailView.as_view(), name='category-detail'),
    
    # Documents
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/download/', views.document_download, name='document-download'),
    path('documents/<int:pk>/share/', views.document_share, name='document-share'),
    
    # Document Versions
    path('documents/<int:document_id>/versions/', views.DocumentVersionListView.as_view(), name='document-version-list'),
    
    # Document Approvals
    path('approvals/', views.DocumentApprovalListView.as_view(), name='approval-list'),
    path('approvals/<int:pk>/approve/', views.approval_approve, name='approval-approve'),
    path('approvals/<int:pk>/reject/', views.approval_reject, name='approval-reject'),
    
    # Document Access
    path('accesses/', views.DocumentAccessListView.as_view(), name='access-list'),
    
    # Document Templates
    path('templates/', views.DocumentTemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.DocumentTemplateDetailView.as_view(), name='template-detail'),
    
    # Document Activities
    path('activities/', views.DocumentActivityListView.as_view(), name='activity-list'),
    path('documents/<int:document_id>/activities/', views.DocumentActivityListView.as_view(), name='document-activity-list'),
]
