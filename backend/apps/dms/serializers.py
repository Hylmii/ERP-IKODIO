"""
Document Management System serializers
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.dms.models import (
    Document, DocumentCategory, DocumentVersion, DocumentApproval,
    DocumentAccess, DocumentTemplate, DocumentActivity
)


# ============= Document Category Serializers =============

class DocumentCategorySerializer(serializers.ModelSerializer):
    """Serializer for document categories"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    document_count = serializers.SerializerMethodField()
    subcategory_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCategory
        fields = [
            'id', 'name', 'code', 'description',
            'parent', 'parent_name',
            'is_restricted', 'icon', 'color', 'is_active',
            'document_count', 'subcategory_count',
            'created_at', 'updated_at'
        ]
    
    def get_document_count(self, obj):
        """Count documents in this category"""
        return obj.documents.filter(deleted_at__isnull=True, is_latest_version=True).count()
    
    def get_subcategory_count(self, obj):
        """Count subcategories"""
        return obj.subcategories.filter(deleted_at__isnull=True).count()


# ============= Document Serializers =============

class DocumentListSerializer(serializers.ModelSerializer):
    """List serializer for documents"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    version_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'document_number', 'title', 'document_type', 'status',
            'owner', 'owner_name',
            'category', 'category_name',
            'department', 'department_name',
            'project', 'project_name',
            'client', 'client_name',
            'version', 'is_latest_version',
            'file_name', 'file_extension', 'file_size', 'file_size_mb',
            'expiry_date', 'is_expired', 'is_expiring_soon', 'days_until_expiry',
            'is_public', 'is_confidential',
            'view_count', 'download_count', 'version_count',
            'created_at', 'updated_at'
        ]
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        return round(obj.file_size / (1024 * 1024), 2)
    
    def get_is_expiring_soon(self, obj):
        """Check if expiring within 30 days"""
        if not obj.expiry_date:
            return False
        
        days_left = (obj.expiry_date - timezone.now().date()).days
        return 0 < days_left <= 30
    
    def get_days_until_expiry(self, obj):
        """Calculate days until expiry"""
        if not obj.expiry_date:
            return None
        
        days_left = (obj.expiry_date - timezone.now().date()).days
        return days_left
    
    def get_version_count(self, obj):
        """Count document versions"""
        return obj.version_history.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Detail serializer for documents"""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    pending_approvals = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
    
    def get_file_size_mb(self, obj):
        """File size in MB"""
        serializer = DocumentListSerializer()
        return serializer.get_file_size_mb(obj)
    
    def get_is_expiring_soon(self, obj):
        """Expiring soon check"""
        serializer = DocumentListSerializer()
        return serializer.get_is_expiring_soon(obj)
    
    def get_days_until_expiry(self, obj):
        """Days until expiry"""
        serializer = DocumentListSerializer()
        return serializer.get_days_until_expiry(obj)
    
    def get_versions(self, obj):
        """Get version history"""
        versions = obj.version_history.order_by('-created_at')[:5]
        return DocumentVersionSerializer(versions, many=True).data
    
    def get_pending_approvals(self, obj):
        """Get pending approvals"""
        approvals = obj.approvals.filter(deleted_at__isnull=True, status='pending')
        return DocumentApprovalSerializer(approvals, many=True).data


# ============= Document Version Serializers =============

class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for document versions"""
    
    document_title = serializers.CharField(source='document.title', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'document_title',
            'version_number', 'file', 'file_size', 'file_size_mb',
            'checksum', 'change_summary',
            'uploaded_by', 'uploaded_by_name',
            'created_at'
        ]
    
    def get_file_size_mb(self, obj):
        """File size in MB"""
        return round(obj.file_size / (1024 * 1024), 2)


# ============= Document Approval Serializers =============

class DocumentApprovalSerializer(serializers.ModelSerializer):
    """Serializer for document approvals"""
    
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_number = serializers.CharField(source='document.document_number', read_only=True)
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentApproval
        fields = [
            'id', 'document', 'document_title', 'document_number',
            'approver', 'approver_name',
            'status', 'approval_level', 'due_date',
            'is_overdue', 'days_until_due',
            'approved_at', 'comments', 'signature',
            'created_at', 'updated_at'
        ]
    
    def get_is_overdue(self, obj):
        """Check if approval is overdue"""
        if obj.status != 'pending' or not obj.due_date:
            return False
        
        return timezone.now().date() > obj.due_date
    
    def get_days_until_due(self, obj):
        """Calculate days until due"""
        if not obj.due_date or obj.status != 'pending':
            return None
        
        days_left = (obj.due_date - timezone.now().date()).days
        return days_left


# ============= Document Access Serializers =============

class DocumentAccessSerializer(serializers.ModelSerializer):
    """Serializer for document access permissions"""
    
    document_title = serializers.CharField(source='document.title', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.get_full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentAccess
        fields = [
            'id', 'document', 'document_title',
            'employee', 'employee_name',
            'department', 'department_name',
            'role', 'role_name',
            'can_view', 'can_download', 'can_edit', 'can_delete', 'can_share',
            'expires_at', 'is_expired',
            'granted_by', 'granted_by_name',
            'created_at'
        ]
    
    def get_is_expired(self, obj):
        """Check if access has expired"""
        if not obj.expires_at:
            return False
        
        return timezone.now() > obj.expires_at


# ============= Document Template Serializers =============

class DocumentTemplateListSerializer(serializers.ModelSerializer):
    """List serializer for document templates"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'template_type',
            'category', 'category_name',
            'file_extension', 'usage_count', 'is_active',
            'created_at'
        ]


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Detail serializer for document templates"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = DocumentTemplate
        fields = '__all__'


# ============= Document Activity Serializers =============

class DocumentActivitySerializer(serializers.ModelSerializer):
    """Serializer for document activities"""
    
    document_title = serializers.CharField(source='document.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentActivity
        fields = [
            'id', 'document', 'document_title',
            'user', 'user_name',
            'activity_type', 'description',
            'ip_address', 'user_agent', 'metadata',
            'created_at'
        ]
