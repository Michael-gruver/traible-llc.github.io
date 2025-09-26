"""
Custom validators for file uploads and input validation
"""
import os
import hashlib
import time
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Try to import magic, but handle gracefully if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available. File content validation will be limited.")

class FileValidator:
    """
    Comprehensive file validation for security and integrity
    """
    
    ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.doc']
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    ]
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_FILE_SIZE = 1024  # 1KB
    
    def __init__(self, max_size=None, allowed_extensions=None, allowed_mime_types=None):
        self.max_size = max_size or self.MAX_FILE_SIZE
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
        self.allowed_mime_types = allowed_mime_types or self.ALLOWED_MIME_TYPES
    
    def __call__(self, file):
        """
        Validate the uploaded file
        """
        self.validate_file_size(file)
        self.validate_file_extension(file)
        self.validate_file_content(file)
        self.validate_file_integrity(file)
    
    def validate_file_size(self, file):
        """
        Validate file size
        """
        if file.size > self.max_size:
            raise ValidationError(
                _('File size cannot exceed %(max_size)s bytes.'),
                params={'max_size': self.max_size}
            )
        
        if file.size < self.MIN_FILE_SIZE:
            raise ValidationError(
                _('File size must be at least %(min_size)s bytes.'),
                params={'min_size': self.MIN_FILE_SIZE}
            )
    
    def validate_file_extension(self, file):
        """
        Validate file extension
        """
        file_name = file.name.lower()
        if not any(file_name.endswith(ext) for ext in self.allowed_extensions):
            raise ValidationError(
                _('File type not allowed. Allowed types: %(allowed_types)s'),
                params={'allowed_types': ', '.join(self.allowed_extensions)}
            )
    
    def validate_file_content(self, file):
        """
        Validate file content using magic numbers
        """
        if not MAGIC_AVAILABLE:
            logger.warning("Magic number validation skipped - python-magic not available")
            return
            
        try:
            # Read the first 1024 bytes to check magic numbers
            file.seek(0)
            file_header = file.read(1024)
            file.seek(0)  # Reset file pointer
            
            # Use python-magic to detect MIME type
            mime_type = magic.from_buffer(file_header, mime=True)
            
            if mime_type not in self.allowed_mime_types:
                raise ValidationError(
                    _('File content does not match allowed MIME types. Detected: %(detected_type)s'),
                    params={'detected_type': mime_type}
                )
                
        except Exception as e:
            logger.warning(f"Could not validate file content: {str(e)}")
            # If magic detection fails, we'll rely on extension validation
            pass
    
    def validate_file_integrity(self, file):
        """
        Basic file integrity check
        """
        try:
            # Calculate file hash for integrity check
            file.seek(0)
            file_hash = hashlib.md5()
            for chunk in file.chunks():
                file_hash.update(chunk)
            file.seek(0)  # Reset file pointer
            
            # Store hash for later verification
            file._file_hash = file_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            raise ValidationError(_('File integrity check failed.'))

class DocumentContentValidator:
    """
    Validate document content for security and quality
    """
    
    MAX_TEXT_LENGTH = 1000000  # 1MB of text
    MIN_TEXT_LENGTH = 100  # Minimum meaningful content
    
    def __init__(self, max_length=None, min_length=None):
        self.max_length = max_length or self.MAX_TEXT_LENGTH
        self.min_length = min_length or self.MIN_TEXT_LENGTH
    
    def validate_text_content(self, text):
        """
        Validate extracted text content
        """
        if not text or not text.strip():
            raise ValidationError(_('Document contains no readable text content.'))
        
        if len(text) > self.max_length:
            raise ValidationError(
                _('Document text content is too long. Maximum length: %(max_length)s characters.'),
                params={'max_length': self.max_length}
            )
        
        if len(text.strip()) < self.min_length:
            raise ValidationError(
                _('Document text content is too short. Minimum length: %(min_length)s characters.'),
                params={'min_length': self.min_length}
            )
        
        # Check for suspicious content patterns
        self.check_suspicious_content(text)
    
    def check_suspicious_content(self, text):
        """
        Check for potentially malicious or suspicious content
        """
        suspicious_patterns = [
            '<script',
            'javascript:',
            'vbscript:',
            'data:text/html',
            'eval(',
            'document.cookie',
            'window.location',
        ]
        
        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                logger.warning(f"Suspicious content detected: {pattern}")
                raise ValidationError(
                    _('Document contains potentially malicious content.')
                )

class QueryValidator:
    """
    Validate user queries for security and quality
    """
    
    MAX_QUERY_LENGTH = 1000
    MIN_QUERY_LENGTH = 3
    
    def __init__(self, max_length=None, min_length=None):
        self.max_length = max_length or self.MAX_QUERY_LENGTH
        self.min_length = min_length or self.MIN_QUERY_LENGTH
    
    def validate_query(self, query):
        """
        Validate user query
        """
        if not query or not query.strip():
            raise ValidationError(_('Query cannot be empty.'))
        
        query = query.strip()
        
        if len(query) > self.max_length:
            raise ValidationError(
                _('Query is too long. Maximum length: %(max_length)s characters.'),
                params={'max_length': self.max_length}
            )
        
        if len(query) < self.min_length:
            raise ValidationError(
                _('Query is too short. Minimum length: %(min_length)s characters.'),
                params={'min_length': self.min_length}
            )
        
        # Check for suspicious query patterns
        self.check_suspicious_query(query)
        
        return query
    
    def check_suspicious_query(self, query):
        """
        Check for potentially malicious query patterns
        """
        suspicious_patterns = [
            '<script',
            'javascript:',
            'vbscript:',
            'data:text/html',
            'eval(',
            'document.cookie',
            'window.location',
            'DROP TABLE',
            'DELETE FROM',
            'INSERT INTO',
            'UPDATE SET',
            'UNION SELECT',
            'OR 1=1',
            'AND 1=1',
        ]
        
        query_lower = query.lower()
        for pattern in suspicious_patterns:
            if pattern in query_lower:
                logger.warning(f"Suspicious query detected: {pattern}")
                raise ValidationError(
                    _('Query contains potentially malicious content.')
                )

class RateLimitValidator:
    """
    Validate rate limiting for API endpoints
    """
    
    def __init__(self, max_requests_per_minute=60, max_requests_per_hour=1000):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
    
    def validate_request_rate(self, user_id, endpoint):
        """
        Validate if user has exceeded rate limits
        """
        # This would typically integrate with Redis or database
        # For now, we'll implement a simple in-memory check
        # In production, use Redis with proper expiration
        
        current_time = time.time()
        minute_key = f"rate_limit:{user_id}:{endpoint}:minute:{int(current_time // 60)}"
        hour_key = f"rate_limit:{user_id}:{endpoint}:hour:{int(current_time // 3600)}"
        
        # Check minute rate limit
        minute_requests = cache.get(minute_key, 0)
        if minute_requests >= self.max_requests_per_minute:
            raise ValidationError(
                _('Rate limit exceeded. Maximum %(max_requests)s requests per minute.'),
                params={'max_requests': self.max_requests_per_minute}
            )
        
        # Check hour rate limit
        hour_requests = cache.get(hour_key, 0)
        if hour_requests >= self.max_requests_per_hour:
            raise ValidationError(
                _('Rate limit exceeded. Maximum %(max_requests)s requests per hour.'),
                params={'max_requests': self.max_requests_per_hour}
            )
        
        # Increment counters
        cache.set(minute_key, minute_requests + 1, 60)
        cache.set(hour_key, hour_requests + 1, 3600)
