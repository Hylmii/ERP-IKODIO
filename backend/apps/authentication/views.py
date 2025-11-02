"""
Authentication & Authorization Views
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User, Role, Permission, UserSession, AuditLog, PasswordResetToken
from .serializers import (
    UserSerializer, UserListSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    RoleSerializer, PermissionSerializer, UserSessionSerializer, AuditLogSerializer
)
from .permissions import IsAdminOrReadOnly, IsSuperUserOrReadOnly
from .utils import create_audit_log, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Create a new user account",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(APIView):
    """
    User login endpoint
    Returns JWT access and refresh tokens
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate user and get JWT tokens",
        request=LoginSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Create user session
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        # Calculate expiration (7 days for refresh token)
        from datetime import timedelta
        expires_at = timezone.now() + timedelta(days=7)
        
        session = UserSession.objects.create(
            user=user,
            token=str(refresh.access_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )
        
        # Create audit log
        create_audit_log(
            user=user,
            action='LOGIN',
            resource_type='User',
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """
    User logout endpoint
    Revokes the refresh token and deactivates session
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="User logout",
        description="Revoke tokens and end session",
        tags=["Authentication"]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate user session
            UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            # Create audit log
            create_audit_log(
                user=request.user,
                action='LOGOUT',
                resource_type='User',
                resource_id=str(request.user.id),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get or update current authenticated user
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get current user",
        description="Retrieve authenticated user details",
        tags=["User Management"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update current user",
        description="Update authenticated user profile",
        tags=["User Management"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update current user",
        description="Partially update authenticated user profile",
        tags=["User Management"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListCreateAPIView):
    """
    List all users or create new user
    """
    queryset = User.objects.all().select_related('role')
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'role']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_login']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegisterSerializer
        return UserListSerializer
    
    @extend_schema(
        summary="List users",
        description="Get paginated list of users",
        tags=["User Management"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create user",
        description="Create a new user (admin only)",
        tags=["User Management"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user
    """
    queryset = User.objects.all().select_related('role')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get user details",
        description="Retrieve detailed user information",
        tags=["User Management"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user",
        description="Update user information (admin only)",
        tags=["User Management"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update user",
        description="Partially update user information (admin only)",
        tags=["User Management"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete user",
        description="Delete user (admin only)",
        tags=["User Management"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    Change password for authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change password for current user",
        request=ChangePasswordSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Create audit log
            create_audit_log(
                user=user,
                action='PASSWORD_CHANGE',
                resource_type='User',
                resource_id=str(user.id),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Request password reset email
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email",
        request=PasswordResetRequestSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Send email
            send_password_reset_email(user, reset_token.token)
            
            # Create audit log
            create_audit_log(
                user=user,
                action='PASSWORD_RESET_REQUEST',
                resource_type='User',
                resource_id=str(user.id),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except User.DoesNotExist:
            pass  # Don't reveal if user exists
        
        return Response(
            {"detail": "Password reset email sent if account exists."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Reset password with token",
        request=PasswordResetConfirmSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                used=False,
                expires_at__gt=timezone.now()
            )
            
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            # Create audit log
            create_audit_log(
                user=user,
                action='PASSWORD_RESET',
                resource_type='User',
                resource_id=str(user.id),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class RoleListView(generics.ListCreateAPIView):
    """
    List all roles or create new role
    """
    queryset = Role.objects.all().prefetch_related('permissions')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @extend_schema(
        summary="List roles",
        description="Get list of all roles",
        tags=["Roles & Permissions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create role",
        description="Create a new role (admin only)",
        tags=["Roles & Permissions"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a role
    """
    queryset = Role.objects.all().prefetch_related('permissions')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @extend_schema(
        summary="Get role details",
        description="Retrieve detailed role information",
        tags=["Roles & Permissions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update role",
        description="Update role information (admin only)",
        tags=["Roles & Permissions"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial update role",
        description="Partially update role information (admin only)",
        tags=["Roles & Permissions"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete role",
        description="Delete role (admin only)",
        tags=["Roles & Permissions"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PermissionListView(generics.ListAPIView):
    """
    List all permissions
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['module']
    search_fields = ['name', 'codename', 'description']
    ordering_fields = ['name', 'module']
    ordering = ['module', 'name']
    
    @extend_schema(
        summary="List permissions",
        description="Get list of all available permissions",
        tags=["Roles & Permissions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserSessionListView(generics.ListAPIView):
    """
    List user sessions
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSession.objects.all().select_related('user')
        return UserSession.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List sessions",
        description="Get list of user sessions",
        tags=["Session Management"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RevokeSessionView(APIView):
    """
    Revoke a user session
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Revoke session",
        description="Deactivate a user session",
        tags=["Session Management"]
    )
    def post(self, request, pk):
        try:
            if request.user.is_staff:
                session = UserSession.objects.get(id=pk)
            else:
                session = UserSession.objects.get(id=pk, user=request.user)
            
            session.is_active = False
            session.save()
            
            # Create audit log
            create_audit_log(
                user=request.user,
                action='SESSION_REVOKE',
                resource_type='UserSession',
                resource_id=str(session.id),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"detail": "Session revoked successfully."}, status=status.HTTP_200_OK)
        except UserSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class AuditLogListView(generics.ListAPIView):
    """
    List audit logs
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'action', 'resource_type']
    search_fields = ['action', 'resource_type', 'user__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return AuditLog.objects.all().select_related('user')
        return AuditLog.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List audit logs",
        description="Get list of audit logs (superuser only)",
        tags=["Audit"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
