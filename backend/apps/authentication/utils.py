"""
Utility functions for authentication module
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import AuditLog


def create_audit_log(user, action, resource_type, resource_id, ip_address='', user_agent='', changes=None):
    """
    Create an audit log entry
    
    Args:
        user: User instance
        action: Action performed (e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN')
        resource_type: Type of resource (e.g., 'User', 'Role', 'Project')
        resource_id: UUID of the resource
        ip_address: IP address of the request
        user_agent: User agent string
        changes: Dict of changes made (optional)
    
    Returns:
        AuditLog instance
    """
    return AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        changes=changes or {}
    )


def send_password_reset_email(user, token):
    """
    Send password reset email to user
    
    Args:
        user: User instance
        token: Password reset token
    """
    subject = 'Password Reset Request - Ikodio ERP'
    
    # In production, this should be a proper frontend URL
    reset_link = f"{settings.ALLOWED_HOSTS[0]}/reset-password?token={token}"
    
    message = f"""
    Hi {user.get_full_name()},
    
    You requested to reset your password for Ikodio ERP.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Ikodio ERP Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_welcome_email(user):
    """
    Send welcome email to new user
    
    Args:
        user: User instance
    """
    subject = 'Welcome to Ikodio ERP'
    
    message = f"""
    Hi {user.get_full_name()},
    
    Welcome to Ikodio ERP!
    
    Your account has been successfully created.
    
    Email: {user.email}
    Username: {user.username}
    
    You can now login to the system and start using our services.
    
    Best regards,
    Ikodio ERP Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_email_verification(user, verification_token):
    """
    Send email verification link to user
    
    Args:
        user: User instance
        verification_token: Email verification token
    """
    subject = 'Verify Your Email - Ikodio ERP'
    
    # In production, this should be a proper frontend URL
    verification_link = f"{settings.ALLOWED_HOSTS[0]}/verify-email?token={verification_token}"
    
    message = f"""
    Hi {user.get_full_name()},
    
    Please verify your email address for Ikodio ERP.
    
    Click the link below to verify your email:
    {verification_link}
    
    This link will expire in 24 hours.
    
    Best regards,
    Ikodio ERP Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
