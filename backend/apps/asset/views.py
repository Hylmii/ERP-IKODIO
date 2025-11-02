"""
IT Asset & Inventory Management views
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
from apps.asset.models import (
    Asset, AssetCategory, Vendor, Procurement, ProcurementLine,
    AssetMaintenance, AssetAssignment, License
)
from apps.asset.serializers import (
    AssetCategorySerializer,
    VendorListSerializer, VendorSerializer,
    AssetListSerializer, AssetSerializer,
    ProcurementListSerializer, ProcurementSerializer, ProcurementLineSerializer,
    AssetMaintenanceListSerializer, AssetMaintenanceSerializer,
    AssetAssignmentSerializer,
    LicenseListSerializer, LicenseSerializer
)


# ============ Asset Category ============

class AssetCategoryListView(generics.ListCreateAPIView):
    """List and create asset categories"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = AssetCategorySerializer
    
    def get_queryset(self):
        queryset = AssetCategory.objects.filter(deleted_at__isnull=True)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search)
            )
        
        return queryset.order_by('name')


class AssetCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete asset category"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = AssetCategorySerializer
    
    def get_queryset(self):
        return AssetCategory.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Vendor ============

class VendorListView(generics.ListCreateAPIView):
    """List and create vendors"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = VendorListSerializer
    
    def get_queryset(self):
        queryset = Vendor.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('name')


class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete vendor"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = VendorSerializer
    
    def get_queryset(self):
        return Vendor.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Asset ============

class AssetListView(generics.ListCreateAPIView):
    """List and create assets"""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetListSerializer
    
    def get_queryset(self):
        queryset = Asset.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users can see all assets but with limited info
        # Filter by asset type
        asset_type = self.request.query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by assigned employee
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter my assets
        my_assets = self.request.query_params.get('my_assets')
        if my_assets and my_assets.lower() == 'true' and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(assigned_to=user.employee_profile)
        
        # Filter warranty expiring
        warranty_expiring = self.request.query_params.get('warranty_expiring')
        if warranty_expiring and warranty_expiring.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                warranty_end__gte=today,
                warranty_end__lte=today + timedelta(days=30)
            )
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(asset_number__icontains=search) |
                Q(name__icontains=search) |
                Q(serial_number__icontains=search)
            )
        
        return queryset.select_related('category', 'assigned_to', 'vendor')


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete asset"""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer
    
    def get_queryset(self):
        return Asset.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asset_assign(request, pk):
    """Assign asset to employee"""
    try:
        asset = Asset.objects.get(pk=pk, deleted_at__isnull=True)
    except Asset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if asset.status not in ['available']:
        return Response(
            {'error': f'Asset cannot be assigned (current status: {asset.status})'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    employee_id = request.data.get('employee_id')
    if not employee_id:
        return Response(
            {'error': 'employee_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create assignment record
    assignment = AssetAssignment.objects.create(
        asset=asset,
        employee_id=employee_id,
        assigned_date=timezone.now().date(),
        location=request.data.get('location', ''),
        condition_at_assignment=request.data.get('condition', 'Good'),
        notes=request.data.get('notes', ''),
        is_active=True
    )
    
    # Update asset
    asset.assigned_to_id = employee_id
    asset.assigned_date = timezone.now().date()
    asset.location = request.data.get('location', asset.location)
    asset.status = 'assigned'
    asset.save()
    
    serializer = AssetSerializer(asset)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asset_return(request, pk):
    """Return asset from employee"""
    try:
        asset = Asset.objects.get(pk=pk, deleted_at__isnull=True)
    except Asset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if asset.status != 'assigned':
        return Response(
            {'error': 'Asset is not currently assigned'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update active assignment
    active_assignment = asset.assignment_history.filter(is_active=True).first()
    if active_assignment:
        active_assignment.returned_date = timezone.now().date()
        active_assignment.condition_at_return = request.data.get('condition', 'Good')
        active_assignment.is_active = False
        active_assignment.save()
    
    # Update asset
    asset.assigned_to = None
    asset.assigned_date = None
    asset.status = 'available'
    asset.save()
    
    serializer = AssetSerializer(asset)
    return Response(serializer.data)


# ============ Procurement ============

class ProcurementListView(generics.ListCreateAPIView):
    """List and create procurements"""
    permission_classes = [IsAuthenticated]
    serializer_class = ProcurementListSerializer
    
    def get_queryset(self):
        queryset = Procurement.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their requests
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(requested_by=user.employee_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by vendor
        vendor = self.request.query_params.get('vendor')
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(procurement_number__icontains=search) |
                Q(title__icontains=search)
            )
        
        return queryset.select_related('requested_by', 'department', 'vendor')


class ProcurementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete procurement"""
    permission_classes = [IsAuthenticated]
    serializer_class = ProcurementSerializer
    
    def get_queryset(self):
        queryset = Procurement.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their requests
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(requested_by=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def procurement_approve(request, pk):
    """Approve a procurement request"""
    try:
        procurement = Procurement.objects.get(pk=pk, deleted_at__isnull=True)
    except Procurement.DoesNotExist:
        return Response(
            {'error': 'Procurement not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if procurement.status != 'submitted':
        return Response(
            {'error': 'Only submitted procurements can be approved'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Approve
    procurement.status = 'approved'
    procurement.approved_by = request.user.employee_profile
    procurement.approved_at = timezone.now()
    procurement.approval_notes = request.data.get('notes', '')
    procurement.save()
    
    serializer = ProcurementSerializer(procurement)
    return Response(serializer.data)


# ============ Asset Maintenance ============

class AssetMaintenanceListView(generics.ListCreateAPIView):
    """List and create asset maintenances"""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetMaintenanceListSerializer
    
    def get_queryset(self):
        queryset = AssetMaintenance.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by maintenance type
        maintenance_type = self.request.query_params.get('type')
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)
        
        # Filter by asset
        asset = self.request.query_params.get('asset')
        if asset:
            queryset = queryset.filter(asset_id=asset)
        
        # Filter by assigned technician
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter overdue
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            queryset = queryset.filter(
                status__in=['scheduled', 'in_progress'],
                scheduled_date__lt=timezone.now().date()
            )
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(maintenance_number__icontains=search) |
                Q(title__icontains=search)
            )
        
        return queryset.select_related('asset', 'assigned_to', 'vendor')


class AssetMaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete asset maintenance"""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetMaintenanceSerializer
    
    def get_queryset(self):
        return AssetMaintenance.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def maintenance_complete(request, pk):
    """Complete a maintenance"""
    try:
        maintenance = AssetMaintenance.objects.get(pk=pk, deleted_at__isnull=True)
    except AssetMaintenance.DoesNotExist:
        return Response(
            {'error': 'Maintenance not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if maintenance.status != 'in_progress':
        return Response(
            {'error': 'Only in-progress maintenances can be completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Complete maintenance
    maintenance.status = 'completed'
    maintenance.completion_date = timezone.now().date()
    maintenance.work_performed = request.data.get('work_performed', '')
    maintenance.parts_replaced = request.data.get('parts_replaced', '')
    maintenance.actual_cost = request.data.get('actual_cost')
    maintenance.next_maintenance_date = request.data.get('next_maintenance_date')
    maintenance.save()
    
    # Update asset status if it was under maintenance
    if maintenance.asset.status == 'maintenance':
        maintenance.asset.status = 'available'
        maintenance.asset.save()
    
    serializer = AssetMaintenanceSerializer(maintenance)
    return Response(serializer.data)


# ============ License ============

class LicenseListView(generics.ListCreateAPIView):
    """List and create licenses"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = LicenseListSerializer
    
    def get_queryset(self):
        queryset = License.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by license type
        license_type = self.request.query_params.get('type')
        if license_type:
            queryset = queryset.filter(license_type=license_type)
        
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
                Q(license_number__icontains=search) |
                Q(software_name__icontains=search)
            )
        
        return queryset.select_related('vendor', 'owner')


class LicenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete license"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = LicenseSerializer
    
    def get_queryset(self):
        return License.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Dashboard ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asset_dashboard(request):
    """Asset dashboard with key metrics"""
    today = timezone.now().date()
    
    # Asset metrics
    assets = Asset.objects.filter(deleted_at__isnull=True)
    
    total_assets = assets.count()
    assets_by_type = assets.values('asset_type').annotate(count=Count('id'))
    assets_by_status = assets.values('status').annotate(count=Count('id'))
    
    total_value = assets.aggregate(
        total=Coalesce(Sum('purchase_cost'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    current_value = assets.aggregate(
        total=Coalesce(Sum('current_value'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    # Warranty metrics
    warranty_expiring = assets.filter(
        warranty_end__gte=today,
        warranty_end__lte=today + timedelta(days=30)
    ).count()
    
    warranty_expired = assets.filter(warranty_end__lt=today).count()
    
    # License metrics
    licenses = License.objects.filter(deleted_at__isnull=True)
    
    total_licenses = licenses.count()
    active_licenses = licenses.filter(status='active').count()
    
    license_seats_total = licenses.aggregate(total=Sum('total_seats'))['total'] or 0
    license_seats_used = licenses.aggregate(total=Sum('used_seats'))['total'] or 0
    
    licenses_expiring = licenses.filter(
        status='active',
        end_date__gte=today,
        end_date__lte=today + timedelta(days=30)
    ).count()
    
    # Maintenance metrics
    maintenances = AssetMaintenance.objects.filter(deleted_at__isnull=True)
    
    upcoming_maintenance = maintenances.filter(
        status='scheduled',
        scheduled_date__gte=today,
        scheduled_date__lte=today + timedelta(days=7)
    ).count()
    
    overdue_maintenance = maintenances.filter(
        status__in=['scheduled', 'in_progress'],
        scheduled_date__lt=today
    ).count()
    
    # Procurement metrics
    procurements = Procurement.objects.filter(deleted_at__isnull=True)
    
    pending_approvals = procurements.filter(status='submitted').count()
    active_procurements = procurements.filter(status__in=['approved', 'ordered']).count()
    
    procurement_value = procurements.filter(status__in=['approved', 'ordered', 'received']).aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    return Response({
        'assets': {
            'total': total_assets,
            'by_type': [
                {
                    'type': item['asset_type'],
                    'count': item['count']
                }
                for item in assets_by_type
            ],
            'by_status': [
                {
                    'status': item['status'],
                    'count': item['count']
                }
                for item in assets_by_status
            ],
            'total_value': float(total_value),
            'current_value': float(current_value),
            'depreciation': float(total_value - current_value)
        },
        'warranty': {
            'expiring_soon': warranty_expiring,
            'expired': warranty_expired
        },
        'licenses': {
            'total': total_licenses,
            'active': active_licenses,
            'total_seats': license_seats_total,
            'used_seats': license_seats_used,
            'available_seats': license_seats_total - license_seats_used,
            'utilization_percentage': round((license_seats_used / license_seats_total * 100), 2) if license_seats_total > 0 else 0,
            'expiring_soon': licenses_expiring
        },
        'maintenance': {
            'upcoming_7_days': upcoming_maintenance,
            'overdue': overdue_maintenance
        },
        'procurement': {
            'pending_approvals': pending_approvals,
            'active': active_procurements,
            'total_value': float(procurement_value)
        }
    })
