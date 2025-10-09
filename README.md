# Traible Backend - Document Intelligence Platform

A comprehensive Django-based backend system for document intelligence, AI chat functionality, and secure user management. Built with modern Python technologies and enterprise-grade features.

## Features

### **Core Features**
- **Document Processing**: Upload, analyze, and process PDF documents with AI-powered text extraction, image analysis, and table recognition
- **AI Chat System**: Interactive chat with AI about document content using AWS Bedrock Claude 3 Sonnet
- **User Authentication**: Secure JWT-based authentication with comprehensive user management
- **Password Recovery**: Complete password reset system with security best practices and rate limiting
- **File Management**: Secure file upload, validation, and storage with duplicate detection
- **Background Tasks**: Asynchronous document processing with Celery integration and progress tracking
- **Health Monitoring**: Comprehensive system health checks, metrics, and Kubernetes-ready probes

### **Security Features**
- **Rate Limiting**: Configurable API rate limiting (1000/hour authenticated, 100/hour anonymous)
- **Input Validation**: Comprehensive file and data validation with security scanning
- **Token Security**: Cryptographically secure token generation and management with cache-based invalidation
- **Email Privacy**: Secure email handling without information disclosure
- **File Security**: Magic number validation, MIME type checking, and file hash verification
- **CORS Protection**: Secure cross-origin request handling
- **SQL Injection Protection**: Query sanitization and parameterized queries
- **Password Security**: Strong password validation and secure reset mechanisms

### **Developer Experience**
- **API Documentation**: Interactive Swagger UI and ReDoc documentation with comprehensive examples
- **Comprehensive Testing**: Unit tests, integration tests, and security tests
- **Error Handling**: Structured error responses with detailed logging and graceful degradation
- **Development Tools**: Debug toolbar, Django extensions, and development utilities
- **Type Safety**: Python type hints and comprehensive validation
- **Hot Reload**: Fast development with Django's built-in server

### **Production Features**
- **Scalability**: Horizontal scaling support with stateless design and Redis caching
- **Caching**: Redis integration with model-level caching and session management
- **Database Optimization**: Strategic indexes, query optimization, and connection pooling
- **Monitoring**: Health checks, metrics, and performance monitoring with system resource tracking
- **Deployment**: Production-ready configuration with environment-based settings
- **Maintenance**: Automated cleanup commands and system maintenance tools

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Backend Architecture](#backend-architecture)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Background Tasks & Celery Configuration](#background-tasks--celery-configuration)
- [AWS Integration](#aws-integration)
- [Security Features](#security-features)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Deployment Guide](#deployment-guide)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **PostgreSQL**: 12 or higher (production) or SQLite (development)
- **Redis**: 6.0 or higher
- **AWS Account**: With Bedrock access for AI features
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 20GB free space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd traible-llc.github.io
   git checkout traible-chat  # Switch to backend branch
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Update .env with your configuration (see Environment Variables section)
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start Redis** (required for caching and background tasks)
   ```bash
   redis-server
   ```

### Development

```bash
# Start Django development server
python manage.py runserver

# Start Celery worker (in separate terminal)
celery -A docbot worker -l info

# Run tests
python manage.py test

# Access API documentation
# http://localhost:8000/api/docs/  (Swagger UI)
# http://localhost:8000/api/redoc/ (ReDoc)

# Health checks
curl http://localhost:8000/health/
curl http://localhost:8000/health/detailed/
```

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/traible_db
# For development, you can use SQLite:
# DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS Configuration (for AI features)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
REGION_NAME=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend URL (for password recovery emails)
FRONTEND_URL=http://localhost:3000

# File Storage
MEDIA_ROOT=media/
STATIC_ROOT=static/
```

## Project Structure

```
├── accounts/              # User authentication and management
│   ├── models.py         # Custom User model with password reset functionality
│   ├── views.py          # Authentication views (login, signup, password reset)
│   ├── serializers.py    # DRF serializers for user data
│   ├── urls.py           # Authentication URL patterns
│   └── migrations/       # Database migrations for user model
├── chatbot/              # Core document processing and chat functionality
│   ├── models.py         # Document, Conversation, Message models
│   ├── views.py          # Document upload, chat, conversation management
│   ├── services/         # Business logic services
│   │   └── bedrock_service.py  # AWS Bedrock and AI integration
│   ├── tasks.py          # Celery background tasks
│   ├── health_views.py   # Health check and monitoring endpoints
│   ├── middleware.py     # Custom middleware for error handling and logging
│   ├── validators.py     # File and data validation
│   └── urls.py           # Chat and document API endpoints
├── docbot/               # Django project configuration
│   ├── settings.py       # Django settings with environment-based config
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI application entry point
│   └── asgi.py           # ASGI application entry point
├── client/               # Frontend React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Route components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utility libraries
│   │   ├── store/        # State management
│   │   └── test/         # Test setup
│   └── index.html        # HTML entry point
├── shared/               # Shared types and schemas
├── vector_stores/        # FAISS vector database storage
├── media/                # Uploaded document files
├── static/               # Static files
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── dist/                # Frontend build output
```

## Backend Architecture

### Django Applications

#### 1. **accounts** - User Management
- **Purpose**: Handles user authentication, registration, and password management
- **Key Features**:
  - Custom User model extending Django's AbstractUser
  - JWT-based authentication with refresh tokens
  - Secure password reset with rate limiting and token invalidation
  - Email verification system
  - Password strength validation

#### 2. **chatbot** - Core Business Logic
- **Purpose**: Document processing, AI chat, and conversation management
- **Key Features**:
  - Document upload and processing with progress tracking
  - AI-powered chat using AWS Bedrock Claude 3 Sonnet
  - Vector-based document search with FAISS
  - Conversation history and management
  - Background task processing with Celery
  - Health monitoring and system metrics

### Service Layer

#### **BedrockService** (`chatbot/services/bedrock_service.py`)
- **AWS Bedrock Integration**: Claude 3 Sonnet for AI responses
- **AWS Textract**: Document analysis and table extraction
- **Vector Search**: FAISS-based similarity search
- **Image Analysis**: OCR and technical diagram analysis
- **Rate Limiting**: Built-in throttling for AWS API calls

### Background Processing

#### **Celery Tasks** (`chatbot/tasks.py`)
- **Document Processing**: Asynchronous PDF processing with progress tracking
- **Resumable Processing**: Support for resuming failed document processing
- **Memory Management**: Efficient handling of large documents
- **Error Handling**: Comprehensive error tracking and retry logic

## API Documentation

### Authentication Endpoints

#### **POST** `/api/auth/signup/`
Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Registration successful.",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **POST** `/api/auth/login/`
Authenticate user and get JWT tokens.

**Request Body:**
```json
{
  "username_or_email": "john@example.com",
  "password": "SecurePassword123!"
}
```

#### **POST** `/api/auth/password-reset-request/`
Request password reset email.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

#### **POST** `/api/auth/password-reset-validate/`
Validate password reset token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "uid": "user_id_here"
}
```

#### **POST** `/api/auth/password-reset-confirm/`
Confirm password reset with new password.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "uid": "user_id_here",
  "password": "NewSecurePassword123!"
}
```

### Document Management Endpoints

#### **POST** `/api/documents/upload/`
Upload a PDF document for processing.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <PDF file>
```

**Response:**
```json
{
  "message": "Document uploaded and queued for processing",
  "document_id": 123,
  "processing_status": "PENDING",
  "title": "document.pdf"
}
```

#### **GET** `/api/documents/`
Get list of user's documents.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "title": "document.pdf",
      "is_processed": true,
      "created_at": "2024-01-01T12:00:00Z",
      "content_type": "application/pdf"
    }
  ]
}
```

#### **GET** `/api/documents/list/`
Get detailed list of user's documents with processing status.

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "title": "document.pdf",
      "created_at": "2024-01-01T12:00:00Z",
      "is_processed": true,
      "processing_status": "COMPLETED",
      "processing_progress": 100,
      "page_count": 25,
      "has_images": true,
      "image_count": 5,
      "file_size": 1024000,
      "download_url": "/api/documents/123/download/"
    }
  ]
}
```

#### **GET** `/api/documents/{document_id}/status/`
Get processing status of a specific document.

**Response:**
```json
{
  "document_id": 123,
  "title": "document.pdf",
  "is_processed": true,
  "processing_status": "COMPLETED",
  "processing_progress": 100,
  "processing_error": null,
  "has_images": true,
  "image_count": 5,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### **GET** `/api/documents/{document_id}/download/`
Download the original PDF file.

**Response:** Binary PDF file with appropriate headers.

#### **DELETE** `/api/documents/{document_id}/delete/`
Delete a document and its associated data.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

### Chat and Conversation Endpoints

#### **POST** `/api/chat/`
Send a message to the AI chat system.

**Request Body:**
```json
{
  "message": "What is the main topic of this document?",
  "document_ids": [123, 124],
  "conversation_id": "uuid-here",
  "stream": false
}
```

**Response:**
```json
{
  "conversation_id": "uuid-here",
  "message": "The main topic of the document is...",
  "document_ids": [123, 124]
}
```

#### **GET** `/api/conversations/`
Get list of user's conversations.

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid-here",
      "title": "What is the main topic of this document?",
      "created_at": "2024-01-01T12:00:00Z",
      "message_count": 4,
      "documents": [
        {
          "id": 123,
          "title": "document.pdf"
        }
      ]
    }
  ]
}
```

#### **GET** `/api/conversations/{conversation_id}/`
Get detailed conversation with message history.

**Response:**
```json
{
  "conversation": {
    "id": "uuid-here",
    "title": "What is the main topic of this document?",
    "created_at": "2024-01-01T12:00:00Z",
    "timeline": [
      {
        "type": "message",
        "id": "msg-uuid",
        "content": "What is the main topic of this document?",
        "role": "user",
        "created_at": "2024-01-01T12:00:00Z"
      },
      {
        "type": "message",
        "id": "msg-uuid-2",
        "content": "The main topic of the document is...",
        "role": "assistant",
        "created_at": "2024-01-01T12:01:00Z"
      }
    ]
  }
}
```

#### **POST** `/api/conversations/initialize/`
Create a new conversation.

**Request Body:**
```json
{
  "document_ids": [123, 124]
}
```

**Response:**
```json
{
  "conversation_id": "uuid-here",
  "documents": [
    {
      "id": 123,
      "title": "document.pdf"
    }
  ]
}
```

#### **DELETE** `/api/conversations/{conversation_id}/delete/`
Delete a conversation and all its messages.

**Response:**
```json
{
  "message": "Conversation deleted successfully"
}
```

### Health and Monitoring Endpoints

#### **GET** `/api/health/`
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "1.0.0"
}
```

#### **GET** `/api/health/detailed/`
Detailed health check with system metrics.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time": 0
    },
    "cache": {
      "status": "healthy"
    },
    "disk": {
      "status": "healthy",
      "free_space_gb": 45.2,
      "total_space_gb": 100.0,
      "free_percentage": 45.2
    },
    "memory": {
      "status": "healthy",
      "used_percentage": 65.4,
      "available_gb": 2.1
    }
  }
}
```

#### **GET** `/api/metrics/`
System performance metrics.

**Response:**
```json
{
  "timestamp": 1640995200.0,
  "system": {
    "cpu_percent": 25.4,
    "memory": {
      "total_gb": 8.0,
      "available_gb": 2.1,
      "used_percent": 73.8
    },
    "disk": {
      "total_gb": 100.0,
      "free_gb": 45.2,
      "used_percent": 54.8
    }
  },
  "process": {
    "pid": 12345,
    "memory_mb": 256.7,
    "cpu_percent": 12.3,
    "num_threads": 8
  }
}
```

#### **GET** `/api/readiness/`
Kubernetes readiness probe.

**Response:**
```json
{
  "status": "ready"
}
```

#### **GET** `/api/liveness/`
Kubernetes liveness probe.

**Response:**
```json
{
  "status": "alive"
}
```

## Database Models

### User Model (`accounts.models.User`)

Extends Django's `AbstractUser` with additional fields for enhanced user management.

**Fields:**
- `id`: Primary key (auto-generated)
- `username`: Unique username (max 150 chars)
- `email`: Unique email address
- `is_verified`: Boolean flag for email verification
- `reset_password_token`: Token for password reset (nullable)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `password_reset_attempts`: Counter for rate limiting (default: 0)
- `last_password_reset_attempt`: Timestamp of last reset attempt

**Key Methods:**
- `generate_password_reset_token()`: Creates secure reset token with cache storage
- `validate_password_reset_token(token)`: Validates token from cache
- `invalidate_password_reset_token(token)`: Removes token from cache
- `can_request_password_reset()`: Checks rate limiting (max 3 attempts/hour)

### Document Model (`chatbot.models.Document`)

Represents uploaded PDF documents with processing status and metadata.

**Fields:**
- `id`: Primary key (auto-generated)
- `user`: Foreign key to User model
- `title`: Document filename
- `file`: FileField for PDF storage
- `content_type`: MIME type of the file
- `created_at`: Upload timestamp
- `is_processed`: Boolean flag for processing completion
- `vector_store_path`: Path to FAISS vector store
- `raw_text`: Extracted text content
- `processing_error`: Error message if processing failed
- `file_hash`: MD5 hash for duplicate detection
- `has_images`: Boolean flag indicating image presence
- `image_count`: Number of images found
- `image_data`: JSON field storing image analysis results
- `extracted_tables`: JSON field storing table data
- `processing_status`: Status enum (PENDING, PROCESSING, COMPLETED, FAILED)
- `task_id`: Celery task ID for processing
- `processing_progress`: Progress percentage (0-100)
- `last_processed_page`: Last processed page for resumable processing
- `page_data`: JSON field storing page-by-page data

**Constraints:**
- Unique constraint on `(user, file_hash)` to prevent duplicate uploads
- Indexes on `(user, created_at)`, `processing_status`, `is_processed`, `created_at`

### Conversation Model (`chatbot.models.Conversation`)

Represents chat conversations between users and the AI system.

**Fields:**
- `id`: UUID primary key
- `user`: Foreign key to User model
- `title`: Conversation title (auto-generated from first message)
- `created_at`: Conversation start timestamp
- `document_key`: Comma-separated document IDs for this conversation
- `updated_at`: Last activity timestamp

**Indexes:**
- `(user, created_at)`: For user's conversation history
- `document_key`: For document-based queries
- `updated_at`: For activity-based sorting

### Message Model (`chatbot.models.Message`)

Represents individual messages within conversations.

**Fields:**
- `id`: UUID primary key
- `conversation`: Foreign key to Conversation model
- `content`: Message text content
- `role`: Message role ('user' or 'assistant')
- `created_at`: Message timestamp
- `references`: JSON field storing document references and context

**Indexes:**
- `(conversation, created_at)`: For conversation message ordering
- `role`: For role-based queries
- `created_at`: For time-based queries

### Model Relationships

```
User (1) ──→ (N) Document
User (1) ──→ (N) Conversation
Conversation (1) ──→ (N) Message
Document (N) ──→ (N) Conversation (through document_key)
```

### Database Indexes

**Performance Optimizations:**
- User-based queries: `(user, created_at)` indexes
- Processing status: `processing_status` index for task monitoring
- Document access: `(user, file_hash)` unique constraint
- Conversation history: `(user, created_at)` for efficient pagination
- Message ordering: `(conversation, created_at)` for timeline display

## Background Tasks & Celery Configuration

### Celery Setup

The application uses Celery for asynchronous task processing, particularly for document processing which can be time-intensive.

**Configuration:**
- **Broker**: Redis (localhost:6379/0)
- **Result Backend**: Django database (django-db)
- **Task Timeout**: 4 hours (14400 seconds)
- **Soft Timeout**: 3.9 hours (14100 seconds)
- **Max Retries**: 3 attempts with 60-second intervals
- **Ack Late**: True (tasks acknowledged after completion)

### Task Definitions

#### **process_document_task** (`chatbot.tasks.process_document_task`)

**Purpose**: Asynchronously process uploaded PDF documents with comprehensive content extraction.

**Features:**
- **Resumable Processing**: Can resume from last processed page if interrupted
- **Progress Tracking**: Real-time progress updates (0-100%)
- **Memory Management**: Processes large documents in chunks to prevent memory issues
- **Error Handling**: Comprehensive error tracking with retry logic
- **Content Extraction**: Text, images, tables, and technical diagrams

**Processing Pipeline:**
1. **Text Extraction**: Extract raw text using PyPDF2
2. **Rich Content Analysis**: 
   - Convert pages to images using pdf2image
   - OCR text extraction with pytesseract
   - Image analysis with AWS Textract for tables
   - Technical diagram analysis with Claude 3 Vision
3. **Vector Store Creation**: Generate embeddings and create FAISS vector store
4. **Progress Updates**: Update database with processing status and progress

**Task Configuration:**
```python
@shared_task(
    bind=True, 
    name="process_document_task", 
    time_limit=14400, 
    soft_time_limit=14100,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    acks_late=True
)
```

**Memory Optimization:**
- Processes documents in configurable chunks (30-100 pages based on document size)
- Garbage collection after each chunk
- Intermediate result saving to prevent data loss
- Efficient handling of large documents (300+ pages)

#### **test_task** (`chatbot.tasks.test_task`)

**Purpose**: Simple test task to verify Celery worker functionality.

**Usage**: Development and debugging tool to ensure Celery is properly configured.

### Celery Worker Management

**Starting Workers:**
```bash
# Start Celery worker
celery -A docbot worker -l info

# Start with specific concurrency
celery -A docbot worker -l info --concurrency=4

# Start with auto-scaling
celery -A docbot worker -l info --autoscale=10,3
```

**Monitoring Tasks:**
```bash
# Monitor task queue
celery -A docbot inspect active

# Check worker status
celery -A docbot inspect stats

# View task results
celery -A docbot result <task_id>
```

### Redis Configuration

**Connection Settings:**
- **Host**: localhost
- **Port**: 6379
- **Database**: 0 (broker), 1 (cache)
- **Connection Pool**: 100 max connections
- **Timeout**: 30 seconds connection, 60 seconds socket
- **Keepalive**: TCP keepalive enabled

**Redis Usage:**
- **Task Queue**: Document processing tasks
- **Result Storage**: Task results and status
- **Caching**: Session data and password reset tokens
- **Rate Limiting**: API rate limiting counters

### Task Monitoring & Debugging

**Progress Tracking:**
- Real-time progress updates in database
- Task status monitoring (PENDING, PROCESSING, COMPLETED, FAILED)
- Error logging with detailed error messages
- Resumable processing for failed tasks

**Logging:**
- Comprehensive task logging with Celery's built-in logger
- Error tracking with stack traces
- Performance metrics and timing information
- Memory usage monitoring

**Health Checks:**
- Worker availability monitoring
- Task queue depth monitoring
- Redis connection health checks
- Task completion rate tracking

## AWS Integration

### AWS Bedrock Integration

The application leverages AWS Bedrock for AI-powered document analysis and chat functionality using Claude 3 Sonnet.

#### **BedrockService** (`chatbot/services/bedrock_service.py`)

**Core Features:**
- **Claude 3 Sonnet Integration**: Advanced language model for document analysis and chat
- **Streaming Responses**: Real-time response streaming for better user experience
- **Rate Limiting**: Built-in throttling to respect AWS API limits
- **Error Handling**: Comprehensive retry logic with exponential backoff

**Configuration:**
```python
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
REGION_NAME=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**Rate Limiting:**
- **Per Second**: 1.5 calls/second
- **Per Minute**: 80 calls/minute
- **Retry Logic**: 5 attempts with exponential backoff
- **Jitter**: Random delays to prevent thundering herd

#### **Document Analysis Pipeline**

**1. Text Extraction:**
- PyPDF2 for basic text extraction
- OCR with pytesseract for scanned documents
- Text cleaning and normalization

**2. Image Analysis:**
- PDF to image conversion using pdf2image
- OpenCV for image preprocessing
- Claude 3 Vision for technical diagram analysis
- Blank page detection and filtering

**3. Table Extraction:**
- AWS Textract for table detection and extraction
- Structured table data with row/column mapping
- Integration with document content

**4. Vector Embeddings:**
- Amazon Titan Embeddings for text vectorization
- FAISS vector store for similarity search
- Chunk-based processing for large documents

### AWS Textract Integration

**Purpose**: Advanced document analysis for table and form extraction.

**Features:**
- **Table Detection**: Automatic table identification and extraction
- **Form Analysis**: Structured data extraction from forms
- **Text Recognition**: OCR for scanned documents
- **Layout Analysis**: Understanding document structure

**Usage:**
```python
# Table extraction from document images
response = self.textract_client.analyze_document(
    Document={'Bytes': img_bytes},
    FeatureTypes=['TABLES', 'FORMS']
)
```

### Vector Search & Embeddings

#### **FAISS Vector Store**

**Purpose**: Efficient similarity search across document content.

**Features:**
- **User Isolation**: Separate vector stores per user
- **Document Segmentation**: Chunk-based storage for large documents
- **Similarity Search**: Cosine similarity for relevant content retrieval
- **Metadata Tracking**: Document and page references

**Storage Structure:**
```
vector_stores/
├── user_1/
│   ├── document_123/
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── document_124/
└── user_2/
    └── document_125/
```

#### **Embedding Process**

**Text Chunking:**
- Recursive character text splitter
- Chunk size: 1000 characters
- Overlap: 200 characters
- Preserves context across chunks

**Embedding Generation:**
- Amazon Titan Embeddings model
- 1536-dimensional vectors
- Batch processing for efficiency
- Error handling and retry logic

### AI Chat System

#### **Claude 3 Sonnet Integration**

**Model Configuration:**
- **Model**: anthropic.claude-3-sonnet-20240229-v1:0
- **Max Tokens**: 1000 for responses, 1500 for image analysis
- **Temperature**: 0.2 for focused responses
- **Streaming**: Real-time response generation

**Chat Features:**
- **Context-Aware Responses**: Uses document content and conversation history
- **Image Analysis**: Technical diagram and machinery analysis
- **Streaming Support**: Real-time response streaming
- **Reference Tracking**: Document and page references in responses

#### **Response Generation Pipeline**

**1. Query Processing:**
- Document relevance scoring
- Multi-document search
- Context aggregation

**2. Prompt Engineering:**
- Context injection
- Conversation history
- Specialized prompts for image questions

**3. Response Generation:**
- Streaming or batch responses
- Reference tracking
- Error handling

**Example Chat Flow:**
```python
# 1. Search relevant documents
search_results, errors = bedrock.search_documents(
    query=user_message,
    document_ids=selected_documents,
    user_id=user.id
)

# 2. Generate response with context
response = bedrock.get_response(
    question=user_message,
    context=aggregated_context,
    conversation_history=message_history,
    stream=stream_mode
)
```

### Security & Best Practices

**AWS Security:**
- IAM roles with minimal required permissions
- Environment-based credential management
- Secure token handling and rotation
- API rate limiting and monitoring

**Data Privacy:**
- User data isolation in vector stores
- Secure document storage
- No data persistence in AWS services
- Local processing for sensitive content

**Error Handling:**
- Comprehensive retry logic
- Graceful degradation
- Detailed error logging
- User-friendly error messages

## Security Features

### Authentication & Authorization

#### **JWT Authentication**
- **Access Tokens**: 7-day expiration with secure generation
- **Refresh Tokens**: 10-year expiration for long-term sessions
- **Token Rotation**: Optional refresh token rotation
- **Blacklisting**: Token invalidation support
- **Secure Headers**: Bearer token authentication

#### **User Management**
- **Custom User Model**: Extended Django AbstractUser
- **Email Verification**: Required for account activation
- **Password Security**: Strong password validation
- **Account Lockout**: Rate limiting for failed login attempts

### Password Security

#### **Password Reset System**
- **Secure Tokens**: Cryptographically secure token generation using `secrets.token_urlsafe(32)`
- **Cache-Based Storage**: Tokens stored in Redis with 1-hour expiration
- **Rate Limiting**: Maximum 3 reset attempts per hour per user
- **Single Use**: Tokens invalidated after successful password reset
- **Email Privacy**: No information disclosure about account existence

#### **Password Validation**
- **Django Validators**: Built-in password strength validation
- **Minimum Length**: Configurable minimum password length
- **Common Passwords**: Protection against common passwords
- **Numeric Passwords**: Prevention of purely numeric passwords
- **User Attribute Similarity**: Prevention of passwords similar to user info

### API Security

#### **Rate Limiting**
- **Authenticated Users**: 1000 requests per hour
- **Anonymous Users**: 100 requests per hour
- **Custom Middleware**: `RateLimitMiddleware` for granular control
- **IP-Based Limiting**: Additional IP-based rate limiting
- **Graceful Degradation**: Proper error responses for rate limit exceeded

#### **Input Validation**
- **File Validation**: Magic number validation for uploaded files
- **MIME Type Checking**: Content type verification
- **File Size Limits**: Configurable file size restrictions
- **SQL Injection Protection**: Parameterized queries throughout
- **XSS Protection**: Input sanitization and output encoding

### CORS & Headers

#### **CORS Configuration**
- **Development**: All origins allowed for development
- **Production**: Configurable allowed origins
- **Credentials**: Secure credential handling
- **Headers**: Custom header support

#### **Security Headers**
- **X-Frame-Options**: Clickjacking protection
- **Content Security Policy**: XSS protection
- **HSTS**: HTTP Strict Transport Security
- **X-Content-Type-Options**: MIME type sniffing protection

### Custom Middleware

#### **ErrorHandlingMiddleware**
- **Structured Errors**: Consistent error response format
- **Error Logging**: Comprehensive error logging
- **Graceful Degradation**: User-friendly error messages
- **Security**: No sensitive information in error responses

#### **RequestLoggingMiddleware**
- **Request Tracking**: Log all incoming requests
- **Performance Monitoring**: Request timing and metrics
- **Security Auditing**: Track suspicious activity
- **Debug Information**: Development debugging support

#### **RateLimitMiddleware**
- **IP-Based Limiting**: Per-IP request limiting
- **User-Based Limiting**: Per-user request limiting
- **Endpoint-Specific**: Different limits for different endpoints
- **Redis Backend**: Scalable rate limiting with Redis

### File Security

#### **Upload Security**
- **File Type Validation**: Only PDF files allowed
- **Magic Number Checking**: File signature verification
- **Virus Scanning**: Optional malware scanning
- **Size Limits**: Configurable file size restrictions
- **Duplicate Detection**: MD5 hash-based duplicate prevention

#### **Storage Security**
- **Secure Paths**: Safe file storage paths
- **Access Control**: User-based file access control
- **Cleanup**: Automatic cleanup of orphaned files
- **Backup**: Secure backup and recovery procedures

### Data Protection

#### **Encryption**
- **At Rest**: Database encryption support
- **In Transit**: HTTPS/TLS encryption
- **Sensitive Data**: Password and token encryption
- **Key Management**: Secure key storage and rotation

#### **Privacy**
- **Data Isolation**: User data separation
- **Minimal Data**: Only necessary data collection
- **Retention Policies**: Configurable data retention
- **GDPR Compliance**: Privacy regulation compliance

### Monitoring & Auditing

#### **Security Logging**
- **Authentication Events**: Login/logout tracking
- **Failed Attempts**: Security event logging
- **Admin Actions**: Administrative action auditing
- **Error Tracking**: Security-related error monitoring

#### **Health Monitoring**
- **System Health**: Regular health checks
- **Security Metrics**: Security-related metrics
- **Alert System**: Automated security alerts
- **Incident Response**: Security incident procedures

### Environment Security

#### **Configuration Management**
- **Environment Variables**: Secure configuration storage
- **Secret Management**: Secure secret handling
- **Development vs Production**: Environment-specific security
- **Configuration Validation**: Security setting validation

#### **Deployment Security**
- **Container Security**: Docker security best practices
- **Network Security**: Secure network configuration
- **Access Control**: Restricted access to production systems
- **Backup Security**: Secure backup procedures

## Monitoring & Health Checks

### Health Check Endpoints

The application provides comprehensive health monitoring endpoints for system reliability and Kubernetes deployment.

#### **Basic Health Check** (`/api/health/`)

**Purpose**: Simple health status endpoint for load balancers and monitoring systems.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "1.0.0"
}
```

**Use Cases:**
- Load balancer health checks
- Basic service availability
- Simple monitoring integration

#### **Detailed Health Check** (`/api/health/detailed/`)

**Purpose**: Comprehensive system health assessment with component status.

**Checks Performed:**
- **Database Connectivity**: PostgreSQL/SQLite connection test
- **Cache System**: Redis cache functionality test
- **Disk Space**: Available disk space monitoring
- **Memory Usage**: System memory utilization
- **Vector Store**: FAISS vector store accessibility

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time": 0
    },
    "cache": {
      "status": "healthy"
    },
    "disk": {
      "status": "healthy",
      "free_space_gb": 45.2,
      "total_space_gb": 100.0,
      "free_percentage": 45.2
    },
    "memory": {
      "status": "healthy",
      "used_percentage": 65.4,
      "available_gb": 2.1
    },
    "vector_store": {
      "status": "healthy",
      "path": "/app/vector_stores"
    }
  }
}
```

**Status Levels:**
- **healthy**: All systems operational
- **warning**: Some systems degraded but functional
- **unhealthy**: Critical systems failing

#### **System Metrics** (`/api/metrics/`)

**Purpose**: Detailed system performance metrics for monitoring and alerting.

**Metrics Collected:**
- **CPU Usage**: Current CPU utilization percentage
- **Memory**: Total, available, and used memory
- **Disk**: Total, free, and used disk space
- **Process**: Application-specific process metrics

**Response:**
```json
{
  "timestamp": 1640995200.0,
  "system": {
    "cpu_percent": 25.4,
    "memory": {
      "total_gb": 8.0,
      "available_gb": 2.1,
      "used_percent": 73.8
    },
    "disk": {
      "total_gb": 100.0,
      "free_gb": 45.2,
      "used_percent": 54.8
    }
  },
  "process": {
    "pid": 12345,
    "memory_mb": 256.7,
    "cpu_percent": 12.3,
    "num_threads": 8
  }
}
```

### Kubernetes Probes

#### **Readiness Probe** (`/api/readiness/`)

**Purpose**: Kubernetes readiness probe to determine if the application is ready to receive traffic.

**Checks:**
- Database connectivity
- Cache system availability
- Essential services status

**Response:**
```json
{
  "status": "ready"
}
```

**HTTP Status Codes:**
- **200**: Application ready to serve requests
- **503**: Application not ready (service unavailable)

#### **Liveness Probe** (`/api/liveness/`)

**Purpose**: Kubernetes liveness probe to determine if the application is alive and should be restarted.

**Response:**
```json
{
  "status": "alive"
}
```

**HTTP Status Codes:**
- **200**: Application is alive and functioning
- **500**: Application is dead and should be restarted

### Monitoring Integration

#### **Prometheus Metrics**

**Available Metrics:**
- HTTP request duration
- HTTP request count
- Database query performance
- Cache hit/miss ratios
- Task queue depth
- Document processing metrics

**Integration:**
```python
# Example Prometheus integration
from prometheus_client import Counter, Histogram, Gauge

http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_tasks = Gauge('celery_active_tasks', 'Number of active Celery tasks')
```

#### **Logging Configuration**

**Structured Logging:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'application.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'chatbot': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Performance Monitoring

#### **Application Performance**

**Key Metrics:**
- Request response times
- Database query performance
- Cache hit rates
- Memory usage patterns
- CPU utilization
- Task processing times

**Monitoring Tools:**
- Django Debug Toolbar (development)
- Custom performance middleware
- Celery monitoring
- Database query analysis

#### **Business Metrics**

**Document Processing:**
- Documents processed per hour
- Processing success rate
- Average processing time
- Queue depth and wait times

**User Activity:**
- Active users
- API usage patterns
- Chat session metrics
- Document upload frequency

### Alerting & Notifications

#### **Health Check Alerts**

**Alert Conditions:**
- Service unavailable (503 status)
- High memory usage (>90%)
- Low disk space (<10%)
- Database connection failures
- Cache system failures

**Notification Channels:**
- Email alerts
- Slack notifications
- PagerDuty integration
- Custom webhook endpoints

#### **Performance Alerts**

**Alert Thresholds:**
- High response times (>5 seconds)
- High error rates (>5%)
- Queue backlog (>100 tasks)
- Memory leaks detection
- CPU usage spikes

### Maintenance & Cleanup

#### **Automated Cleanup**

**Scheduled Tasks:**
- Orphaned file cleanup
- Expired token removal
- Log file rotation
- Database maintenance
- Vector store optimization

**Cleanup Commands:**
```bash
# Clean up expired password reset tokens
python manage.py cleanup_tokens

# Remove orphaned files
python manage.py cleanup_files

# Optimize vector stores
python manage.py optimize_vector_stores
```

#### **System Maintenance**

**Regular Maintenance:**
- Database optimization
- Cache cleanup
- Log rotation
- Backup verification
- Security updates

**Monitoring Maintenance:**
- Health check validation
- Alert rule testing
- Performance baseline updates
- Capacity planning

## Deployment Guide

### Production Setup

#### **Environment Configuration**

**Required Environment Variables:**
```bash
# Django Settings
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/traible_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
REGION_NAME=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Email Configuration
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@yourdomain.com

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### **Database Setup**

**PostgreSQL Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE traible_prod;
CREATE USER traible_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE traible_prod TO traible_user;
\q
```

**Database Migration:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### **Redis Setup**

**Redis Installation:**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
```

#### **Static Files & Media**

**Static Files Collection:**
```bash
python manage.py collectstatic --noinput
```

**Media Directory Setup:**
```bash
mkdir -p media/documents
chmod 755 media/documents
```

### Web Server Configuration

#### **Nginx Configuration**

**Nginx Virtual Host:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

#### **Gunicorn Configuration**

**Gunicorn Service:**
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
EOF
```

**Systemd Service:**
```ini
[Unit]
Description=Traible Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py docbot.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Celery Configuration

#### **Celery Worker Service**

**Systemd Service for Celery:**
```ini
[Unit]
Description=Traible Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/venv/bin/celery -A docbot worker -l info --detach
ExecStop=/path/to/venv/bin/celery -A docbot control shutdown
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Beat Service (for scheduled tasks):**
```ini
[Unit]
Description=Traible Celery Beat
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/venv/bin/celery -A docbot beat -l info --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

#### **Dockerfile**

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        redis-tools \
        tesseract-ocr \
        poppler-utils \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories
RUN mkdir -p media vector_stores static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "docbot.wsgi:application"]
```

#### **Docker Compose**

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: traible_prod
      POSTGRES_USER: traible_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 docbot.wsgi:application
    volumes:
      - .:/app
      - media_data:/app/media
      - vector_data:/app/vector_stores
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://traible_user:secure_password@db:5432/traible_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A docbot worker -l info
    volumes:
      - .:/app
      - media_data:/app/media
      - vector_data:/app/vector_stores
    environment:
      - DATABASE_URL=postgresql://traible_user:secure_password@db:5432/traible_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A docbot beat -l info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://traible_user:secure_password@db:5432/traible_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
  media_data:
  vector_data:
```

### Kubernetes Deployment

#### **Deployment YAML**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: traible-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: traible-backend
  template:
    metadata:
      labels:
        app: traible-backend
    spec:
      containers:
      - name: traible-backend
        image: your-registry/traible-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: traible-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: traible-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: traible-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /api/liveness/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/readiness/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: traible-backend-service
spec:
  selector:
    app: traible-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### SSL/TLS Configuration

#### **Let's Encrypt with Certbot**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Backup Strategy

#### **Database Backup**

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="traible_prod"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U traible_user $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

#### **Media Files Backup**

```bash
#!/bin/bash
# backup_media.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/media"
MEDIA_DIR="/path/to/your/project/media"

mkdir -p $BACKUP_DIR

# Create tar backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .

# Remove backups older than 30 days
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +30 -delete
```

### Monitoring & Logging

#### **Log Rotation**

```bash
# /etc/logrotate.d/traible
/path/to/your/project/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload traible-backend
    endscript
}
```

#### **Health Check Monitoring**

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="https://yourdomain.com/api/health/detailed/"
ALERT_EMAIL="admin@yourdomain.com"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response != "200" ]; then
    echo "Health check failed with status: $response" | mail -s "Traible Health Check Failed" $ALERT_EMAIL
fi
```

### Performance Optimization

#### **Database Optimization**

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_documents_user_created ON documents(user_id, created_at);
CREATE INDEX CONCURRENTLY idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX CONCURRENTLY idx_conversations_user_created ON conversations(user_id, created_at);

-- Analyze tables for query optimization
ANALYZE documents;
ANALYZE messages;
ANALYZE conversations;
```

#### **Redis Optimization**

```bash
# Redis configuration optimization
echo "maxmemory 1gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
echo "save 900 1" >> /etc/redis/redis.conf
echo "save 300 10" >> /etc/redis/redis.conf
echo "save 60 10000" >> /etc/redis/redis.conf
```

### Security Hardening

#### **Firewall Configuration**

```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### **System Security**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban for SSH
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Tech Stack

### Backend Technologies
- **Framework**: Django 4.2.19 with Django REST Framework 3.15.2
- **Database**: SQLite (development) / PostgreSQL (production) with psycopg2-binary
- **Authentication**: JWT with django-rest-framework-simplejwt
- **Task Queue**: Celery 5.4.0 with Redis broker
- **AI/ML**: AWS Bedrock (Claude 3 Sonnet), AWS Textract, LangChain
- **Vector Database**: FAISS for document embeddings
- **File Processing**: PyPDF2, pdf2image, pytesseract, OpenCV
- **Caching**: Redis with django-redis
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Security**: django-cors-headers, django-ratelimit
- **Development**: django-debug-toolbar, django-extensions

### Frontend Technologies
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Custom stores (Zustand-like)
- **UI Components**: Radix UI primitives with custom styling
- **Testing**: Vitest, React Testing Library
- **Code Quality**: ESLint, Prettier

### Infrastructure & DevOps
- **Containerization**: Docker support
- **Process Management**: Celery workers
- **Monitoring**: Health checks, metrics endpoints
- **Logging**: Structured logging with Python logging
- **Environment Management**: python-decouple for configuration

## Development Workflow

### Local Development Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd traible-llc.github.io
   git checkout traible-chat
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start Services**:
   ```bash
   # Terminal 1: Django server
   python manage.py runserver
   
   # Terminal 2: Celery worker
   celery -A docbot worker -l info
   
   # Terminal 3: Redis (if not running)
   redis-server
   ```

### Testing

**Run Tests**:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test chatbot

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

**Test Structure**:
- Unit tests for models and business logic
- Integration tests for API endpoints
- Security tests for authentication and authorization
- Performance tests for document processing

### Code Quality

**Linting and Formatting**:
```bash
# Python linting
flake8 .
black .
isort .

# Type checking
mypy .

# Frontend linting
npm run lint
npm run format
```

**Pre-commit Hooks**:
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

### API Documentation

**Interactive Documentation**:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

**Schema Generation**:
```bash
# Generate OpenAPI schema
python manage.py spectacular --file schema.yml
```

## Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 and Django best practices
2. **Testing**: Write tests for all new features and bug fixes
3. **Documentation**: Update documentation for API changes
4. **Security**: Follow security best practices and review sensitive code
5. **Performance**: Consider performance implications of changes

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Issue Reporting

When reporting issues, please include:
- **Environment**: OS, Python version, Django version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Screenshots**: If applicable

### Feature Requests

For feature requests, please provide:
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Additional Context**: Any other relevant information

## Support

### Getting Help

- **Documentation**: Check this README and inline code documentation
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team for urgent issues

### Troubleshooting

**Common Issues**:

1. **Celery Worker Not Starting**:
   - Check Redis connection: `redis-cli ping`
   - Verify environment variables
   - Check worker logs: `celery -A docbot worker -l debug`

2. **Document Processing Fails**:
   - Check AWS credentials and permissions
   - Verify file format (PDF only)
   - Check available disk space
   - Review task logs in Django admin

3. **Database Connection Issues**:
   - Verify database is running
   - Check connection string format
   - Ensure database exists and user has permissions

4. **Authentication Problems**:
   - Check JWT token expiration
   - Verify CORS settings
   - Check email configuration for password reset

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Django**: Web framework
- **AWS Bedrock**: AI/ML services
- **LangChain**: LLM application framework
- **FAISS**: Vector similarity search
- **Celery**: Distributed task queue
- **Redis**: In-memory data store
- **PostgreSQL**: Relational database
