"""
Comprehensive test suite for chatbot views
"""
import os
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import json

from chatbot.models import Document, Conversation, Message
from chatbot.validators import FileValidator, DocumentContentValidator, QueryValidator

User = get_user_model()

class DocumentUploadTestCase(APITestCase):
    """
    Test cases for document upload functionality
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test PDF content
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    def test_document_upload_success(self):
        """
        Test successful document upload
        """
        with patch('chatbot.services.bedrock_service.BedrockService.process_document') as mock_process:
            mock_process.return_value = True
            
            # Create test file
            test_file = SimpleUploadedFile(
                "test.pdf",
                self.test_pdf_content,
                content_type="application/pdf"
            )
            
            response = self.client.post(
                reverse('upload-document'),
                {'file': test_file, 'title': 'Test Document'},
                format='multipart'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(Document.objects.filter(user=self.user, title='Test Document').exists())
    
    def test_document_upload_invalid_file_type(self):
        """
        Test document upload with invalid file type
        """
        # Create invalid file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a PDF",
            content_type="text/plain"
        )
        
        response = self.client.post(
            reverse('upload-document'),
            {'file': test_file, 'title': 'Test Document'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_document_upload_file_too_large(self):
        """
        Test document upload with file too large
        """
        # Create large file (simulate)
        large_content = b'x' * (51 * 1024 * 1024)  # 51MB
        
        test_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        response = self.client.post(
            reverse('upload-document'),
            {'file': test_file, 'title': 'Large Document'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_document_upload_unauthorized(self):
        """
        Test document upload without authentication
        """
        client = APIClient()  # No authentication
        
        test_file = SimpleUploadedFile(
            "test.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = client.post(
            reverse('upload-document'),
            {'file': test_file, 'title': 'Test Document'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ChatTestCase(APITestCase):
    """
    Test cases for chat functionality
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test document
        self.document = Document.objects.create(
            user=self.user,
            title='Test Document',
            file='test.pdf',
            is_processed=True,
            raw_text='This is test content for the document.'
        )
        
        # Create test conversation
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
    
    @patch('chatbot.services.bedrock_service.BedrockService.get_response')
    def test_chat_success(self, mock_get_response):
        """
        Test successful chat interaction
        """
        mock_get_response.return_value = "This is a test response"
        
        response = self.client.post(
            reverse('chat'),
            {
                'message': 'What is this document about?',
                'document_ids': [str(self.document.id)],
                'conversation_id': str(self.conversation.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertTrue(Message.objects.filter(conversation=self.conversation).exists())
    
    def test_chat_invalid_query(self):
        """
        Test chat with invalid query
        """
        response = self.client.post(
            reverse('chat'),
            {
                'message': '',  # Empty message
                'document_ids': [str(self.document.id)],
                'conversation_id': str(self.conversation.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_chat_unauthorized(self):
        """
        Test chat without authentication
        """
        client = APIClient()  # No authentication
        
        response = client.post(
            reverse('chat'),
            {
                'message': 'What is this document about?',
                'document_ids': [str(self.document.id)],
                'conversation_id': str(self.conversation.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class HealthCheckTestCase(APITestCase):
    """
    Test cases for health check endpoints
    """
    
    def test_health_check(self):
        """
        Test basic health check endpoint
        """
        response = self.client.get(reverse('health-check'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_detailed_health_check(self):
        """
        Test detailed health check endpoint
        """
        response = self.client.get(reverse('detailed-health'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('checks', response.data)
    
    def test_metrics_endpoint(self):
        """
        Test metrics endpoint
        """
        response = self.client.get(reverse('metrics'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('timestamp', response.data)
        self.assertIn('system', response.data)
    
    def test_readiness_probe(self):
        """
        Test readiness probe endpoint
        """
        response = self.client.get(reverse('readiness'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
    
    def test_liveness_probe(self):
        """
        Test liveness probe endpoint
        """
        response = self.client.get(reverse('liveness'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

class ValidatorTestCase(TestCase):
    """
    Test cases for custom validators
    """
    
    def test_file_validator_success(self):
        """
        Test file validator with valid file
        """
        validator = FileValidator()
        
        # Create valid PDF file
        test_file = SimpleUploadedFile(
            "test.pdf",
            b'%PDF-1.4\nTest content',
            content_type="application/pdf"
        )
        
        # Should not raise any exception
        validator(test_file)
    
    def test_file_validator_invalid_extension(self):
        """
        Test file validator with invalid extension
        """
        validator = FileValidator()
        
        # Create file with invalid extension
        test_file = SimpleUploadedFile(
            "test.exe",
            b'This is not a PDF',
            content_type="application/octet-stream"
        )
        
        with self.assertRaises(Exception):
            validator(test_file)
    
    def test_query_validator_success(self):
        """
        Test query validator with valid query
        """
        validator = QueryValidator()
        
        valid_query = "What is this document about?"
        result = validator.validate_query(valid_query)
        
        self.assertEqual(result, valid_query)
    
    def test_query_validator_empty_query(self):
        """
        Test query validator with empty query
        """
        validator = QueryValidator()
        
        with self.assertRaises(Exception):
            validator.validate_query("")
    
    def test_query_validator_suspicious_content(self):
        """
        Test query validator with suspicious content
        """
        validator = QueryValidator()
        
        suspicious_query = "What is this document about? <script>alert('xss')</script>"
        
        with self.assertRaises(Exception):
            validator.validate_query(suspicious_query)

class DocumentModelTestCase(TestCase):
    """
    Test cases for Document model
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_document_creation(self):
        """
        Test document creation
        """
        document = Document.objects.create(
            user=self.user,
            title='Test Document',
            file='test.pdf',
            is_processed=True
        )
        
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.user, self.user)
        self.assertTrue(document.is_processed)
    
    def test_document_str_representation(self):
        """
        Test document string representation
        """
        document = Document.objects.create(
            user=self.user,
            title='Test Document',
            file='test.pdf'
        )
        
        self.assertEqual(str(document), 'Test Document')

class ConversationModelTestCase(TestCase):
    """
    Test cases for Conversation model
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_conversation_creation(self):
        """
        Test conversation creation
        """
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.user, self.user)
    
    def test_conversation_str_representation(self):
        """
        Test conversation string representation
        """
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        
        self.assertEqual(str(conversation), 'Test Conversation')

class MessageModelTestCase(TestCase):
    """
    Test cases for Message model
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
    
    def test_message_creation(self):
        """
        Test message creation
        """
        message = Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            role='user'
        )
        
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.conversation, self.conversation)
    
    def test_message_str_representation(self):
        """
        Test message string representation
        """
        message = Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            role='user'
        )
        
        self.assertEqual(str(message), 'Test message')
