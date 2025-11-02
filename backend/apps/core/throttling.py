"""
Custom throttling classes for rate limiting
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts
    Limits: 5 attempts per minute for anonymous users
    """
    scope = 'login'


class SensitiveOperationThrottle(UserRateThrottle):
    """
    Throttle for sensitive operations (delete, export, etc.)
    Limits: 10 operations per minute
    """
    scope = 'sensitive'


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst traffic
    Limits: 60 requests per minute
    """
    scope = 'burst'
    rate = '60/min'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained traffic
    Limits: 1000 requests per hour
    """
    scope = 'sustained'
    rate = '1000/hour'
