"""
Management command to clean up old documents and vector stores
"""
import os
import shutil
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from chatbot.models import Document, Conversation, Message
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up old documents, conversations, and vector stores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep documents (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        force = options['force']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting cleanup of documents older than {days} days')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will be deleted')
            )
        
        # Clean up old documents
        self.cleanup_documents(cutoff_date, dry_run, force)
        
        # Clean up old conversations
        self.cleanup_conversations(cutoff_date, dry_run, force)
        
        # Clean up orphaned vector stores
        self.cleanup_vector_stores(dry_run, force)
        
        self.stdout.write(
            self.style.SUCCESS('Cleanup completed successfully')
        )

    def cleanup_documents(self, cutoff_date, dry_run, force):
        """
        Clean up old documents
        """
        old_documents = Document.objects.filter(created_at__lt=cutoff_date)
        count = old_documents.count()
        
        if count == 0:
            self.stdout.write('No old documents found to clean up')
            return
        
        self.stdout.write(f'Found {count} old documents to clean up')
        
        if not dry_run:
            if not force:
                confirm = input(f'Delete {count} old documents? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write('Skipping document cleanup')
                    return
            
            # Delete document files and database records
            for document in old_documents:
                try:
                    # Delete the file if it exists
                    if document.file and os.path.exists(document.file.path):
                        os.remove(document.file.path)
                        self.stdout.write(f'Deleted file: {document.file.path}')
                    
                    # Delete vector store if it exists
                    if document.vector_store_path and os.path.exists(document.vector_store_path):
                        shutil.rmtree(document.vector_store_path)
                        self.stdout.write(f'Deleted vector store: {document.vector_store_path}')
                    
                    # Delete database record
                    document.delete()
                    self.stdout.write(f'Deleted document record: {document.id}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error deleting document {document.id}: {str(e)}')
                    )
        
        self.stdout.write(f'{"Would delete" if dry_run else "Deleted"} {count} old documents')

    def cleanup_conversations(self, cutoff_date, dry_run, force):
        """
        Clean up old conversations and their messages
        """
        old_conversations = Conversation.objects.filter(created_at__lt=cutoff_date)
        count = old_conversations.count()
        
        if count == 0:
            self.stdout.write('No old conversations found to clean up')
            return
        
        self.stdout.write(f'Found {count} old conversations to clean up')
        
        if not dry_run:
            if not force:
                confirm = input(f'Delete {count} old conversations? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write('Skipping conversation cleanup')
                    return
            
            # Delete conversations and their messages
            for conversation in old_conversations:
                try:
                    # Delete all messages in the conversation
                    message_count = conversation.messages.count()
                    conversation.messages.all().delete()
                    
                    # Delete the conversation
                    conversation.delete()
                    
                    self.stdout.write(f'Deleted conversation {conversation.id} with {message_count} messages')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error deleting conversation {conversation.id}: {str(e)}')
                    )
        
        self.stdout.write(f'{"Would delete" if dry_run else "Deleted"} {count} old conversations')

    def cleanup_vector_stores(self, dry_run, force):
        """
        Clean up orphaned vector stores
        """
        vector_store_dir = getattr(settings, 'VECTOR_STORE_DIR', 'vector_stores')
        
        if not os.path.exists(vector_store_dir):
            self.stdout.write('Vector store directory not found')
            return
        
        orphaned_stores = []
        
        # Find orphaned vector stores
        for root, dirs, files in os.walk(vector_store_dir):
            if 'index.faiss' in files:
                # Extract document ID from path
                path_parts = root.split(os.sep)
                if len(path_parts) >= 3:
                    try:
                        document_id = int(path_parts[-1].split('_')[-1])
                        # Check if document still exists
                        if not Document.objects.filter(id=document_id).exists():
                            orphaned_stores.append(root)
                    except (ValueError, IndexError):
                        # Invalid path format, consider it orphaned
                        orphaned_stores.append(root)
        
        if not orphaned_stores:
            self.stdout.write('No orphaned vector stores found')
            return
        
        self.stdout.write(f'Found {len(orphaned_stores)} orphaned vector stores')
        
        if not dry_run:
            if not force:
                confirm = input(f'Delete {len(orphaned_stores)} orphaned vector stores? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write('Skipping vector store cleanup')
                    return
            
            # Delete orphaned vector stores
            for store_path in orphaned_stores:
                try:
                    shutil.rmtree(store_path)
                    self.stdout.write(f'Deleted orphaned vector store: {store_path}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error deleting vector store {store_path}: {str(e)}')
                    )
        
        self.stdout.write(f'{"Would delete" if dry_run else "Deleted"} {len(orphaned_stores)} orphaned vector stores')
