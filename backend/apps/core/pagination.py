"""
Custom pagination classes for optimized performance
"""
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with 20 items per page
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.page_size),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets with 50 items per page
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for small datasets with 10 items per page
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class OptimizedCursorPagination(CursorPagination):
    """
    Cursor-based pagination for better performance on large datasets
    No count() query executed, faster for large tables
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'  # Default ordering
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class NoPaginationClass:
    """
    Disable pagination for specific views (use with caution!)
    """
    def paginate_queryset(self, queryset, request, view=None):
        return None
    
    def get_paginated_response(self, data):
        return Response(data)
