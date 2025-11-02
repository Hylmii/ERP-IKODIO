"""
URL configuration for Ikodio ERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/hr/', include('apps.hr.urls')),
    path('api/v1/project/', include('apps.project.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/crm/', include('apps.crm.urls')),
    path('api/v1/asset/', include('apps.asset.urls')),
    path('api/v1/helpdesk/', include('apps.helpdesk.urls')),
    path('api/v1/dms/', include('apps.dms.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/integration/', include('apps.core.integration_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
