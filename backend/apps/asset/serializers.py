"""
IT Asset & Inventory Management serializers
"""
from rest_framework import serializers
from django.db.models import Sum, Count
from apps.asset.models import (
    Asset, AssetCategory, Vendor, Procurement, ProcurementLine,
    AssetMaintenance, AssetAssignment, License
)


# ============ Asset Category ============

class AssetCategorySerializer(serializers.ModelSerializer):
    """Asset category serializer"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCategory
        fields = [
            'id', 'code', 'name', 'description', 'parent', 'parent_name',
            'is_active', 'asset_count',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_asset_count(self, obj):
        return obj.assets.filter(deleted_at__isnull=True).count()


# ============ Vendor ============

class VendorListSerializer(serializers.ModelSerializer):
    """Lightweight vendor list"""
    asset_count = serializers.SerializerMethodField()
    procurement_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'code', 'name', 'email', 'phone',
            'city', 'province', 'status', 'rating',
            'asset_count', 'procurement_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_asset_count(self, obj):
        return obj.assets.filter(deleted_at__isnull=True).count()
    
    def get_procurement_count(self, obj):
        return obj.procurements.filter(deleted_at__isnull=True).count()


class VendorSerializer(serializers.ModelSerializer):
    """Full vendor serializer"""
    asset_count = serializers.SerializerMethodField()
    procurement_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'code', 'name', 'email', 'phone', 'website',
            'address', 'city', 'province', 'postal_code', 'country',
            'tax_id', 'contact_person_name', 'contact_person_phone',
            'contact_person_email', 'status', 'rating',
            'payment_terms_days', 'notes',
            'asset_count', 'procurement_count',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_asset_count(self, obj):
        return obj.assets.filter(deleted_at__isnull=True).count()
    
    def get_procurement_count(self, obj):
        return obj.procurements.filter(deleted_at__isnull=True).count()


# ============ Asset ============

class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight asset list"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    is_warranty_valid = serializers.SerializerMethodField()
    is_license_expiring = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_number', 'name', 'asset_type', 'category_name',
            'manufacturer', 'model_number', 'serial_number',
            'status', 'assigned_to_name', 'location', 'vendor_name',
            'purchase_date', 'purchase_cost', 'current_value',
            'is_warranty_valid', 'is_license_expiring',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_warranty_valid(self, obj):
        if obj.warranty_end:
            from django.utils import timezone
            return obj.warranty_end >= timezone.now().date()
        return False
    
    def get_is_license_expiring(self, obj):
        if obj.asset_type in ['software', 'license'] and obj.license_end:
            from django.utils import timezone
            from datetime import timedelta
            return timezone.now().date() <= obj.license_end <= timezone.now().date() + timedelta(days=30)
        return False


class AssetSerializer(serializers.ModelSerializer):
    """Full asset serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    depreciation_amount = serializers.SerializerMethodField()
    is_warranty_valid = serializers.SerializerMethodField()
    warranty_days_left = serializers.SerializerMethodField()
    license_utilization = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_number', 'name', 'description', 'asset_type',
            'category', 'category_name', 'manufacturer', 'model_number',
            'serial_number', 'vendor', 'vendor_name',
            'purchase_date', 'purchase_cost', 'currency',
            'warranty_start', 'warranty_end', 'warranty_provider',
            'license_key', 'license_start', 'license_end',
            'license_seats', 'license_used_seats',
            'assigned_to', 'assigned_to_name', 'assigned_date', 'location',
            'status', 'depreciation_method', 'useful_life_years',
            'salvage_value', 'current_value', 'depreciation_amount',
            'image', 'documents', 'notes', 'tags',
            'is_warranty_valid', 'warranty_days_left', 'license_utilization',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'assigned_date', 'created_at', 'updated_at', 'deleted_at']
    
    def get_depreciation_amount(self, obj):
        if obj.purchase_cost and obj.current_value:
            return float(obj.purchase_cost - obj.current_value)
        return 0
    
    def get_is_warranty_valid(self, obj):
        if obj.warranty_end:
            from django.utils import timezone
            return obj.warranty_end >= timezone.now().date()
        return False
    
    def get_warranty_days_left(self, obj):
        if obj.warranty_end:
            from django.utils import timezone
            delta = obj.warranty_end - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_license_utilization(self, obj):
        if obj.asset_type in ['software', 'license'] and obj.license_seats:
            return round((obj.license_used_seats / obj.license_seats) * 100, 2)
        return None


# ============ Procurement ============

class ProcurementLineSerializer(serializers.ModelSerializer):
    """Procurement line item serializer"""
    asset_category_name = serializers.CharField(source='asset_category.name', read_only=True)
    quantity_pending = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementLine
        fields = [
            'id', 'description', 'quantity', 'unit_price', 'amount',
            'asset_category', 'asset_category_name',
            'quantity_received', 'quantity_pending', 'line_number', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_quantity_pending(self, obj):
        return float(obj.quantity - obj.quantity_received)


class ProcurementListSerializer(serializers.ModelSerializer):
    """Lightweight procurement list"""
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    
    class Meta:
        model = Procurement
        fields = [
            'id', 'procurement_number', 'title', 'requested_by_name',
            'department_name', 'vendor_name', 'request_date', 'required_date',
            'total_amount', 'currency', 'priority', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProcurementSerializer(serializers.ModelSerializer):
    """Full procurement serializer"""
    lines = ProcurementLineSerializer(many=True, read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Procurement
        fields = [
            'id', 'procurement_number', 'title', 'description',
            'requested_by', 'requested_by_name',
            'department', 'department_name',
            'vendor', 'vendor_name', 'priority', 'status',
            'request_date', 'required_date', 'ordered_date', 'received_date',
            'total_amount', 'currency', 'budget',
            'approved_by', 'approved_by_name', 'approved_at', 'approval_notes',
            'po_number', 'notes', 'attachments', 'lines',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'approved_at', 'ordered_date', 'received_date', 'created_at', 'updated_at', 'deleted_at']


# ============ Asset Maintenance ============

class AssetMaintenanceListSerializer(serializers.ModelSerializer):
    """Lightweight maintenance list"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_number = serializers.CharField(source='asset.asset_number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetMaintenance
        fields = [
            'id', 'maintenance_number', 'asset_number', 'asset_name',
            'maintenance_type', 'title', 'scheduled_date',
            'status', 'assigned_to_name', 'vendor_name',
            'estimated_cost', 'actual_cost', 'currency',
            'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_overdue(self, obj):
        if obj.status in ['scheduled', 'in_progress']:
            from django.utils import timezone
            return obj.scheduled_date < timezone.now().date()
        return False


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    """Full maintenance serializer"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_number = serializers.CharField(source='asset.asset_number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetMaintenance
        fields = [
            'id', 'asset', 'asset_number', 'asset_name',
            'maintenance_number', 'maintenance_type', 'title', 'description',
            'scheduled_date', 'start_date', 'completion_date',
            'assigned_to', 'assigned_to_name', 'vendor', 'vendor_name',
            'status', 'estimated_cost', 'actual_cost', 'currency',
            'work_performed', 'parts_replaced', 'next_maintenance_date',
            'notes', 'attachments', 'is_overdue',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'start_date', 'completion_date', 'created_at', 'updated_at', 'deleted_at']
    
    def get_is_overdue(self, obj):
        if obj.status in ['scheduled', 'in_progress']:
            from django.utils import timezone
            return obj.scheduled_date < timezone.now().date()
        return False


# ============ Asset Assignment ============

class AssetAssignmentSerializer(serializers.ModelSerializer):
    """Asset assignment history serializer"""
    asset_number = serializers.CharField(source='asset.asset_number', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    days_assigned = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetAssignment
        fields = [
            'id', 'asset', 'asset_number', 'asset_name',
            'employee', 'employee_name', 'assigned_date', 'returned_date',
            'location', 'condition_at_assignment', 'condition_at_return',
            'is_active', 'notes', 'days_assigned',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_assigned(self, obj):
        from django.utils import timezone
        end_date = obj.returned_date or timezone.now().date()
        return (end_date - obj.assigned_date).days


# ============ License ============

class LicenseListSerializer(serializers.ModelSerializer):
    """Lightweight license list"""
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    available_seats = serializers.ReadOnlyField()
    utilization_percentage = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = License
        fields = [
            'id', 'license_number', 'software_name', 'version',
            'publisher', 'license_type', 'total_seats', 'used_seats',
            'available_seats', 'utilization_percentage',
            'start_date', 'end_date', 'status', 'vendor_name', 'owner_name',
            'days_until_expiry', 'is_expiring_soon',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_utilization_percentage(self, obj):
        if obj.total_seats > 0:
            return round((obj.used_seats / obj.total_seats) * 100, 2)
        return 0
    
    def get_days_until_expiry(self, obj):
        if obj.end_date:
            from django.utils import timezone
            delta = obj.end_date - timezone.now().date()
            return delta.days
        return None
    
    def get_is_expiring_soon(self, obj):
        days = self.get_days_until_expiry(obj)
        return days is not None and 0 < days <= obj.renewal_notice_days


class LicenseSerializer(serializers.ModelSerializer):
    """Full license serializer"""
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    available_seats = serializers.ReadOnlyField()
    utilization_percentage = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = License
        fields = [
            'id', 'license_number', 'software_name', 'version', 'publisher',
            'license_type', 'license_key', 'total_seats', 'used_seats',
            'available_seats', 'utilization_percentage',
            'purchase_date', 'start_date', 'end_date', 'status',
            'purchase_cost', 'annual_cost', 'currency',
            'vendor', 'vendor_name', 'is_auto_renewable', 'renewal_notice_days',
            'owner', 'owner_name', 'notes', 'documents',
            'days_until_expiry', 'is_expiring_soon',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_utilization_percentage(self, obj):
        if obj.total_seats > 0:
            return round((obj.used_seats / obj.total_seats) * 100, 2)
        return 0
    
    def get_days_until_expiry(self, obj):
        if obj.end_date:
            from django.utils import timezone
            delta = obj.end_date - timezone.now().date()
            return delta.days
        return None
    
    def get_is_expiring_soon(self, obj):
        days = self.get_days_until_expiry(obj)
        return days is not None and 0 < days <= obj.renewal_notice_days
