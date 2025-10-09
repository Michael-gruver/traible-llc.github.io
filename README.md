# Traible Backend - Document Intelligence Platform

A comprehensive Django-based backend system for document intelligence, AI chat functionality, and secure user management. Built with modern Python technologies and enterprise-grade features.

## Features
## Features

### Core Features
- **Document Processing**: Upload, analyze, and process PDF documents with AI-powered text extraction, image analysis, and table recognition
- **AI Chat System**: Interactive chat with AI about document content using AWS Bedrock Claude 3 Sonnet
- **User Authentication**: Secure JWT-based authentication with comprehensive user management
- **Password Recovery**: Complete password reset system with security best practices and rate limiting
- **File Management**: Secure file upload, validation, and storage with duplicate detection
- **Background Tasks**: Asynchronous document processing with Celery integration and progress tracking
- **Health Monitoring**: Comprehensive system health checks, metrics, and Kubernetes-ready probes

### Security Features
- **Rate Limiting**: Configurable API rate limiting (1000/hour authenticated, 100/hour anonymous)
- **Input Validation**: Comprehensive file and data validation with security scanning
- **Token Security**: Cryptographically secure token generation and management with cache-based invalidation
- **Email Privacy**: Secure email handling without information disclosure
- **File Security**: Magic number validation, MIME type checking, and file hash verification
- **CORS Protection**: Secure cross-origin request handling
- **SQL Injection Protection**: Query sanitization and parameterized queries
- **Password Security**: Strong password validation and secure reset mechanisms

### Developer Experience
- **API Documentation**: Interactive Swagger UI and ReDoc documentation with comprehensive examples
- **Comprehensive Testing**: Unit tests, integration tests, and security tests
- **Error Handling**: Structured error responses with detailed logging and graceful degradation
- **Development Tools**: Debug toolbar, Django extensions, and development utilities
- **Type Safety**: Python type hints and comprehensive validation
- **Hot Reload**: Fast development with Django's built-in server

### Production Features
- **Scalability**: Horizontal scaling support with stateless design and Redis caching
- **Caching**: Redis integration with model-level caching and session management
- **Database Optimization**: Strategic indexes, query optimization, and connection pooling
- **Monitoring**: Health checks, metrics, and performance monitoring with system resource tracking
- **Deployment**: Production-ready configuration with environment-based settings
- **Maintenance**: Automated cleanup commands and system maintenance tools

## Table of Contents
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

- **POST** `/api/auth/signup/` - Register a new user account
- **POST** `/api/auth/login/` - Authenticate user and get JWT tokens
- **POST** `/api/auth/password-reset-request/` - Request password reset email
- **POST** `/api/auth/password-reset-validate/` - Validate password reset token
- **POST** `/api/auth/password-reset-confirm/` - Confirm password reset with new password

### Document Management Endpoints

- **POST** `/api/documents/upload/` - Upload a PDF document for processing
- **GET** `/api/documents/` - Get list of user's documents
- **GET** `/api/documents/list/` - Get detailed list with processing status
- **GET** `/api/documents/{document_id}/status/` - Get processing status of specific document
- **GET** `/api/documents/{document_id}/download/` - Download the original PDF file
- **DELETE** `/api/documents/{document_id}/delete/` - Delete a document and its associated data

### Chat and Conversation Endpoints

- **POST** `/api/chat/` - Send a message to the AI chat system
- **GET** `/api/conversations/` - Get list of user's conversations
- **GET** `/api/conversations/{conversation_id}/` - Get detailed conversation with message history
- **POST** `/api/conversations/initialize/` - Create a new conversation
- **DELETE** `/api/conversations/{conversation_id}/delete/` - Delete a conversation and all its messages

### Health and Monitoring Endpoints

- **GET** `/api/health/` - Basic health check
- **GET** `/api/health/detailed/` - Detailed health check with system metrics
- **GET** `/api/metrics/` - System performance metrics

- **GET** `/api/readiness/` - Kubernetes readiness probe
- **GET** `/api/liveness/` - Kubernetes liveness probe

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
- Time limit: 4 hours (14400 seconds)
- Max retries: 3 attempts with 60-second intervals
- Late acknowledgment enabled
- Auto-retry on exceptions

**Memory Optimization:**
- Processes documents in configurable chunks (30-100 pages based on document size)
- Garbage collection after each chunk
- Intermediate result saving to prevent data loss
- Efficient handling of large documents (300+ pages)

#### **test_task** (`chatbot.tasks.test_task`)

**Purpose**: Simple test task to verify Celery worker functionality.

**Usage**: Development and debugging tool to ensure Celery is properly configured.

### Celery Worker Management

**Worker Management:**
- Start worker: `celery -A docbot worker -l info`
- Monitor tasks: `celery -A docbot inspect active`
- Check worker status: `celery -A docbot inspect stats`

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
- AWS credentials and region configuration
- Claude 3 Sonnet model integration
- Rate limiting and retry logic

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
- Table detection and extraction from document images
- Form analysis and structured data extraction
- OCR for scanned documents

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

**Chat Flow:**
1. Search relevant documents using vector similarity
2. Aggregate context from multiple documents
3. Generate AI response with conversation history
4. Support both streaming and batch responses

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
- HTTP request metrics (count, duration)
- Database query performance
- Cache hit/miss ratios
- Task queue depth and processing metrics

#### **Logging Configuration**

**Structured Logging:**
- File and console handlers with different formatters
- JSON formatting for production environments
- Separate log levels for Django and application components
- Comprehensive error tracking and debugging information

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
- `python manage.py cleanup_tokens` - Clean up expired password reset tokens
- `python manage.py cleanup_files` - Remove orphaned files
- `python manage.py optimize_vector_stores` - Optimize vector stores

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
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- Database configuration (DATABASE_URL)
- Redis configuration (REDIS_URL)
- AWS credentials and region settings
- Email configuration for notifications
- Frontend URL and CORS settings

#### **Database Setup**

**PostgreSQL Setup:**
- Install PostgreSQL and create database
- Create user with appropriate permissions
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

#### **Redis Setup**

**Redis Setup:**
- Install and start Redis server
- Enable auto-start on boot
- Test connection with `redis-cli ping`

#### **Static Files & Media**

**Setup:**
- Collect static files: `python manage.py collectstatic --noinput`
- Create media directories with proper permissions

### Web Server Configuration

#### **Nginx Configuration**

**Requirements:**
- SSL/TLS termination with Let's Encrypt
- Proxy pass to Gunicorn on port 8000
- Static file serving with caching headers
- File upload support (100MB max)

#### **Gunicorn Configuration**

**Setup:**
- Install Gunicorn: `pip install gunicorn`
- Configure workers, timeouts, and connection limits
- Create systemd service for auto-start and management

### Celery Configuration

#### **Celery Worker Service**

**Setup:**
- Create systemd services for Celery worker and beat scheduler
- Configure auto-start and restart policies
- Set proper user permissions and environment variables

### Docker Deployment

#### **Dockerfile**

**Key Components:**
- Python 3.9 slim base image
- System dependencies (PostgreSQL client, Redis tools, OCR libraries)
- Python dependencies from requirements.txt
- Static file collection and directory setup
- Gunicorn as WSGI server

#### **Docker Compose**

**Services:**
- PostgreSQL database with persistent volumes
- Redis for caching and task queue
- Web application with Gunicorn
- Celery worker for background tasks
- Celery beat for scheduled tasks
- Shared volumes for media and vector stores

### Kubernetes Deployment

#### **Kubernetes Deployment**

**Key Features:**
- 3 replicas for high availability
- Health checks (liveness and readiness probes)
- Resource limits and requests
- Environment variables from secrets
- LoadBalancer service for external access

### SSL/TLS Configuration

#### **SSL/TLS Configuration**

**Setup:**
- Install Certbot for Let's Encrypt certificates
- Obtain certificates for domain
- Configure auto-renewal with cron job

### Backup Strategy

#### **Backup Strategy**

**Database Backup:**
- Automated PostgreSQL dumps with compression
- 30-day retention policy
- Scheduled daily backups

**Media Files Backup:**
- Compressed tar archives of uploaded documents
- Automated cleanup of old backups
- Regular backup verification

### Monitoring & Logging

#### **Monitoring & Logging**

**Log Rotation:**
- Daily log rotation with 52-week retention
- Compression and cleanup of old logs
- Automatic service reload after rotation

**Health Check Monitoring:**
- Automated health check scripts
- Email alerts for service failures
- Integration with monitoring systems

### Performance Optimization

#### **Performance Optimization**

**Database Optimization:**
- Strategic indexes on frequently queried columns
- Regular table analysis for query optimization
- Connection pooling and query caching

**Redis Optimization:**
- Memory limits and eviction policies
- Persistent storage configuration
- Connection pooling and timeout settings

### Security Hardening

#### **Security Hardening**

**Firewall Configuration:**
- UFW firewall with restrictive default policies
- Allow only necessary ports (SSH, HTTP, HTTPS)
- Deny all incoming traffic by default

**System Security:**
- Regular system updates and security patches
- Fail2ban for intrusion prevention
- SSH security hardening

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

1. **Clone and Setup**: Clone repository, create virtual environment, install dependencies
2. **Environment Configuration**: Copy and configure environment variables
3. **Database Setup**: Run migrations and create superuser
4. **Start Services**: Start Django server, Celery worker, and Redis

### Testing

**Testing:**
- Run all tests: `python manage.py test`
- Run specific app tests: `python manage.py test accounts`
- Coverage reporting with coverage.py
- Unit, integration, security, and performance tests

### Code Quality

**Code Quality:**
- Python linting with flake8, black, and isort
- Type checking with mypy
- Frontend linting and formatting
- Pre-commit hooks for automated checks

### API Documentation

**API Documentation:**
- Interactive Swagger UI and ReDoc documentation
- OpenAPI schema generation with drf-spectacular
- Comprehensive endpoint documentation

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

1. **Celery Worker Not Starting**: Check Redis connection, environment variables, and worker logs
2. **Document Processing Fails**: Verify AWS credentials, file format, disk space, and task logs
3. **Database Connection Issues**: Check database status, connection string, and permissions
4. **Authentication Problems**: Verify JWT tokens, CORS settings, and email configuration

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
