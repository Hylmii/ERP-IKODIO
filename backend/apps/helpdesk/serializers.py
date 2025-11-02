"""
Helpdesk/Support/Ticketing System serializers
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.helpdesk.models import (
    Ticket, TicketComment, SLAPolicy, TicketEscalation,
    KnowledgeBase, TicketTemplate
)
from apps.hr.models import Employee, Department
from apps.crm.models import Client


# ============= Ticket Serializers =============

class TicketListSerializer(serializers.ModelSerializer):
    """List serializer for tickets"""
    
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    sla_status = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    age_hours = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'category', 'priority', 'status',
            'requester', 'requester_name', 'requester_email',
            'assigned_to', 'assigned_to_name', 'assigned_team', 'assigned_team_name',
            'client', 'client_name',
            'due_date', 'response_due', 'resolution_due',
            'sla_status', 'is_overdue', 'age_hours',
            'satisfaction_rating', 'comment_count',
            'created_at', 'updated_at'
        ]
    
    def get_sla_status(self, obj):
        """Check SLA compliance status"""
        if not obj.sla_policy:
            return 'no_sla'
        
        now = timezone.now()
        
        # Check resolution SLA
        if obj.resolution_due:
            if obj.status in ['resolved', 'closed']:
                # Check if resolved within SLA
                if obj.resolved_at and obj.resolved_at <= obj.resolution_due:
                    return 'met'
                else:
                    return 'breached'
            else:
                # Still open, check if overdue
                if now > obj.resolution_due:
                    return 'breached'
                else:
                    # Check if approaching deadline (< 25% time remaining)
                    created_time = obj.created_at
                    total_time = (obj.resolution_due - created_time).total_seconds()
                    remaining_time = (obj.resolution_due - now).total_seconds()
                    
                    if remaining_time / total_time < 0.25:
                        return 'warning'
                    return 'on_track'
        
        return 'no_sla'
    
    def get_is_overdue(self, obj):
        """Check if ticket is overdue"""
        if obj.status in ['resolved', 'closed', 'cancelled']:
            return False
        
        if obj.resolution_due and timezone.now() > obj.resolution_due:
            return True
        
        return False
    
    def get_age_hours(self, obj):
        """Calculate ticket age in hours"""
        if obj.status in ['resolved', 'closed']:
            end_time = obj.closed_at or obj.resolved_at or timezone.now()
        else:
            end_time = timezone.now()
        
        age = end_time - obj.created_at
        return round(age.total_seconds() / 3600, 2)
    
    def get_comment_count(self, obj):
        """Count ticket comments"""
        return obj.comments.filter(deleted_at__isnull=True).count()


class TicketSerializer(serializers.ModelSerializer):
    """Detail serializer for tickets"""
    
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    sla_policy_name = serializers.CharField(source='sla_policy.name', read_only=True)
    sla_status = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    age_hours = serializers.SerializerMethodField()
    time_to_first_response_hours = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = '__all__'
    
    def get_sla_status(self, obj):
        """SLA compliance status"""
        serializer = TicketListSerializer()
        return serializer.get_sla_status(obj)
    
    def get_is_overdue(self, obj):
        """Check if overdue"""
        serializer = TicketListSerializer()
        return serializer.get_is_overdue(obj)
    
    def get_age_hours(self, obj):
        """Ticket age"""
        serializer = TicketListSerializer()
        return serializer.get_age_hours(obj)
    
    def get_time_to_first_response_hours(self, obj):
        """Calculate time to first response"""
        if obj.first_response_at:
            delta = obj.first_response_at - obj.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def get_comments(self, obj):
        """Get ticket comments"""
        comments = obj.comments.filter(deleted_at__isnull=True).order_by('created_at')
        return TicketCommentSerializer(comments, many=True).data


# ============= Ticket Comment Serializers =============

class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'author', 'author_name',
            'comment', 'is_internal', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author']


# ============= SLA Policy Serializers =============

class SLAPolicyListSerializer(serializers.ModelSerializer):
    """List serializer for SLA policies"""
    
    active_ticket_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SLAPolicy
        fields = [
            'id', 'name', 'priority',
            'response_time_hours', 'resolution_time_hours',
            'is_business_hours_only', 'include_weekends',
            'is_active', 'active_ticket_count',
            'created_at'
        ]
    
    def get_active_ticket_count(self, obj):
        """Count active tickets using this SLA"""
        return obj.tickets.filter(
            deleted_at__isnull=True,
            status__in=['new', 'open', 'in_progress', 'pending']
        ).count()


class SLAPolicySerializer(serializers.ModelSerializer):
    """Detail serializer for SLA policies"""
    
    active_ticket_count = serializers.SerializerMethodField()
    compliance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SLAPolicy
        fields = '__all__'
    
    def get_active_ticket_count(self, obj):
        """Count active tickets"""
        serializer = SLAPolicyListSerializer()
        return serializer.get_active_ticket_count(obj)
    
    def get_compliance_rate(self, obj):
        """Calculate SLA compliance rate"""
        resolved_tickets = obj.tickets.filter(
            deleted_at__isnull=True,
            status__in=['resolved', 'closed']
        )
        
        total_count = resolved_tickets.count()
        if total_count == 0:
            return None
        
        # Count tickets resolved within SLA
        compliant_count = 0
        for ticket in resolved_tickets:
            if ticket.resolved_at and ticket.resolution_due:
                if ticket.resolved_at <= ticket.resolution_due:
                    compliant_count += 1
        
        return round((compliant_count / total_count) * 100, 2)


# ============= Ticket Escalation Serializers =============

class TicketEscalationSerializer(serializers.ModelSerializer):
    """Serializer for ticket escalations"""
    
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    escalated_from_name = serializers.CharField(source='escalated_from.get_full_name', read_only=True)
    escalated_to_name = serializers.CharField(source='escalated_to.get_full_name', read_only=True)
    
    class Meta:
        model = TicketEscalation
        fields = [
            'id', 'ticket', 'ticket_number',
            'escalated_from', 'escalated_from_name',
            'escalated_to', 'escalated_to_name',
            'reason', 'escalation_level',
            'resolved', 'resolved_at',
            'created_at'
        ]


# ============= Knowledge Base Serializers =============

class KnowledgeBaseListSerializer(serializers.ModelSerializer):
    """List serializer for knowledge base articles"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    helpfulness_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'article_number', 'title', 'summary', 'category', 'status',
            'author', 'author_name',
            'view_count', 'helpful_count', 'not_helpful_count', 'helpfulness_rate',
            'keywords', 'tags',
            'published_at', 'created_at', 'updated_at'
        ]
    
    def get_helpfulness_rate(self, obj):
        """Calculate helpfulness percentage"""
        total_votes = obj.helpful_count + obj.not_helpful_count
        if total_votes == 0:
            return None
        return round((obj.helpful_count / total_votes) * 100, 2)


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """Detail serializer for knowledge base articles"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    helpfulness_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = '__all__'
    
    def get_helpfulness_rate(self, obj):
        """Helpfulness percentage"""
        serializer = KnowledgeBaseListSerializer()
        return serializer.get_helpfulness_rate(obj)


# ============= Ticket Template Serializers =============

class TicketTemplateListSerializer(serializers.ModelSerializer):
    """List serializer for ticket templates"""
    
    default_assigned_team_name = serializers.CharField(source='default_assigned_team.name', read_only=True)
    sla_policy_name = serializers.CharField(source='sla_policy.name', read_only=True)
    
    class Meta:
        model = TicketTemplate
        fields = [
            'id', 'name', 'description',
            'default_category', 'default_priority',
            'default_assigned_team', 'default_assigned_team_name',
            'sla_policy', 'sla_policy_name',
            'is_active', 'usage_count',
            'created_at'
        ]


class TicketTemplateSerializer(serializers.ModelSerializer):
    """Detail serializer for ticket templates"""
    
    default_assigned_team_name = serializers.CharField(source='default_assigned_team.name', read_only=True)
    sla_policy_name = serializers.CharField(source='sla_policy.name', read_only=True)
    
    class Meta:
        model = TicketTemplate
        fields = '__all__'
