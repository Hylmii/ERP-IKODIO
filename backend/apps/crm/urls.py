"""
CRM & Sales URLs
"""
from django.urls import path
from apps.crm import views

app_name = 'crm'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.crm_dashboard, name='crm-dashboard'),
    
    # Clients
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    
    # Leads
    path('leads/', views.LeadListView.as_view(), name='lead-list'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead-detail'),
    path('leads/<int:pk>/convert/', views.lead_convert, name='lead-convert'),
    
    # Opportunities
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity-list'),
    path('opportunities/<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity-detail'),
    path('opportunities/<int:pk>/move/', views.opportunity_move_stage, name='opportunity-move'),
    
    # Contracts
    path('contracts/', views.ContractListView.as_view(), name='contract-list'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
    
    # Quotations
    path('quotations/', views.QuotationListView.as_view(), name='quotation-list'),
    path('quotations/<int:pk>/', views.QuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<int:pk>/accept/', views.quotation_accept, name='quotation-accept'),
    path('quotations/<int:pk>/reject/', views.quotation_reject, name='quotation-reject'),
    
    # Follow-ups
    path('follow-ups/', views.FollowUpListView.as_view(), name='followup-list'),
    path('follow-ups/<int:pk>/', views.FollowUpDetailView.as_view(), name='followup-detail'),
    path('follow-ups/<int:pk>/complete/', views.followup_complete, name='followup-complete'),
]
