"""
CRM & Sales serializers
"""
from rest_framework import serializers
from django.db.models import Sum, Count, Q
from apps.crm.models import (
    Client, Lead, Opportunity, Contract, Quotation, QuotationLine, FollowUp
)


# ============ Client ============

class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight client list"""
    account_manager_name = serializers.CharField(source='account_manager.full_name', read_only=True)
    opportunity_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'code', 'name', 'client_type', 'email', 'phone',
            'city', 'province', 'status', 'account_manager_name',
            'rating', 'opportunity_count', 'total_revenue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_opportunity_count(self, obj):
        return obj.opportunities.count()
    
    def get_total_revenue(self, obj):
        from apps.finance.models import Invoice
        total = Invoice.objects.filter(
            client=obj,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total']
        return float(total or 0)


class ClientSerializer(serializers.ModelSerializer):
    """Full client serializer"""
    account_manager_name = serializers.CharField(source='account_manager.full_name', read_only=True)
    opportunity_count = serializers.SerializerMethodField()
    active_contracts = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'code', 'name', 'client_type', 'email', 'phone', 'mobile', 'website',
            'address', 'city', 'province', 'postal_code', 'country',
            'tax_id', 'company_registration', 'industry',
            'contact_person_name', 'contact_person_title',
            'contact_person_email', 'contact_person_phone',
            'status', 'account_manager', 'account_manager_name',
            'credit_limit', 'payment_terms_days', 'rating',
            'notes', 'tags', 'opportunity_count', 'active_contracts', 'total_revenue',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_opportunity_count(self, obj):
        return obj.opportunities.filter(stage__in=['prospecting', 'qualification', 'proposal', 'negotiation']).count()
    
    def get_active_contracts(self, obj):
        return obj.contracts.filter(status='active').count()
    
    def get_total_revenue(self, obj):
        from apps.finance.models import Invoice
        total = Invoice.objects.filter(
            client=obj,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total']
        return float(total or 0)


# ============ Lead ============

class LeadListSerializer(serializers.ModelSerializer):
    """Lightweight lead list"""
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'lead_number', 'company_name', 'contact_name', 'email', 'phone',
            'source', 'status', 'estimated_value', 'is_qualified',
            'assigned_to_name', 'days_since_created',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_since_created(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days


class LeadSerializer(serializers.ModelSerializer):
    """Full lead serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    converted_opportunity_number = serializers.CharField(
        source='converted_opportunity.opportunity_number', read_only=True
    )
    days_since_created = serializers.SerializerMethodField()
    follow_up_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'lead_number', 'company_name', 'contact_name', 'title',
            'email', 'phone', 'mobile', 'city', 'province', 'country',
            'source', 'industry', 'estimated_value',
            'assigned_to', 'assigned_to_name', 'status',
            'is_qualified', 'qualified_at',
            'converted_opportunity', 'converted_opportunity_number', 'converted_at',
            'description', 'notes', 'days_since_created', 'follow_up_count',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'qualified_at', 'converted_at', 'created_at', 'updated_at', 'deleted_at']
    
    def get_days_since_created(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days
    
    def get_follow_up_count(self, obj):
        return obj.follow_ups.count()


# ============ Opportunity ============

class OpportunityListSerializer(serializers.ModelSerializer):
    """Lightweight opportunity list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    weighted_value = serializers.SerializerMethodField()
    days_in_stage = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'opportunity_number', 'name', 'client_name', 'stage',
            'probability', 'estimated_value', 'expected_revenue',
            'weighted_value', 'expected_close_date', 'owner_name',
            'days_in_stage', 'is_won',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_weighted_value(self, obj):
        return float(obj.estimated_value * obj.probability / 100)
    
    def get_days_in_stage(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.updated_at).days


class OpportunitySerializer(serializers.ModelSerializer):
    """Full opportunity serializer"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    weighted_value = serializers.SerializerMethodField()
    days_in_stage = serializers.SerializerMethodField()
    quotation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'opportunity_number', 'name', 'description',
            'client', 'client_name', 'lead', 'lead_number',
            'stage', 'probability', 'estimated_value', 'expected_revenue',
            'weighted_value', 'currency',
            'expected_close_date', 'actual_close_date',
            'owner', 'owner_name', 'competitors',
            'is_won', 'win_loss_reason',
            'project', 'project_name', 'notes',
            'days_in_stage', 'quotation_count',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'actual_close_date', 'created_at', 'updated_at', 'deleted_at']
    
    def get_weighted_value(self, obj):
        return float(obj.estimated_value * obj.probability / 100)
    
    def get_days_in_stage(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.updated_at).days
    
    def get_quotation_count(self, obj):
        return obj.quotations.count()


# ============ Contract ============

class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight contract list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'contract_type', 'title',
            'client_name', 'status', 'start_date', 'end_date',
            'contract_value', 'currency', 'owner_name',
            'days_until_expiry', 'is_expiring_soon',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_until_expiry(self, obj):
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return delta.days
        return None
    
    def get_is_expiring_soon(self, obj):
        days = self.get_days_until_expiry(obj)
        return days is not None and 0 < days <= obj.renewal_notice_days


class ContractSerializer(serializers.ModelSerializer):
    """Full contract serializer"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    opportunity_number = serializers.CharField(source='opportunity.opportunity_number', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'contract_type', 'title', 'description',
            'client', 'client_name',
            'opportunity', 'opportunity_number', 'project', 'project_name',
            'start_date', 'end_date', 'signed_date',
            'contract_value', 'currency', 'status',
            'is_auto_renewable', 'renewal_notice_days',
            'payment_terms', 'terms_and_conditions',
            'owner', 'owner_name',
            'contract_file', 'signed_contract_file', 'notes',
            'days_until_expiry', 'is_expiring_soon',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_days_until_expiry(self, obj):
        from django.utils import timezone
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return delta.days
        return None
    
    def get_is_expiring_soon(self, obj):
        days = self.get_days_until_expiry(obj)
        return days is not None and 0 < days <= obj.renewal_notice_days


# ============ Quotation ============

class QuotationLineSerializer(serializers.ModelSerializer):
    """Quotation line item serializer"""
    
    class Meta:
        model = QuotationLine
        fields = [
            'id', 'description', 'quantity', 'unit_price',
            'discount_percentage', 'amount', 'line_number', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuotationListSerializer(serializers.ModelSerializer):
    """Lightweight quotation list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    prepared_by_name = serializers.CharField(source='prepared_by.full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'title', 'client_name',
            'quotation_date', 'valid_until', 'total_amount', 'currency',
            'status', 'prepared_by_name', 'days_until_expiry',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_until_expiry(self, obj):
        from django.utils import timezone
        if obj.valid_until:
            delta = obj.valid_until - timezone.now().date()
            return delta.days
        return None


class QuotationSerializer(serializers.ModelSerializer):
    """Full quotation serializer"""
    lines = QuotationLineSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    opportunity_number = serializers.CharField(source='opportunity.opportunity_number', read_only=True)
    prepared_by_name = serializers.CharField(source='prepared_by.full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'title', 'description',
            'client', 'client_name', 'opportunity', 'opportunity_number',
            'quotation_date', 'valid_until',
            'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
            'currency', 'tax_percentage', 'status',
            'prepared_by', 'prepared_by_name',
            'accepted_at', 'rejected_at', 'rejection_reason',
            'payment_terms', 'notes', 'terms_and_conditions',
            'quotation_file', 'lines', 'days_until_expiry',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'accepted_at', 'rejected_at', 'created_at', 'updated_at', 'deleted_at']
    
    def get_days_until_expiry(self, obj):
        from django.utils import timezone
        if obj.valid_until:
            delta = obj.valid_until - timezone.now().date()
            return delta.days
        return None


# ============ Follow Up ============

class FollowUpListSerializer(serializers.ModelSerializer):
    """Lightweight follow-up list"""
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)
    opportunity_number = serializers.CharField(source='opportunity.opportunity_number', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = FollowUp
        fields = [
            'id', 'activity_type', 'subject', 'scheduled_date',
            'status', 'assigned_to_name', 'client_name',
            'lead_number', 'opportunity_number', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.status == 'planned':
            return obj.scheduled_date < timezone.now()
        return False


class FollowUpSerializer(serializers.ModelSerializer):
    """Full follow-up serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    lead_number = serializers.CharField(source='lead.lead_number', read_only=True)
    opportunity_number = serializers.CharField(source='opportunity.opportunity_number', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = FollowUp
        fields = [
            'id', 'lead', 'lead_number', 'opportunity', 'opportunity_number',
            'client', 'client_name', 'activity_type', 'subject', 'description',
            'scheduled_date', 'completed_date',
            'assigned_to', 'assigned_to_name', 'status',
            'outcome', 'next_action', 'send_reminder', 'reminder_sent',
            'is_overdue',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'completed_date', 'reminder_sent', 'created_at', 'updated_at', 'deleted_at']
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.status == 'planned':
            return obj.scheduled_date < timezone.now()
        return False
