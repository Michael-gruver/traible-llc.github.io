# Traible Backend - Document Intelligence Platform

A comprehensive Django-based backend system for document intelligence, AI chat functionality, and secure user management. Built with modern Python technologies and enterprise-grade features.

## 🚀 Features

### 🎯 **Core Features**
- **Document Processing**: Upload, analyze, and process PDF documents with AI
- **AI Chat System**: Interactive chat with AI about document content using AWS Bedrock
- **User Authentication**: Secure JWT-based authentication with comprehensive user management
- **Password Recovery**: Complete password reset system with security best practices
- **File Management**: Secure file upload, validation, and storage
- **Background Tasks**: Asynchronous processing with Celery integration
- **Health Monitoring**: Comprehensive system health checks and metrics

### 🔐 **Security Features**
- **Rate Limiting**: Configurable API rate limiting (1000/hour authenticated, 100/hour anonymous)
- **Input Validation**: Comprehensive file and data validation with security scanning
- **Token Security**: Cryptographically secure token generation and management
- **Email Privacy**: Secure email handling without information disclosure
- **File Security**: Magic number validation, MIME type checking, and malware scanning
- **CORS Protection**: Secure cross-origin request handling
- **SQL Injection Protection**: Query sanitization and parameterized queries

### 🎨 **Developer Experience**
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Comprehensive Testing**: Unit tests, integration tests, and security tests
- **Error Handling**: Structured error responses with detailed logging
- **Development Tools**: Debug toolbar, Django extensions, and development utilities
- **Type Safety**: Python type hints and comprehensive validation
- **Hot Reload**: Fast development with Django's built-in server

### 🛠 **Production Features**
- **Scalability**: Horizontal scaling support with stateless design
- **Caching**: Redis integration with model-level caching
- **Database Optimization**: Strategic indexes and query optimization
- **Monitoring**: Health checks, metrics, and performance monitoring
- **Deployment**: Docker support and production-ready configuration
- **Maintenance**: Automated cleanup commands and system maintenance tools

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [API Documentation](#api-documentation)
- [Authentication System](#authentication-system)
- [Document Processing](#document-processing)
- [Chat System](#chat-system)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Contributing](#contributing)

## 🚀 Getting Started

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
├── client/                 # Frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Route components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── store/         # State management
│   │   └── test/          # Test setup
│   └── index.html         # HTML entry point
├── shared/                # Shared types and schemas
├── migrations/            # Database migrations
└── dist/                  # Build output
```

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **State Management**: Custom stores (Zustand-like)
- **Database**: PostgreSQL with Drizzle ORM
- **Testing**: Vitest, React Testing Library
- **Code Quality**: ESLint, Prettier
- **UI Components**: Radix UI primitives with custom styling

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Ensure all linting and type checks pass
4. Update documentation as needed

## License

MIT
