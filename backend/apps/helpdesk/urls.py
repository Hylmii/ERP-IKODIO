"""
Helpdesk/Support/Ticketing URLs
"""
from django.urls import path
from apps.helpdesk import views

app_name = 'helpdesk'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.helpdesk_dashboard, name='dashboard'),
    
    # Tickets
    path('tickets/', views.TicketListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/assign/', views.ticket_assign, name='ticket-assign'),
    path('tickets/<int:pk>/resolve/', views.ticket_resolve, name='ticket-resolve'),
    path('tickets/<int:pk>/close/', views.ticket_close, name='ticket-close'),
    path('tickets/<int:pk>/reopen/', views.ticket_reopen, name='ticket-reopen'),
    path('tickets/<int:pk>/rate/', views.ticket_rate, name='ticket-rate'),
    
    # Ticket Comments
    path('tickets/<int:ticket_id>/comments/', views.TicketCommentListView.as_view(), name='ticket-comment-list'),
    
    # SLA Policies
    path('sla-policies/', views.SLAPolicyListView.as_view(), name='sla-policy-list'),
    path('sla-policies/<int:pk>/', views.SLAPolicyDetailView.as_view(), name='sla-policy-detail'),
    
    # Escalations
    path('escalations/', views.TicketEscalationListView.as_view(), name='escalation-list'),
    path('escalations/<int:pk>/resolve/', views.escalation_resolve, name='escalation-resolve'),
    
    # Knowledge Base
    path('knowledge-base/', views.KnowledgeBaseListView.as_view(), name='knowledge-base-list'),
    path('knowledge-base/<int:pk>/', views.KnowledgeBaseDetailView.as_view(), name='knowledge-base-detail'),
    path('knowledge-base/<int:pk>/vote/', views.knowledge_base_vote, name='knowledge-base-vote'),
    path('knowledge-base/<int:pk>/publish/', views.knowledge_base_publish, name='knowledge-base-publish'),
    
    # Ticket Templates
    path('templates/', views.TicketTemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', views.TicketTemplateDetailView.as_view(), name='template-detail'),
]
