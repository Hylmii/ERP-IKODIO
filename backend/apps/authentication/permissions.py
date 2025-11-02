"""
Custom permission classes for authentication
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to edit objects.
    Read permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_superuser


class HasPermission(permissions.BasePermission):
    """
    Custom permission to check if user has specific permission via role.
    Usage: permission_classes = [HasPermission]
    Define required_permission in view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True
        
        if not request.user.role:
            return False
        
        return request.user.role.permissions.filter(
            codename=required_permission
        ).exists()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to edit objects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        return obj == request.user or request.user.is_staff
