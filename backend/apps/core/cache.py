"""
Caching utilities for performance optimization
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_key(*args, **kwargs):
    """
    Generate cache key from function arguments
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_query(timeout=300, key_prefix='query'):
    """
    Decorator to cache database queries
    
    Usage:
        @cached_query(timeout=600, key_prefix='employees')
        def get_active_employees():
            return Employee.objects.filter(employment_status='active')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_suffix = cache_key(*args, **kwargs)
            full_key = f"{key_prefix}:{func.__name__}:{cache_suffix}"
            
            # Try to get from cache
            result = cache.get(full_key)
            
            if result is None:
                # Cache miss - execute query
                result = func(*args, **kwargs)
                # Store in cache
                cache.set(full_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache keys matching pattern
    
    Usage:
        invalidate_cache('employees:*')
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Get all keys matching pattern
        keys = redis_conn.keys(f"ikodio_erp:{key_pattern}")
        
        if keys:
            redis_conn.delete(*keys)
            return len(keys)
        return 0
    except Exception as e:
        print(f"Error invalidating cache: {e}")
        return 0


class CacheManager:
    """
    Manager class for cache operations
    """
    
    @staticmethod
    def get_or_set(key, callback, timeout=300):
        """
        Get value from cache or execute callback and cache result
        """
        result = cache.get(key)
        if result is None:
            result = callback()
            cache.set(key, result, timeout)
        return result
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidate all keys matching pattern
        """
        return invalidate_cache(pattern)
    
    @staticmethod
    def clear_all():
        """
        Clear entire cache (use with caution!)
        """
        cache.clear()
    
    @staticmethod
    def get_stats():
        """
        Get cache statistics
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            
            return {
                'total_keys': info.get('db1', {}).get('keys', 0),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'hit_rate': f"{info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1) * 100:.2f}%",
                'uptime_days': info.get('uptime_in_days', 0),
            }
        except Exception as e:
            return {'error': str(e)}


# Common cache timeouts
CACHE_TIMEOUTS = {
    'short': 60,        # 1 minute
    'medium': 300,      # 5 minutes
    'long': 1800,       # 30 minutes
    'very_long': 3600,  # 1 hour
    'day': 86400,       # 24 hours
}


# Cache key patterns for different modules
CACHE_KEYS = {
    'dashboard': 'dashboard:*',
    'employees': 'employees:*',
    'departments': 'departments:*',
    'projects': 'projects:*',
    'tasks': 'tasks:*',
    'invoices': 'invoices:*',
    'clients': 'clients:*',
    'assets': 'assets:*',
    'tickets': 'tickets:*',
    'documents': 'documents:*',
    'analytics': 'analytics:*',
}
