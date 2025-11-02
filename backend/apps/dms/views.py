"""
Document Management System views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta

from apps.dms.models import (
    Document, DocumentCategory, DocumentVersion, DocumentApproval,
    DocumentAccess, DocumentTemplate, DocumentActivity
)
from apps.dms.serializers import (
    DocumentListSerializer, DocumentSerializer,
    DocumentCategorySerializer,
    DocumentVersionSerializer,
    DocumentApprovalSerializer,
    DocumentAccessSerializer,
    DocumentTemplateListSerializer, DocumentTemplateSerializer,
    DocumentActivitySerializer
)
from apps.core.permissions import IsAdminOrReadOnly


# ============= Document Category Views =============

class DocumentCategoryListView(generics.ListCreateAPIView):
    """List and create document categories"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DocumentCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = DocumentCategory.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        # Filter top level categories
        if self.request.query_params.get('top_level', None) == 'true':
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset


class DocumentCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a document category"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DocumentCategorySerializer
    queryset = DocumentCategory.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Document Views =============

class DocumentListView(generics.ListCreateAPIView):
    """List and create documents"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'document_type', 'category', 'owner', 'department', 'project', 'client', 'is_public']
    search_fields = ['document_number', 'title', 'description', 'tags', 'keywords', 'file_name']
    ordering_fields = ['created_at', 'title', 'file_size', 'download_count', 'view_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentSerializer
        return DocumentListSerializer
    
    def get_queryset(self):
        queryset = Document.objects.filter(deleted_at__isnull=True, is_latest_version=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            # Non-admin users see:
            # 1. Public documents
            # 2. Documents they own
            # 3. Documents with explicit access
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) |
                    Q(owner=user.employee) |
                    Q(access_permissions__employee=user.employee) |
                    Q(access_permissions__department=user.employee.department) |
                    Q(access_permissions__role__in=user.roles.all())
                ).distinct()
        
        # Filter expiring documents
        if self.request.query_params.get('expiring_soon', None) == 'true':
            thirty_days_later = timezone.now().date() + timedelta(days=30)
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=thirty_days_later,
                is_expired=False
            )
        
        # Filter expired documents
        if self.request.query_params.get('expired', None) == 'true':
            queryset = queryset.filter(is_expired=True)
        
        # Filter my documents
        if self.request.query_params.get('my_documents', None) == 'true':
            if hasattr(user, 'employee'):
                queryset = queryset.filter(owner=user.employee)
        
        # Filter pending approval
        if self.request.query_params.get('pending_approval', None) == 'true':
            queryset = queryset.filter(status='pending_approval')
        
        return queryset.select_related(
            'owner', 'category', 'department', 'project', 'client'
        )


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a document"""
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        queryset = Document.objects.filter(deleted_at__isnull=True)
        
        # Access control
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    Q(is_public=True) |
                    Q(owner=user.employee) |
                    Q(access_permissions__employee=user.employee) |
                    Q(access_permissions__department=user.employee.department) |
                    Q(access_permissions__role__in=user.roles.all())
                ).distinct()
        
        return queryset.select_related(
            'owner', 'category', 'department', 'project', 'client'
        )
    
    def retrieve(self, request, *args, **kwargs):
        # Log view activity
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        # Create activity log
        if hasattr(request.user, 'employee'):
            DocumentActivity.objects.create(
                document=instance,
                user=request.user.employee,
                activity_type='viewed',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()
        
        # Log deletion activity
        if hasattr(self.request.user, 'employee'):
            DocumentActivity.objects.create(
                document=instance,
                user=self.request.user.employee,
                activity_type='deleted',
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def document_download(request, pk):
    """Download a document"""
    try:
        document = Document.objects.get(pk=pk, deleted_at__isnull=True)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check download permission
    user = request.user
    if not document.is_public and not user.is_staff:
        if hasattr(user, 'employee'):
            has_access = DocumentAccess.objects.filter(
                document=document,
                can_download=True
            ).filter(
                Q(employee=user.employee) |
                Q(department=user.employee.department) |
                Q(role__in=user.roles.all())
            ).exists()
            
            if not has_access and document.owner != user.employee:
                return Response({'error': 'Download permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Increment download count
    document.download_count += 1
    document.save(update_fields=['download_count'])
    
    # Log download activity
    if hasattr(user, 'employee'):
        DocumentActivity.objects.create(
            document=document,
            user=user.employee,
            activity_type='downloaded',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    return Response({
        'file_url': document.file.url,
        'file_name': document.file_name
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def document_share(request, pk):
    """Share a document with users/departments"""
    try:
        document = Document.objects.get(pk=pk, deleted_at__isnull=True)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check share permission
    user = request.user
    if not user.is_staff and hasattr(user, 'employee'):
        if document.owner != user.employee:
            return Response({'error': 'Only owner can share document'}, status=status.HTTP_403_FORBIDDEN)
    
    # Create access permissions
    employee_ids = request.data.get('employee_ids', [])
    department_ids = request.data.get('department_ids', [])
    role_ids = request.data.get('role_ids', [])
    permissions = request.data.get('permissions', {})
    
    accesses_created = []
    
    for emp_id in employee_ids:
        access = DocumentAccess.objects.create(
            document=document,
            employee_id=emp_id,
            granted_by=user.employee if hasattr(user, 'employee') else document.owner,
            can_view=permissions.get('can_view', True),
            can_download=permissions.get('can_download', False),
            can_edit=permissions.get('can_edit', False),
            can_delete=permissions.get('can_delete', False),
            can_share=permissions.get('can_share', False)
        )
        accesses_created.append(access)
    
    for dept_id in department_ids:
        access = DocumentAccess.objects.create(
            document=document,
            department_id=dept_id,
            granted_by=user.employee if hasattr(user, 'employee') else document.owner,
            can_view=permissions.get('can_view', True),
            can_download=permissions.get('can_download', False),
            can_edit=permissions.get('can_edit', False),
            can_delete=permissions.get('can_delete', False),
            can_share=permissions.get('can_share', False)
        )
        accesses_created.append(access)
    
    for role_id in role_ids:
        access = DocumentAccess.objects.create(
            document=document,
            role_id=role_id,
            granted_by=user.employee if hasattr(user, 'employee') else document.owner,
            can_view=permissions.get('can_view', True),
            can_download=permissions.get('can_download', False),
            can_edit=permissions.get('can_edit', False),
            can_delete=permissions.get('can_delete', False),
            can_share=permissions.get('can_share', False)
        )
        accesses_created.append(access)
    
    # Log share activity
    if hasattr(user, 'employee'):
        DocumentActivity.objects.create(
            document=document,
            user=user.employee,
            activity_type='shared',
            description=f"Shared with {len(accesses_created)} recipients",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    serializer = DocumentAccessSerializer(accesses_created, many=True)
    return Response(serializer.data)


# ============= Document Version Views =============

class DocumentVersionListView(generics.ListCreateAPIView):
    """List and create document versions"""
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentVersionSerializer
    
    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        return DocumentVersion.objects.filter(
            document_id=document_id
        ).select_related('document', 'uploaded_by').order_by('-created_at')


# ============= Document Approval Views =============

class DocumentApprovalListView(generics.ListCreateAPIView):
    """List and create document approvals"""
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentApprovalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['document', 'approver', 'status']
    ordering = ['approval_level', 'created_at']
    
    def get_queryset(self):
        queryset = DocumentApproval.objects.filter(deleted_at__isnull=True)
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                # Show approvals assigned to user or created by user
                queryset = queryset.filter(
                    Q(approver=user.employee) |
                    Q(document__owner=user.employee)
                )
        
        # Filter pending approvals for current user
        if self.request.query_params.get('my_pending', None) == 'true':
            if hasattr(user, 'employee'):
                queryset = queryset.filter(
                    approver=user.employee,
                    status='pending'
                )
        
        return queryset.select_related('document', 'approver')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approval_approve(request, pk):
    """Approve a document"""
    try:
        approval = DocumentApproval.objects.get(pk=pk, deleted_at__isnull=True)
    except DocumentApproval.DoesNotExist:
        return Response({'error': 'Approval not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if current user is the approver
    user = request.user
    if hasattr(user, 'employee') and approval.approver != user.employee:
        return Response({'error': 'Only assigned approver can approve'}, status=status.HTTP_403_FORBIDDEN)
    
    if approval.status != 'pending':
        return Response({'error': 'Only pending approvals can be approved'}, status=status.HTTP_400_BAD_REQUEST)
    
    comments = request.data.get('comments', '')
    
    approval.status = 'approved'
    approval.approved_at = timezone.now()
    approval.comments = comments
    approval.save()
    
    # Check if all approvals are complete
    document = approval.document
    pending_approvals = document.approvals.filter(
        deleted_at__isnull=True,
        status='pending'
    ).exists()
    
    if not pending_approvals:
        # All approvals complete, update document status
        document.status = 'approved'
        document.save()
    
    serializer = DocumentApprovalSerializer(approval)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approval_reject(request, pk):
    """Reject a document"""
    try:
        approval = DocumentApproval.objects.get(pk=pk, deleted_at__isnull=True)
    except DocumentApproval.DoesNotExist:
        return Response({'error': 'Approval not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if current user is the approver
    user = request.user
    if hasattr(user, 'employee') and approval.approver != user.employee:
        return Response({'error': 'Only assigned approver can reject'}, status=status.HTTP_403_FORBIDDEN)
    
    if approval.status != 'pending':
        return Response({'error': 'Only pending approvals can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
    
    comments = request.data.get('comments', '')
    
    approval.status = 'rejected'
    approval.approved_at = timezone.now()
    approval.comments = comments
    approval.save()
    
    # Update document status
    document = approval.document
    document.status = 'rejected'
    document.save()
    
    serializer = DocumentApprovalSerializer(approval)
    return Response(serializer.data)


# ============= Document Access Views =============

class DocumentAccessListView(generics.ListCreateAPIView):
    """List and create document access permissions"""
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentAccessSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'employee', 'department', 'role']
    
    def get_queryset(self):
        queryset = DocumentAccess.objects.all()
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                # Show accesses for documents user owns
                queryset = queryset.filter(document__owner=user.employee)
        
        return queryset.select_related(
            'document', 'employee', 'department', 'role', 'granted_by'
        )


# ============= Document Template Views =============

class DocumentTemplateListView(generics.ListCreateAPIView):
    """List and create document templates"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'category']
    search_fields = ['name', 'description']
    ordering_fields = ['usage_count', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentTemplateSerializer
        return DocumentTemplateListSerializer
    
    def get_queryset(self):
        queryset = DocumentTemplate.objects.filter(deleted_at__isnull=True)
        
        # Filter active only
        if self.request.query_params.get('active_only', None) == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.select_related('category')


class DocumentTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a document template"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DocumentTemplateSerializer
    queryset = DocumentTemplate.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============= Document Activity Views =============

class DocumentActivityListView(generics.ListAPIView):
    """List document activities"""
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentActivitySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['document', 'user', 'activity_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        document_id = self.kwargs.get('document_id', None)
        queryset = DocumentActivity.objects.all()
        
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        
        # Filter by user permissions
        user = self.request.user
        if not user.is_staff:
            if hasattr(user, 'employee'):
                # Show activities for documents user owns or has access to
                queryset = queryset.filter(
                    Q(document__owner=user.employee) |
                    Q(user=user.employee)
                )
        
        return queryset.select_related('document', 'user')


# ============= Dashboard =============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dms_dashboard(request):
    """DMS dashboard with metrics"""
    
    # Document metrics
    all_documents = Document.objects.filter(deleted_at__isnull=True, is_latest_version=True)
    
    # Count by status
    doc_by_status = {}
    for status_key, status_label in Document.STATUS_CHOICES:
        count = all_documents.filter(status=status_key).count()
        doc_by_status[status_key] = {
            'label': status_label,
            'count': count
        }
    
    # Count by type
    doc_by_type = {}
    for type_key, type_label in Document.DOCUMENT_TYPE_CHOICES:
        count = all_documents.filter(document_type=type_key).count()
        doc_by_type[type_key] = {
            'label': type_label,
            'count': count
        }
    
    # Storage metrics
    total_storage_bytes = all_documents.aggregate(total=Sum('file_size'))['total'] or 0
    total_storage_gb = round(total_storage_bytes / (1024 ** 3), 2)
    
    # Expiring documents
    thirty_days_later = timezone.now().date() + timedelta(days=30)
    expiring_soon = all_documents.filter(
        expiry_date__isnull=False,
        expiry_date__lte=thirty_days_later,
        is_expired=False
    ).count()
    
    expired_count = all_documents.filter(is_expired=True).count()
    
    # Approval metrics
    pending_approvals = DocumentApproval.objects.filter(
        deleted_at__isnull=True,
        status='pending'
    ).count()
    
    # Activity metrics
    today = timezone.now().date()
    activities_today = DocumentActivity.objects.filter(
        created_at__date=today
    ).count()
    
    # Top categories
    category_stats = []
    for category in DocumentCategory.objects.filter(deleted_at__isnull=True, is_active=True)[:10]:
        doc_count = category.documents.filter(
            deleted_at__isnull=True,
            is_latest_version=True
        ).count()
        category_stats.append({
            'id': category.id,
            'name': category.name,
            'document_count': doc_count
        })
    
    # Recent documents
    recent_documents = all_documents.select_related('owner', 'category').order_by('-created_at')[:10]
    recent_documents_data = DocumentListSerializer(recent_documents, many=True).data
    
    # Most downloaded
    most_downloaded = all_documents.select_related('owner', 'category').order_by('-download_count')[:10]
    most_downloaded_data = DocumentListSerializer(most_downloaded, many=True).data
    
    return Response({
        'documents': {
            'total': all_documents.count(),
            'by_status': doc_by_status,
            'by_type': doc_by_type,
            'expiring_soon': expiring_soon,
            'expired': expired_count,
        },
        'storage': {
            'total_bytes': total_storage_bytes,
            'total_gb': total_storage_gb,
        },
        'approvals': {
            'pending': pending_approvals,
        },
        'activity': {
            'today': activities_today,
        },
        'categories': category_stats,
        'recent_documents': recent_documents_data,
        'most_downloaded': most_downloaded_data,
    })
