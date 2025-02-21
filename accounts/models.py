# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_verified = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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