# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.cache import cache
import uuid
import secrets
from datetime import timedelta

class User(AbstractUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_verified = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Password reset tracking
    password_reset_attempts = models.PositiveIntegerField(default=0)
    last_password_reset_attempt = models.DateTimeField(null=True, blank=True)
    
    # Adding unique related_name to avoid reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # Unique name for the reverse relationship
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_permission_set',  # Unique name for the reverse relationship
        blank=True
    )

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # This will prevent Django's unique validation from firing first
        self._state.adding = self.id is None
        super().save(*args, **kwargs)
    
    def generate_password_reset_token(self):
        """Generate a secure password reset token and store it in cache"""
        # Generate a cryptographically secure token
        token = secrets.token_urlsafe(32)
        uid = str(self.id)
        
        # Store token in cache with 1 hour expiration
        cache_key = f"password_reset_token_{uid}_{token}"
        cache.set(cache_key, {
            'user_id': self.id,
            'email': self.email,
            'created_at': timezone.now().isoformat()
        }, 3600)  # 1 hour
        
        return token, uid
    
    def validate_password_reset_token(self, token):
        """Validate if a password reset token is valid and not expired"""
        uid = str(self.id)
        cache_key = f"password_reset_token_{uid}_{token}"
        token_data = cache.get(cache_key)
        
        if token_data:
            return True
        return False
    
    def invalidate_password_reset_token(self, token):
        """Invalidate a password reset token after use"""
        uid = str(self.id)
        cache_key = f"password_reset_token_{uid}_{token}"
        cache.delete(cache_key)
    
    def can_request_password_reset(self):
        """Check if user can request password reset based on rate limiting"""
        now = timezone.now()
        
        # Reset attempts if it's been more than 1 hour since last attempt
        if (self.last_password_reset_attempt and 
            now - self.last_password_reset_attempt > timedelta(hours=1)):
            self.password_reset_attempts = 0
            self.save()
        
        # Allow if less than 3 attempts in the last hour
        return self.password_reset_attempts < 3
    
    def increment_password_reset_attempts(self):
        """Increment password reset attempts counter"""
        self.password_reset_attempts += 1
        self.last_password_reset_attempt = timezone.now()
        self.save()
    
    def reset_password_attempts(self):
        """Reset password reset attempts counter"""
        self.password_reset_attempts = 0
        self.last_password_reset_attempt = None
        self.save()