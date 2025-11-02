"""
Base models that will be inherited by other models across the application
"""
from django.db import models
from django.contrib.auth import get_user_model


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft delete functionality
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )

    class Meta:
        abstract = True


class AuditModel(TimeStampedModel):
    """
    Abstract base model with audit trail fields
    """
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


class BaseModel(AuditModel, SoftDeleteModel):
    """
    Combined base model with timestamp, audit, and soft delete functionality
    """
    class Meta:
        abstract = True


# Import integration models to register them with Django
from .integration_models import (  # noqa: E402, F401
    EmailTemplate,
    EmailLog,
    Notification,
    Webhook,
    WebhookDelivery,
    ExternalService,
    APILog,
    ScheduledJob,
    SystemSetting,
)
