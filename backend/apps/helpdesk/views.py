"""
Helpdesk/Support/Ticketing System views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from decimal import Decimal
from datetime import timedelta

from apps.helpdesk.models import (
    Ticket, TicketComment, SLAPolicy, TicketEscalation,
    KnowledgeBase, TicketTemplate
)
from apps.helpdesk.serializers import (
    TicketListSerializer, TicketSerializer,
    TicketCommentSerializer,
    SLAPolicyListSerializer, SLAPolicySerializer,
    TicketEscalationSerializer,
    KnowledgeBaseListSerializer, KnowledgeBaseSerializer,
    TicketTemplateListSerializer, TicketTemplateSerializer
)
from apps.core.permissions import IsAdminOrReadOnly


# ============= Ticket Views =============

class TicketListView(generics.ListCreateAPIView):
    """List and create tickets"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to', 'assigned_team', 'requester', 'client']
    search_fields = ['ticket_number', 'subject', 'description', 'requester_email']
    ordering_fields = ['created_at', 'priority', 'status', 'due_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketSerializer
        return TicketListSerializer
    
    def get_queryset(self):
        queryset = Ticket.objects.filter(deleted_at__isnull=True)
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            # Non-admin users see tickets they created or assigned to them
            queryset = queryset.filter(
                Q(requester__user=user) | Q(assigned_to__user=user)
            )
        
        # Filter by status groups
        status_filter = self.request.query_params.get('status_group', None)
        if status_filter == 'open':
            queryset = queryset.filter(status__in=['new', 'open', 'in_progress', 'pending'])
        elif status_filter == 'closed':
            queryset = queryset.filter(status__in=['resolved', 'closed', 'cancelled'])
        
        # Filter overdue tickets
        if self.request.query_params.get('overdue', None) == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                resolution_due__lt=now,
                status__in=['new', 'open', 'in_progress', 'pending']
            )
        
        # Filter by assigned to me
        if self.request.query_params.get('my_tickets', None) == 'true':
            queryset = queryset.filter(assigned_to__user=user)
        
        return queryset.select_related(
            'requester', 'assigned_to', 'assigned_team', 'client', 'sla_policy'
        )


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a ticket"""
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        queryset = Ticket.objects.filter(deleted_at__isnull=True)
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(requester__user=user) | Q(assigned_to__user=user)
            )
        
        return queryset.select_related(
            'requester', 'assigned_to', 'assigned_team', 'client', 'sla_policy'
        )
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_assign(request, pk):
    """Assign ticket to employee or team"""
    try:
        ticket = Ticket.objects.get(pk=pk, deleted_at__isnull=True)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    user = request.user
    if not user.is_staff and ticket.requester.user != user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    assigned_to_id = request.data.get('assigned_to')
    assigned_team_id = request.data.get('assigned_team')
    
    if assigned_to_id:
        ticket.assigned_to_id = assigned_to_id
    
    if assigned_team_id:
        ticket.assigned_team_id = assigned_team_id
    
    # Update status if still new
    if ticket.status == 'new':
        ticket.status = 'open'
    
    ticket.save()
    
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_resolve(request, pk):
    """Mark ticket as resolved"""
    try:
        ticket = Ticket.objects.get(pk=pk, deleted_at__isnull=True)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions - only assigned employee or admin can resolve
    user = request.user
    if not user.is_staff:
        if not ticket.assigned_to or ticket.assigned_to.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    resolution = request.data.get('resolution', '')
    
    ticket.status = 'resolved'
    ticket.resolution = resolution
    ticket.resolved_at = timezone.now()
    
    # Calculate resolution time
    resolution_time = ticket.resolved_at - ticket.created_at
    ticket.resolution_time_hours = Decimal(str(round(resolution_time.total_seconds() / 3600, 2)))
    
    ticket.save()
    
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_close(request, pk):
    """Close a resolved ticket"""
    try:
        ticket = Ticket.objects.get(pk=pk, deleted_at__isnull=True)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if ticket.status != 'resolved':
        return Response({'error': 'Only resolved tickets can be closed'}, status=status.HTTP_400_BAD_REQUEST)
    
    ticket.status = 'closed'
    ticket.closed_at = timezone.now()
    ticket.save()
    
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_reopen(request, pk):
    """Reopen a closed ticket"""
    try:
        ticket = Ticket.objects.get(pk=pk, deleted_at__isnull=True)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if ticket.status not in ['resolved', 'closed']:
        return Response({'error': 'Only resolved/closed tickets can be reopened'}, status=status.HTTP_400_BAD_REQUEST)
    
    reason = request.data.get('reason', '')
    
    ticket.status = 'open'
    ticket.resolved_at = None
    ticket.closed_at = None
    ticket.resolution_time_hours = None
    ticket.save()
    
    # Add comment about reopening
    if hasattr(request.user, 'employee'):
        TicketComment.objects.create(
            ticket=ticket,
            author=request.user.employee,
            comment=f"Ticket reopened. Reason: {reason}",
            is_internal=False
        )
    
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_rate(request, pk):
    """Rate ticket satisfaction"""
    try:
        ticket = Ticket.objects.get(pk=pk, deleted_at__isnull=True)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if requester
    user = request.user
    if hasattr(user, 'employee') and ticket.requester != user.employee:
        return Response({'error': 'Only requester can rate the ticket'}, status=status.HTTP_403_FORBIDDEN)
    
    rating = request.data.get('rating')
    feedback = request.data.get('feedback', '')
    
    if not rating or not (1 <= int(rating) <= 5):
        return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
    
    ticket.satisfaction_rating = rating
    ticket.satisfaction_feedback = feedback
    ticket.save()
    
    serializer = TicketSerializer(ticket)
    return Response(serializer.data)


# ============= Ticket Comment Views =============

class TicketCommentListView(generics.ListCreateAPIView):
    """List and create ticket comments"""
    permission_classes = [IsAuthenticated]
    serializer_class = TicketCommentSerializer
    
    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        queryset = TicketComment.objects.filter(ticket_id=ticket_id)
        
        # Hide internal comments from non-staff users
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(is_internal=False)
        
        return queryset.select_related('author', 'ticket').order_by('created_at')
    
    def perform_create(self, serializer):
        # Auto-set author
        if hasattr(self.request.user, 'employee'):
            ticket_id = self.kwargs.get('ticket_id')
            ticket = Ticket.objects.get(pk=ticket_id)
            
            comment = serializer.save(
                author=self.request.user.employee,
                ticket=ticket
            )
            
            # Update first response time if not set
            if not ticket.first_response_at and ticket.assigned_to == self.request.user.employee:
                ticket.first_response_at = timezone.now()
                ticket.save()


# ============= SLA Policy Views =============

class SLAPolicyListView(generics.ListCreateAPIView):
    """List and create SLA policies"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['priority', 'response_time_hours', 'resolution_time_hours']
    ordering = ['priority']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SLAPolicySerializer
        return SLAPolicyListSerializer
    
    def get_queryset(self):
        queryset = SLAPolicy.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset


class SLAPolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an SLA policy"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SLAPolicySerializer
    queryset = SLAPolicy.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Ticket Escalation Views =============

class TicketEscalationListView(generics.ListCreateAPIView):
    """List and create ticket escalations"""
    permission_classes = [IsAuthenticated]
    serializer_class = TicketEscalationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ticket', 'escalated_to', 'resolved']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = TicketEscalation.objects.all()
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(escalated_to__user=user) | Q(escalated_from__user=user)
                )
        
        return queryset.select_related('ticket', 'escalated_from', 'escalated_to')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalation_resolve(request, pk):
    """Mark escalation as resolved"""
    try:
        escalation = TicketEscalation.objects.get(pk=pk)
    except TicketEscalation.DoesNotExist:
        return Response({'error': 'Escalation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    escalation.resolved = True
    escalation.resolved_at = timezone.now()
    escalation.save()
    
    serializer = TicketEscalationSerializer(escalation)
    return Response(serializer.data)


# ============= Knowledge Base Views =============

class KnowledgeBaseListView(generics.ListCreateAPIView):
    """List and create knowledge base articles"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'author']
    search_fields = ['title', 'content', 'summary', 'keywords', 'tags']
    ordering_fields = ['published_at', 'view_count', 'helpful_count']
    ordering = ['-published_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KnowledgeBaseSerializer
        return KnowledgeBaseListSerializer
    
    def get_queryset(self):
        queryset = KnowledgeBase.objects.filter(deleted_at__isnull=True)
        
        # Non-admin users see only published articles
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset.select_related('author')


class KnowledgeBaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a knowledge base article"""
    permission_classes = [IsAuthenticated]
    serializer_class = KnowledgeBaseSerializer
    
    def get_queryset(self):
        queryset = KnowledgeBase.objects.filter(deleted_at__isnull=True)
        
        # Non-admin users see only published articles
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset.select_related('author')
    
    def retrieve(self, request, *args, **kwargs):
        # Increment view count
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def knowledge_base_vote(request, pk):
    """Vote on article helpfulness"""
    try:
        article = KnowledgeBase.objects.get(pk=pk, deleted_at__isnull=True)
    except KnowledgeBase.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)
    
    helpful = request.data.get('helpful')
    
    if helpful is True or helpful == 'true':
        article.helpful_count += 1
    else:
        article.not_helpful_count += 1
    
    article.save()
    
    serializer = KnowledgeBaseSerializer(article)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def knowledge_base_publish(request, pk):
    """Publish a draft article"""
    try:
        article = KnowledgeBase.objects.get(pk=pk, deleted_at__isnull=True)
    except KnowledgeBase.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if article.status != 'draft':
        return Response({'error': 'Only draft articles can be published'}, status=status.HTTP_400_BAD_REQUEST)
    
    article.status = 'published'
    article.published_at = timezone.now()
    article.save()
    
    serializer = KnowledgeBaseSerializer(article)
    return Response(serializer.data)


# ============= Ticket Template Views =============

class TicketTemplateListView(generics.ListCreateAPIView):
    """List and create ticket templates"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['usage_count', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketTemplateSerializer
        return TicketTemplateListSerializer
    
    def get_queryset(self):
        queryset = TicketTemplate.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.select_related('default_assigned_team', 'sla_policy')


class TicketTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a ticket template"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TicketTemplateSerializer
    queryset = TicketTemplate.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Dashboard =============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def helpdesk_dashboard(request):
    """Helpdesk dashboard with metrics"""
    
    # Ticket metrics
    all_tickets = Ticket.objects.filter(deleted_at__isnull=True)
    open_tickets = all_tickets.filter(status__in=['new', 'open', 'in_progress', 'pending'])
    
    # Count by status
    ticket_by_status = {}
    for status_key, status_label in Ticket.STATUS_CHOICES:
        count = all_tickets.filter(status=status_key).count()
        ticket_by_status[status_key] = {
            'label': status_label,
            'count': count
        }
    
    # Count by priority
    ticket_by_priority = {}
    for priority_key, priority_label in Ticket.PRIORITY_CHOICES:
        count = all_tickets.filter(priority=priority_key).count()
        ticket_by_priority[priority_key] = {
            'label': priority_label,
            'count': count
        }
    
    # Overdue tickets
    now = timezone.now()
    overdue_tickets = open_tickets.filter(resolution_due__lt=now).count()
    
    # Response time metrics
    tickets_with_response = all_tickets.exclude(first_response_at__isnull=True)
    avg_first_response_hours = None
    if tickets_with_response.exists():
        total_seconds = sum([
            (t.first_response_at - t.created_at).total_seconds()
            for t in tickets_with_response
        ])
        avg_first_response_hours = round(total_seconds / tickets_with_response.count() / 3600, 2)
    
    # Resolution time metrics
    resolved_tickets = all_tickets.filter(status__in=['resolved', 'closed'])
    avg_resolution_hours = resolved_tickets.aggregate(
        avg=Avg('resolution_time_hours')
    )['avg']
    if avg_resolution_hours:
        avg_resolution_hours = round(float(avg_resolution_hours), 2)
    
    # Satisfaction metrics
    rated_tickets = all_tickets.exclude(satisfaction_rating__isnull=True)
    avg_satisfaction = rated_tickets.aggregate(avg=Avg('satisfaction_rating'))['avg']
    if avg_satisfaction:
        avg_satisfaction = round(float(avg_satisfaction), 2)
    
    # SLA compliance
    tickets_with_sla = resolved_tickets.exclude(sla_policy__isnull=True)
    sla_met_count = 0
    for ticket in tickets_with_sla:
        if ticket.resolved_at and ticket.resolution_due:
            if ticket.resolved_at <= ticket.resolution_due:
                sla_met_count += 1
    
    sla_compliance_rate = None
    if tickets_with_sla.count() > 0:
        sla_compliance_rate = round((sla_met_count / tickets_with_sla.count()) * 100, 2)
    
    # Top categories
    ticket_by_category = {}
    for category_key, category_label in Ticket.CATEGORY_CHOICES:
        count = all_tickets.filter(category=category_key).count()
        ticket_by_category[category_key] = {
            'label': category_label,
            'count': count
        }
    
    # Knowledge base metrics
    kb_articles = KnowledgeBase.objects.filter(deleted_at__isnull=True)
    kb_published = kb_articles.filter(status='published').count()
    kb_total_views = kb_articles.aggregate(total=Sum('view_count'))['total'] or 0
    
    # Recent tickets
    recent_tickets = open_tickets.order_by('-created_at')[:10]
    recent_tickets_data = TicketListSerializer(recent_tickets, many=True).data
    
    return Response({
        'tickets': {
            'total': all_tickets.count(),
            'open': open_tickets.count(),
            'resolved': resolved_tickets.count(),
            'overdue': overdue_tickets,
            'by_status': ticket_by_status,
            'by_priority': ticket_by_priority,
            'by_category': ticket_by_category,
        },
        'performance': {
            'avg_first_response_hours': avg_first_response_hours,
            'avg_resolution_hours': avg_resolution_hours,
            'avg_satisfaction_rating': avg_satisfaction,
            'sla_compliance_rate': sla_compliance_rate,
        },
        'knowledge_base': {
            'total_articles': kb_articles.count(),
            'published_articles': kb_published,
            'total_views': kb_total_views,
        },
        'recent_tickets': recent_tickets_data,
    })
