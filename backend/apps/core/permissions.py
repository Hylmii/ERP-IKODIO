"""
Core permission classes for the application.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read-only permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to edit objects.
    Read-only permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions are only allowed to superusers
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to the owner or admin
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user or request.user.is_staff
        
        # Default to admin-only for write operations
        return request.user.is_staff


class HasPermission(permissions.BasePermission):
    """
    Custom permission to check if user has specific permission.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if view has required_permission attribute
        if hasattr(view, 'required_permission'):
            permission_codename = view.required_permission
            # Check if user has the required permission through their roles
            if hasattr(request.user, 'roles'):
                for role in request.user.roles.all():
                    if role.permissions.filter(codename=permission_codename).exists():
                        return True
            return False
        
        # If no specific permission is required, allow authenticated users
        return True
