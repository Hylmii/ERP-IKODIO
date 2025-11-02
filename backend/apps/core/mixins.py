"""
Query optimization mixins for ViewSets
"""
from rest_framework import viewsets


class OptimizedQueryMixin:
    """
    Mixin to optimize database queries with select_related and prefetch_related
    
    Usage:
        class EmployeeViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
            select_related_fields = ['department', 'position', 'user']
            prefetch_related_fields = ['attendances', 'leaves']
    """
    select_related_fields = []
    prefetch_related_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply select_related
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        # Apply prefetch_related
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        return queryset


class CachedQueryMixin:
    """
    Mixin to cache queryset results
    
    Usage:
        class DepartmentViewSet(CachedQueryMixin, viewsets.ModelViewSet):
            cache_timeout = 600  # 10 minutes
            cache_key_prefix = 'departments'
    """
    cache_timeout = 300  # 5 minutes default
    cache_key_prefix = 'viewset'
    
    def list(self, request, *args, **kwargs):
        from apps.core.cache import CacheManager
        
        # Generate cache key based on query params
        query_params = str(sorted(request.query_params.items()))
        cache_key = f"{self.cache_key_prefix}:list:{hash(query_params)}"
        
        # Try to get from cache
        def get_data():
            return super(CachedQueryMixin, self).list(request, *args, **kwargs)
        
        return CacheManager.get_or_set(cache_key, get_data, self.cache_timeout)


class BulkOperationMixin:
    """
    Mixin for efficient bulk operations
    
    Provides bulk_create, bulk_update methods
    """
    
    def bulk_create_objects(self, data_list, batch_size=100):
        """
        Efficiently create multiple objects in batches
        """
        objects = [self.get_serializer_class()(data=data).save() for data in data_list]
        return self.get_queryset().model.objects.bulk_create(objects, batch_size=batch_size)
    
    def bulk_update_objects(self, queryset, **update_fields):
        """
        Efficiently update multiple objects
        """
        return queryset.update(**update_fields)


class PaginationMixin:
    """
    Enhanced pagination with performance considerations
    """
    
    def get_paginated_response_data(self, data):
        """
        Add pagination metadata without expensive count queries for large datasets
        """
        assert self.paginator is not None
        
        return self.paginator.get_paginated_response(data).data


class FilterOptimizationMixin:
    """
    Optimize filtering operations
    """
    
    def filter_queryset(self, queryset):
        """
        Override to add query optimization hints
        """
        queryset = super().filter_queryset(queryset)
        
        # Add only() to limit fields if needed
        if hasattr(self, 'list_fields') and self.action == 'list':
            queryset = queryset.only(*self.list_fields)
        
        # Add defer() to exclude heavy fields
        if hasattr(self, 'deferred_fields'):
            queryset = queryset.defer(*self.deferred_fields)
        
        return queryset


class PerformanceMonitoringMixin:
    """
    Monitor query performance
    """
    
    def dispatch(self, request, *args, **kwargs):
        import time
        from django.db import connection
        
        # Reset query count
        queries_before = len(connection.queries)
        time_before = time.time()
        
        # Execute request
        response = super().dispatch(request, *args, **kwargs)
        
        # Calculate metrics
        queries_after = len(connection.queries)
        time_after = time.time()
        
        query_count = queries_after - queries_before
        execution_time = (time_after - time_before) * 1000  # milliseconds
        
        # Add headers
        response['X-Query-Count'] = query_count
        response['X-Execution-Time'] = f"{execution_time:.2f}ms"
        
        # Log slow requests
        if execution_time > 1000 or query_count > 10:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"- {query_count} queries in {execution_time:.2f}ms"
            )
        
        return response
