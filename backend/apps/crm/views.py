"""
CRM & Sales views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.authentication.permissions import IsAdminOrReadOnly
from apps.crm.models import (
    Client, Lead, Opportunity, Contract, Quotation, QuotationLine, FollowUp
)
from apps.crm.serializers import (
    ClientListSerializer, ClientSerializer,
    LeadListSerializer, LeadSerializer,
    OpportunityListSerializer, OpportunitySerializer,
    ContractListSerializer, ContractSerializer,
    QuotationListSerializer, QuotationSerializer, QuotationLineSerializer,
    FollowUpListSerializer, FollowUpSerializer
)


# ============ Client ============

class ClientListView(generics.ListCreateAPIView):
    """List and create clients"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = ClientListSerializer
    
    def get_queryset(self):
        queryset = Client.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by client type
        client_type = self.request.query_params.get('type')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        # Filter by account manager
        account_manager = self.request.query_params.get('account_manager')
        if account_manager:
            queryset = queryset.filter(account_manager_id=account_manager)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.select_related('account_manager')


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete client"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = ClientSerializer
    
    def get_queryset(self):
        return Client.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Lead ============

class LeadListView(generics.ListCreateAPIView):
    """List and create leads"""
    permission_classes = [IsAuthenticated]
    serializer_class = LeadListSerializer
    
    def get_queryset(self):
        queryset = Lead.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their assigned leads
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(assigned_to=user.employee_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter qualified
        is_qualified = self.request.query_params.get('is_qualified')
        if is_qualified is not None:
            queryset = queryset.filter(is_qualified=is_qualified.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(lead_number__icontains=search) |
                Q(company_name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.select_related('assigned_to')


class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete lead"""
    permission_classes = [IsAuthenticated]
    serializer_class = LeadSerializer
    
    def get_queryset(self):
        queryset = Lead.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their assigned leads
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(assigned_to=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lead_convert(request, pk):
    """Convert a lead to opportunity"""
    try:
        lead = Lead.objects.get(pk=pk, deleted_at__isnull=True)
    except Lead.DoesNotExist:
        return Response(
            {'error': 'Lead not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if lead.status == 'converted':
        return Response(
            {'error': 'Lead already converted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create opportunity from lead
    opportunity_data = request.data.get('opportunity', {})
    opportunity = Opportunity.objects.create(
        opportunity_number=f"OPP-{timezone.now().strftime('%Y%m%d')}-{Opportunity.objects.count() + 1:04d}",
        name=opportunity_data.get('name', f"Opportunity from {lead.contact_name}"),
        description=opportunity_data.get('description', lead.description),
        lead=lead,
        estimated_value=lead.estimated_value or 0,
        expected_revenue=lead.estimated_value or 0,
        expected_close_date=opportunity_data.get('expected_close_date', timezone.now().date() + timedelta(days=30)),
        owner=lead.assigned_to or request.user.employee_profile,
        stage='prospecting',
        probability=10
    )
    
    # Update lead
    lead.status = 'converted'
    lead.converted_opportunity = opportunity
    lead.converted_at = timezone.now()
    lead.save()
    
    from apps.crm.serializers import OpportunitySerializer
    serializer = OpportunitySerializer(opportunity)
    return Response(serializer.data)


# ============ Opportunity ============

class OpportunityListView(generics.ListCreateAPIView):
    """List and create opportunities"""
    permission_classes = [IsAuthenticated]
    serializer_class = OpportunityListSerializer
    
    def get_queryset(self):
        queryset = Opportunity.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their owned opportunities
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(owner=user.employee_profile)
        
        # Filter by stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stage=stage)
        
        # Filter by client
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Filter by owner
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner_id=owner)
        
        # Filter won/lost
        is_won = self.request.query_params.get('is_won')
        if is_won is not None:
            queryset = queryset.filter(is_won=is_won.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(opportunity_number__icontains=search) |
                Q(name__icontains=search)
            )
        
        return queryset.select_related('client', 'owner')


class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete opportunity"""
    permission_classes = [IsAuthenticated]
    serializer_class = OpportunitySerializer
    
    def get_queryset(self):
        queryset = Opportunity.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their owned opportunities
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(owner=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def opportunity_move_stage(request, pk):
    """Move opportunity to different stage"""
    try:
        opportunity = Opportunity.objects.get(pk=pk, deleted_at__isnull=True)
    except Opportunity.DoesNotExist:
        return Response(
            {'error': 'Opportunity not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_stage = request.data.get('stage')
    if not new_stage:
        return Response(
            {'error': 'Stage is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update stage and probability
    stage_probability = {
        'prospecting': 10,
        'qualification': 25,
        'proposal': 50,
        'negotiation': 75,
        'closed_won': 100,
        'closed_lost': 0
    }
    
    opportunity.stage = new_stage
    opportunity.probability = stage_probability.get(new_stage, opportunity.probability)
    
    # Handle won/lost
    if new_stage == 'closed_won':
        opportunity.is_won = True
        opportunity.actual_close_date = timezone.now().date()
    elif new_stage == 'closed_lost':
        opportunity.is_won = False
        opportunity.actual_close_date = timezone.now().date()
        opportunity.win_loss_reason = request.data.get('reason', '')
    
    opportunity.save()
    
    serializer = OpportunitySerializer(opportunity)
    return Response(serializer.data)


# ============ Contract ============

class ContractListView(generics.ListCreateAPIView):
    """List and create contracts"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = ContractListSerializer
    
    def get_queryset(self):
        queryset = Contract.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by contract type
        contract_type = self.request.query_params.get('type')
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        
        # Filter by client
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Filter expiring soon
        expiring = self.request.query_params.get('expiring')
        if expiring and expiring.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='active',
                end_date__gte=today,
                end_date__lte=today + timedelta(days=F('renewal_notice_days'))
            )
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(title__icontains=search)
            )
        
        return queryset.select_related('client', 'owner')


class ContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete contract"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = ContractSerializer
    
    def get_queryset(self):
        return Contract.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Quotation ============

class QuotationListView(generics.ListCreateAPIView):
    """List and create quotations"""
    permission_classes = [IsAuthenticated]
    serializer_class = QuotationListSerializer
    
    def get_queryset(self):
        queryset = Quotation.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their prepared quotations
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(prepared_by=user.employee_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by client
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Filter by opportunity
        opportunity = self.request.query_params.get('opportunity')
        if opportunity:
            queryset = queryset.filter(opportunity_id=opportunity)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(quotation_number__icontains=search) |
                Q(title__icontains=search)
            )
        
        return queryset.select_related('client', 'prepared_by')


class QuotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete quotation"""
    permission_classes = [IsAuthenticated]
    serializer_class = QuotationSerializer
    
    def get_queryset(self):
        queryset = Quotation.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their prepared quotations
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(prepared_by=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quotation_accept(request, pk):
    """Accept a quotation"""
    try:
        quotation = Quotation.objects.get(pk=pk, deleted_at__isnull=True)
    except Quotation.DoesNotExist:
        return Response(
            {'error': 'Quotation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if quotation.status != 'sent':
        return Response(
            {'error': 'Only sent quotations can be accepted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Accept quotation
    quotation.status = 'accepted'
    quotation.accepted_at = timezone.now()
    quotation.save()
    
    serializer = QuotationSerializer(quotation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quotation_reject(request, pk):
    """Reject a quotation"""
    try:
        quotation = Quotation.objects.get(pk=pk, deleted_at__isnull=True)
    except Quotation.DoesNotExist:
        return Response(
            {'error': 'Quotation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if quotation.status != 'sent':
        return Response(
            {'error': 'Only sent quotations can be rejected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reject quotation
    quotation.status = 'rejected'
    quotation.rejected_at = timezone.now()
    quotation.rejection_reason = request.data.get('reason', '')
    quotation.save()
    
    serializer = QuotationSerializer(quotation)
    return Response(serializer.data)


# ============ Follow Up ============

class FollowUpListView(generics.ListCreateAPIView):
    """List and create follow-ups"""
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUpListSerializer
    
    def get_queryset(self):
        queryset = FollowUp.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their assigned follow-ups
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(assigned_to=user.employee_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter overdue
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            queryset = queryset.filter(
                status='planned',
                scheduled_date__lt=timezone.now()
            )
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('assigned_to', 'client', 'lead', 'opportunity')


class FollowUpDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete follow-up"""
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUpSerializer
    
    def get_queryset(self):
        queryset = FollowUp.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their assigned follow-ups
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(assigned_to=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def followup_complete(request, pk):
    """Mark follow-up as completed"""
    try:
        followup = FollowUp.objects.get(pk=pk, deleted_at__isnull=True)
    except FollowUp.DoesNotExist:
        return Response(
            {'error': 'Follow-up not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if followup.status != 'planned':
        return Response(
            {'error': 'Only planned follow-ups can be completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Complete follow-up
    followup.status = 'completed'
    followup.completed_date = timezone.now()
    followup.outcome = request.data.get('outcome', '')
    followup.next_action = request.data.get('next_action', '')
    followup.save()
    
    serializer = FollowUpSerializer(followup)
    return Response(serializer.data)


# ============ Dashboard ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crm_dashboard(request):
    """CRM dashboard with key metrics"""
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Lead metrics
    leads = Lead.objects.filter(deleted_at__isnull=True)
    
    total_leads = leads.count()
    new_leads_this_month = leads.filter(created_at__gte=current_month_start).count()
    qualified_leads = leads.filter(is_qualified=True).count()
    conversion_rate = (leads.filter(status='converted').count() / total_leads * 100) if total_leads > 0 else 0
    
    leads_by_source = leads.values('source').annotate(count=Count('id')).order_by('-count')
    
    # Opportunity metrics
    opportunities = Opportunity.objects.filter(deleted_at__isnull=True)
    
    total_opportunities = opportunities.count()
    active_opportunities = opportunities.exclude(stage__in=['closed_won', 'closed_lost']).count()
    
    pipeline_value = opportunities.exclude(stage__in=['closed_won', 'closed_lost']).aggregate(
        total=Coalesce(Sum('estimated_value'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    weighted_pipeline = opportunities.exclude(stage__in=['closed_won', 'closed_lost']).aggregate(
        total=Coalesce(
            Sum(F('estimated_value') * F('probability') / 100, output_field=DecimalField()),
            Decimal('0'),
            output_field=DecimalField()
        )
    )['total']
    
    won_revenue = opportunities.filter(is_won=True).aggregate(
        total=Coalesce(Sum('estimated_value'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    win_rate = (opportunities.filter(is_won=True).count() / 
                opportunities.filter(stage__in=['closed_won', 'closed_lost']).count() * 100) \
                if opportunities.filter(stage__in=['closed_won', 'closed_lost']).count() > 0 else 0
    
    opportunities_by_stage = opportunities.values('stage').annotate(
        count=Count('id'),
        value=Coalesce(Sum('estimated_value'), Decimal('0'), output_field=DecimalField())
    ).order_by('stage')
    
    # Client metrics
    clients = Client.objects.filter(deleted_at__isnull=True)
    
    total_clients = clients.count()
    active_clients = clients.filter(status='active').count()
    
    # Contract metrics
    contracts = Contract.objects.filter(deleted_at__isnull=True)
    
    active_contracts = contracts.filter(status='active').count()
    expiring_contracts = contracts.filter(
        status='active',
        end_date__gte=today,
        end_date__lte=today + timedelta(days=30)
    ).count()
    
    # Follow-up metrics
    followups = FollowUp.objects.filter(deleted_at__isnull=True)
    
    upcoming_followups = followups.filter(
        status='planned',
        scheduled_date__gte=today,
        scheduled_date__lte=today + timedelta(days=7)
    ).count()
    
    overdue_followups = followups.filter(
        status='planned',
        scheduled_date__lt=today
    ).count()
    
    return Response({
        'leads': {
            'total': total_leads,
            'new_this_month': new_leads_this_month,
            'qualified': qualified_leads,
            'conversion_rate': round(conversion_rate, 2),
            'by_source': [
                {
                    'source': item['source'],
                    'count': item['count']
                }
                for item in leads_by_source
            ]
        },
        'opportunities': {
            'total': total_opportunities,
            'active': active_opportunities,
            'pipeline_value': float(pipeline_value),
            'weighted_pipeline': float(weighted_pipeline),
            'won_revenue': float(won_revenue),
            'win_rate': round(win_rate, 2),
            'by_stage': [
                {
                    'stage': item['stage'],
                    'count': item['count'],
                    'value': float(item['value'])
                }
                for item in opportunities_by_stage
            ]
        },
        'clients': {
            'total': total_clients,
            'active': active_clients
        },
        'contracts': {
            'active': active_contracts,
            'expiring_soon': expiring_contracts
        },
        'follow_ups': {
            'upcoming_7_days': upcoming_followups,
            'overdue': overdue_followups
        }
    })
