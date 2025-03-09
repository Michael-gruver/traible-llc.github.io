# chatbot/models.py

from django.db import models
from django.conf import settings
import uuid

class Document(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    content_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    vector_store_path = models.CharField(max_length=255, null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)  # Store extracted text
    processing_error = models.TextField(null=True, blank=True)  # Store any processing errors
    file_hash = models.CharField(max_length=64, null=True)  # Add file hash for duplicate detection
    has_images = models.BooleanField(default=False)
    image_count = models.IntegerField(default=0)
    image_data = models.JSONField(null=True, blank=True)
    extracted_tables = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'documents'
        unique_together = ('user', 'file_hash')  # Prevent duplicate uploads per user

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    document_key = models.CharField(max_length=255, null=True, blank=True)  # Added field
    updated_at = models.DateTimeField(auto_now=True)  # Added to track last activity
    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['document_key']),  # Add index for faster lookup
        ]

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    created_at = models.DateTimeField(auto_now_add=True)
    references = models.JSONField(null=True, blank=True)  # Store document references

    class Meta:
        db_table = 'messages'
