# Traible - Document Intelligence Platform

> **Know Your Tribe** - Transform your documents into intelligent, searchable knowledge with AI-powered chat functionality.

Traible is a comprehensive document intelligence platform that enables users to upload documents, extract insights using AI, and engage in intelligent conversations about their content. Built with modern technologies and enterprise-grade security.

## 🚀 Quick Start

This repository contains the complete Traible product across multiple branches:

- **[Backend (Django)](../../tree/traible-chat)** - API server, document processing, AI integration
- **[Frontend (React)](../../tree/traible-chat-FE)** - User interface, chat system, document management

### Choose Your Development Path

#### 🔧 Backend Development
```bash
git checkout traible-chat
# Follow backend setup instructions in that branch's README
```

#### 🎨 Frontend Development  
```bash
git checkout traible-chat-FE
# Follow frontend setup instructions in that branch's README
```

#### 🚀 Full Stack Development
```bash
# Terminal 1 - Backend
git checkout traible-chat
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

# Terminal 2 - Frontend  
git checkout traible-chat-FE
npm install
npm run dev
```

## 📋 Product Overview

### 🎯 **Core Features**
- **Document Upload & Processing**: Secure PDF, DOC, TXT file handling with AI extraction
- **Intelligent Chat**: AI-powered conversations about document content using AWS Bedrock
- **User Management**: Complete authentication system with secure password recovery
- **Real-time Interface**: Modern React frontend with responsive design
- **Enterprise Security**: Rate limiting, input validation, and comprehensive security measures

### 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Django Backend │    │   AWS Services  │
│                 │    │                  │    │                 │
│ • Modern UI     │◄──►│ • REST API       │◄──►│ • Bedrock (AI)  │
│ • Chat Interface│    │ • Document Proc. │    │ • Textract      │
│ • Auth System   │    │ • User Auth      │    │ • S3 Storage    │
│ • File Upload   │    │ • Security       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────────────┐
                    │     Infrastructure      │
                    │                         │
                    │ • PostgreSQL Database   │
                    │ • Redis Cache          │
                    │ • Celery Tasks         │
                    │ • Docker Support       │
                    └─────────────────────────┘
```

### 🛠️ **Technology Stack**

#### Frontend (`traible-chat-FE` branch)
- **React 18** with TypeScript for type-safe development
- **Vite** for fast development and building
- **Tailwind CSS** with custom design system
- **Radix UI** components with accessibility support
- **Zustand** for state management
- **React Query** for API data fetching

#### Backend (`traible-chat` branch)
- **Django 4.2+** with Django REST Framework
- **PostgreSQL** for robust data storage
- **Redis** for caching and session management
- **Celery** for background task processing
- **AWS Bedrock** for AI model integration
- **JWT Authentication** for secure API access

## 📚 Branch Documentation

### 🔧 Backend Branch (`traible-chat`)
Complete Django-based backend system with:
- **API Documentation**: Interactive Swagger UI at `/api/docs/`
- **Authentication System**: JWT-based with password recovery
- **Document Processing**: AI-powered document analysis
- **Chat System**: Intelligent conversations with AI
- **Security Features**: Rate limiting, input validation, file security
- **Health Monitoring**: Comprehensive system health checks
- **Production Ready**: Docker support, monitoring, deployment guides

**[📖 View Backend Documentation](../../tree/traible-chat)**

### 🎨 Frontend Branch (`traible-chat-FE`)
Modern React application featuring:
- **Document Intelligence**: Upload and analyze documents with AI
- **Interactive Chat**: Real-time chat interface with AI responses
- **User Authentication**: Secure login, registration, password recovery
- **Modern UI/UX**: Responsive design with dark/light themes
- **Password Security**: Strength indicators and secure password generation
- **Accessibility**: Full keyboard navigation and screen reader support

**[📖 View Frontend Documentation](../../tree/traible-chat-FE)**

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18.18+ (for frontend)
- **Python** 3.9+ (for backend)
- **PostgreSQL** 12+ (production) or SQLite (development)
- **Redis** 6.0+ (for caching)
- **AWS Account** (for AI features)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd traible-llc.github.io
   ```

2. **Choose your development focus**
   ```bash
   # For backend development
   git checkout traible-chat
   
   # For frontend development
   git checkout traible-chat-FE
   ```

3. **Follow branch-specific setup instructions**
   - Each branch has detailed setup instructions in its README
   - Backend: Django setup, database configuration, AWS setup
   - Frontend: Node.js setup, environment configuration

### Development Workflow

1. **Backend Development**: Work in `traible-chat` branch
2. **Frontend Development**: Work in `traible-chat-FE` branch  
3. **Integration Testing**: Test both systems together
4. **Deployment**: Use production guides in respective branches

## 🔐 Security & Compliance

- **Data Protection**: Secure file handling and storage
- **Authentication**: JWT-based with secure password policies
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive security validation
- **Encryption**: HTTPS-ready with secure communication
- **Privacy**: No data disclosure in error messages

## 📊 Features Comparison

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| User Authentication | ✅ | ✅ | Complete |
| Password Recovery | ✅ | ✅ | Complete |
| Document Upload | ✅ | ✅ | Complete |
| AI Chat System | ✅ | ✅ | Complete |
| Real-time Updates | ✅ | ✅ | Complete |
| Health Monitoring | - | ✅ | Complete |
| API Documentation | - | ✅ | Complete |
| Responsive Design | ✅ | - | Complete |
| Dark/Light Theme | ✅ | - | Complete |
| Accessibility | ✅ | - | Complete |

## 🚀 Deployment

### Production Deployment Options

#### Option 1: Separate Deployments
- **Frontend**: Deploy React app to Vercel, Netlify, or CDN
- **Backend**: Deploy Django to AWS, GCP, or dedicated server

#### Option 2: Containerized Deployment
- **Docker**: Both branches include Docker configuration
- **Kubernetes**: Production-ready with health checks
- **Docker Compose**: Local development and testing

#### Option 3: Full Stack Deployment
- **Single Server**: Deploy both frontend and backend together
- **Load Balancer**: Scale horizontally with multiple instances

### Environment Configuration

Each branch includes comprehensive environment setup:
- **Development**: Local development with hot reload
- **Staging**: Pre-production testing environment  
- **Production**: Optimized for performance and security

## 🤝 Contributing

### Development Branches
- **`traible-chat`**: Backend Django development
- **`traible-chat-FE`**: Frontend React development
- **`main`**: Product overview and documentation (this branch)

### Contribution Workflow
1. **Choose your area**: Backend or Frontend development
2. **Switch to appropriate branch**: `traible-chat` or `traible-chat-FE`
3. **Create feature branch**: From the development branch
4. **Follow branch guidelines**: Each branch has specific coding standards
5. **Submit pull request**: To the appropriate development branch

### Code Standards
- **Backend**: Python PEP 8, Django best practices, comprehensive testing
- **Frontend**: TypeScript strict mode, React best practices, accessibility standards
- **Documentation**: Update README and API docs with changes
- **Security**: Follow security best practices for all changes

## 📞 Support

### Documentation
- **[Backend Documentation](../../tree/traible-chat)**: Complete Django backend guide
- **[Frontend Documentation](../../tree/traible-chat-FE)**: Complete React frontend guide
- **API Documentation**: Interactive docs at `/api/docs/` when backend is running

### Getting Help
1. **Check branch-specific documentation** for detailed setup and troubleshooting
2. **Review API documentation** for backend integration questions
3. **Search existing issues** in the repository
4. **Create new issue** with detailed information and branch context

### Development Support
- **Backend Issues**: Use `traible-chat` branch context
- **Frontend Issues**: Use `traible-chat-FE` branch context
- **Integration Issues**: Mention both branches and setup details

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🎯 Next Steps

1. **Choose your development path** (Backend or Frontend)
2. **Switch to the appropriate branch** (`traible-chat` or `traible-chat-FE`)
3. **Follow the detailed setup instructions** in that branch's README
4. **Start building** amazing document intelligence features!

**Traible** - Transforming documents into intelligent, searchable knowledge. Built with ❤️ for developers and users who value security, performance, and great user experience.
