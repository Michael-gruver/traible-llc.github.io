"""
Custom middleware for error handling and request logging
"""
import logging
import time
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle exceptions and provide consistent error responses
    """
    
    def process_exception(self, request, exception):
        """
        Handle exceptions and return consistent error responses
        """
        # Log the exception
        logger.error(
            f"Exception in {request.path}: {str(exception)}",
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'exception_type': type(exception).__name__,
                'traceback': traceback.format_exc()
            }
        )
        
        # Return appropriate error response
        if settings.DEBUG:
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': str(exception),
                'type': type(exception).__name__,
                'path': request.path,
                'traceback': traceback.format_exc()
            }, status=500)
        else:
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred. Please try again later.'
            }, status=500)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses
    """
    
    def process_request(self, request):
        """
        Log incoming requests
        """
        request.start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'request_method': request.method,
                'request_path': request.path,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
    
    def process_response(self, request, response):
        """
        Log outgoing responses
        """
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"Response: {request.method} {request.path} - {response.status_code} ({duration:.3f}s)",
                extra={
                    'request_method': request.method,
                    'request_path': request.path,
                    'response_status': response.status_code,
                    'duration': duration,
                    'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                }
            )
        
        return response
    
    def get_client_ip(self, request):
        """
        Get the client IP address from the request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check rate limits for API requests
        """
        # Only apply rate limiting to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Get client identifier
        client_id = self.get_client_id(request)
        current_time = time.time()
        
        # Clean old entries (older than 1 hour)
        self.clean_old_entries(current_time)
        
        # Check rate limit
        if self.is_rate_limited(client_id, current_time):
            logger.warning(
                f"Rate limit exceeded for {client_id} on {request.path}",
                extra={
                    'client_id': client_id,
                    'request_path': request.path,
                    'request_method': request.method,
                }
            )
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }, status=429)
        
        # Record this request
        self.record_request(client_id, current_time)
        
        return None
    
    def get_client_id(self, request):
        """
        Get a unique identifier for the client
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            return f"ip_{self.get_client_ip(request)}"
    
    def get_client_ip(self, request):
        """
        Get the client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_id, current_time):
        """
        Check if the client has exceeded the rate limit
        """
        if client_id not in self.requests:
            return False
        
        # Count requests in the last hour
        hour_ago = current_time - 3600
        recent_requests = [t for t in self.requests[client_id] if t > hour_ago]
        
        # Rate limit: 1000 requests per hour for authenticated users, 100 for anonymous
        limit = 1000 if client_id.startswith('user_') else 100
        
        return len(recent_requests) >= limit
    
    def record_request(self, client_id, current_time):
        """
        Record a request for the client
        """
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id].append(current_time)
    
    def clean_old_entries(self, current_time):
        """
        Clean old request entries
        """
        hour_ago = current_time - 3600
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [t for t in self.requests[client_id] if t > hour_ago]
            if not self.requests[client_id]:
                del self.requests[client_id]
