"""
Custom security middleware for Django application
"""
import logging
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Strict Transport Security (HSTS) - only in production with HTTPS
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validate incoming requests for security threats
    """
    
    SUSPICIOUS_PATTERNS = [
        '../', '..\\',  # Path traversal
        '<script', '</script>',  # XSS attempts
        'javascript:',  # JavaScript protocol
        'onerror=', 'onload=',  # Event handlers
        'SELECT', 'UNION', 'DROP', 'INSERT', '--',  # SQL injection patterns
    ]
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    def process_request(self, request):
        # Check request size
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            logger.warning(
                f"Request too large: {content_length} bytes from {self.get_client_ip(request)}"
            )
            return HttpResponseForbidden("Request entity too large")
        
        # Check for suspicious patterns in query params
        query_string = request.META.get('QUERY_STRING', '')
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in query_string.lower():
                logger.warning(
                    f"Suspicious pattern '{pattern}' detected in request from {self.get_client_ip(request)}: {query_string}"
                )
                return HttpResponseForbidden("Invalid request")
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Whitelist specific IP addresses for admin access (optional)
    Set ADMIN_IP_WHITELIST in settings to enable
    """
    
    def process_request(self, request):
        # Only apply to admin URLs
        if not request.path.startswith('/admin/'):
            return None
        
        whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', None)
        if not whitelist:
            return None
        
        client_ip = self.get_client_ip(request)
        
        if client_ip not in whitelist:
            logger.warning(
                f"Unauthorized admin access attempt from {client_ip}"
            )
            return HttpResponseForbidden("Access denied")
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLogMiddleware(MiddlewareMixin):
    """
    Log all API requests for audit trail
    """
    
    SENSITIVE_FIELDS = ['password', 'token', 'secret', 'api_key']
    
    def process_request(self, request):
        # Store request start time
        import time
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Only log API requests
        if not request.path.startswith('/api/'):
            return response
        
        # Calculate request duration
        import time
        duration = int((time.time() - getattr(request, '_start_time', time.time())) * 1000)
        
        # Get user
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Log request
        log_data = {
            'method': request.method,
            'path': request.path,
            'user_id': user_id,
            'ip_address': client_ip,
            'status_code': response.status_code,
            'duration_ms': duration,
        }
        
        if response.status_code >= 400:
            logger.warning(f"API request failed: {log_data}")
        else:
            logger.info(f"API request: {log_data}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
