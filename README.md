# Traible - Know Your Tribe

A comprehensive document intelligence platform built with modern React, TypeScript, and Django. Traible enables users to upload documents, chat with AI about their content, and manage conversations with advanced security features.

## Features

### **Core Features**
- **Document Intelligence**: Upload and analyze PDF documents with AI
- **Interactive Chat**: Chat with AI about your document content
- **Conversation Management**: Organize and manage chat conversations
- **User Authentication**: Secure login and registration system
- **Password Recovery**: Comprehensive password reset functionality
- **Real-time Updates**: Live chat interface with message streaming

### **Security Features**
- **Rate Limiting**: Prevents brute force attacks
- **Token Expiration**: Secure session and reset token management
- **Password Strength Validation**: Enforces strong password requirements
- **Email Privacy**: Secure email handling without revealing user existence
- **Single Use Tokens**: Tokens invalidated after use

### **User Experience**
- **Modern UI**: Clean, responsive design with animations
- **Dark/Light Theme**: Customizable theme support
- **Password Strength Indicator**: Real-time password strength feedback
- **Password Generator**: Built-in secure password generator
- **Progressive Enhancement**: Works without JavaScript for basic functionality
- **Accessibility**: Full keyboard navigation and screen reader support
- **Offline Support**: Offline detection and graceful handling

### **Developer Experience**
- **TypeScript**: Full type safety across the application
- **Reusable Components**: Modular, composable UI components
- **Custom Hooks**: Clean separation of logic and UI
- **Comprehensive Testing**: Unit and integration tests with Vitest
- **Code Quality**: ESLint, Prettier, and automated formatting
- **Hot Reload**: Fast development with Vite

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Features Documentation](#features-documentation)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

- **Node.js** 18.18 or higher
- **Python** 3.8 or higher
- **PostgreSQL** (for production) or SQLite (for development)
- **npm** or **yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd traible-llc.github.io
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Update .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Frontend database (Drizzle)
   npm run drizzle:generate
   npm run drizzle:push
   
   # Backend database (Django)
   python manage.py migrate
   ```

### Development

#### Frontend Development
```bash
# Start development server
npm run dev

# Type checking
npm run typecheck

# Linting and formatting
npm run lint
npm run lint:fix
npm run format
npm run format:check

# Testing
npm run test
npm run test:ui
npm run test:coverage

# Database management
npm run drizzle:studio
```

#### Backend Development
```bash
# Start Django development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Build for Production

```bash
# Build frontend
npm run build
npm run preview

# Prepare backend for production
python manage.py collectstatic --noinput
python manage.py migrate
```

## Project Structure

```
traible-llc.github.io/
├── client/                     # Frontend React application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── auth/          # Authentication components
│   │   │   ├── chat/          # Chat interface components
│   │   │   ├── common/        # Shared components
│   │   │   ├── layout/        # Layout components
│   │   │   ├── pdf/           # PDF handling components
│   │   │   └── ui/            # UI primitives (Radix UI based)
│   │   ├── pages/             # Route components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility libraries
│   │   ├── store/             # State management (Zustand)
│   │   └── test/              # Test setup and utilities
│   ├── assets/                # Static assets
│   └── index.html             # HTML entry point
├── accounts/                   # Django user management
├── chatbot/                   # Django chat and document processing
│   ├── management/            # Django management commands
│   ├── migrations/            # Database migrations
│   ├── services/              # Business logic services
│   └── tests/                 # Backend tests
├── docbot/                    # Django project configuration
├── shared/                    # Shared types and schemas
├── migrations/                # Database migrations
└── dist/                      # Frontend build output
```

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and building
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Radix UI primitives with custom styling
- **State Management**: Zustand for global state
- **Routing**: React Router DOM
- **HTTP Client**: Axios with React Query for data fetching
- **Forms**: React Hook Form with Zod validation
- **Testing**: Vitest with React Testing Library
- **Animation**: Framer Motion
- **Icons**: Lucide React and React Icons

### Backend
- **Framework**: Django with Django REST Framework
- **Database**: PostgreSQL with Django ORM
- **Authentication**: Django's built-in auth with custom extensions
- **Task Queue**: Celery for background tasks
- **AI Integration**: AWS Bedrock for document processing
- **File Storage**: Django file handling with cloud storage support

### Database
- **Frontend**: Drizzle ORM with PostgreSQL/SQLite
- **Backend**: Django ORM with PostgreSQL

### Development Tools
- **Code Quality**: ESLint, Prettier
- **Type Checking**: TypeScript strict mode
- **Testing**: Vitest, React Testing Library, Django Test Framework
- **Package Management**: npm, pip

## Features Documentation

### Authentication System

The application includes a comprehensive authentication system with:

#### Login & Registration
- Secure user registration with email verification
- Login with email and password
- Form validation with real-time feedback
- Remember me functionality

#### Password Recovery System
A complete password recovery system with advanced security features:

**Security Features:**
- Rate limiting (3 requests/email/hour, 10/IP/hour)
- Token expiration (1 hour limit)
- Single-use tokens (invalidated after use)
- Secure token generation (cryptographically secure)
- Email privacy (doesn't reveal if email exists)
- Password strength validation

**User Flow:**
1. User clicks "Forgot Password?" on login page
2. Enters email on `/password-reset-request`
3. Receives secure reset email with token
4. Clicks link to `/password-reset-confirm`
5. Sets new password with strength indicator
6. Redirected to login with success message

**Components:**
- `PasswordResetRequest` - Email input and validation
- `PasswordResetConfirm` - New password setting
- `PasswordStrengthInput` - Enhanced password input with strength indicator
- `usePasswordRecovery` - Custom hook for password recovery logic

### Chat System

Interactive document chat functionality:

#### Features
- **Document Upload**: PDF upload and processing
- **AI Chat**: Chat with AI about document content
- **Conversation Management**: Organize multiple conversations
- **Message History**: Persistent message storage
- **Real-time Updates**: Live message streaming

#### Components
- `ChatInterface` - Main chat input and controls
- `MessageList` - Display chat messages
- `ConversationList` - Manage multiple conversations
- `DocumentList` - View uploaded documents
- `PdfUpload` - Document upload functionality

### UI Components

Built on Radix UI primitives with custom styling:

#### Core Components
- **Forms**: Input, Textarea, Select, Checkbox, Radio Group
- **Navigation**: Tabs, Navigation Menu, Breadcrumb
- **Feedback**: Toast, Alert, Progress, Loading Spinner
- **Layout**: Card, Sheet, Dialog, Popover, Accordion
- **Data Display**: Table, Avatar, Badge, Separator

#### Custom Components
- **TraibleLoader**: Branded loading component with custom messages
- **OfflineAlert**: Network status detection and user notification
- **PasswordStrengthInput**: Enhanced password input with validation
- **ThemeProvider**: Dark/light theme management

## API Documentation

### Authentication Endpoints

#### Password Reset Request
```http
POST /api/auth/password-reset-request/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "If an account with this email exists, you will receive reset instructions."
}
```

#### Password Reset Validation
```http
POST /api/auth/password-reset-validate/
Content-Type: application/json

{
  "token": "abc123...",
  "uid": "123"
}
```

**Response (200 OK - Valid):**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

#### Password Reset Confirmation
```http
POST /api/auth/password-reset-confirm/
Content-Type: application/json

{
  "token": "abc123...",
  "uid": "123",
  "password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password has been reset successfully"
}
```

### Chat Endpoints

#### Document Upload
```http
POST /api/documents/upload/
Content-Type: multipart/form-data

{
  "file": <PDF file>,
  "title": "Document Title"
}
```

#### Chat Message
```http
POST /api/chat/message/
Content-Type: application/json

{
  "message": "What is this document about?",
  "document_id": "123",
  "conversation_id": "456"
}
```

### Rate Limiting

All API endpoints implement rate limiting:
- **Password Reset**: 3 requests per email per hour, 10 per IP per hour
- **Chat Messages**: 100 requests per user per hour
- **Document Upload**: 10 uploads per user per hour

## Security

### Password Requirements

**Default Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- Maximum 128 characters

**Forbidden Patterns:**
- More than 2 consecutive identical characters
- Sequential numbers (123, 234, etc.)
- Sequential letters (abc, bcd, etc.)

**Strength Levels:**
- **Weak** (Red): Basic requirements not met
- **Medium** (Yellow): Basic requirements met
- **Strong** (Blue): Multiple character types, good length
- **Very Strong** (Green): Excellent entropy and complexity

### Token Security

- **Generation**: Cryptographically secure random strings
- **Storage**: Secure cache with expiration
- **Transmission**: HTTPS only
- **Validation**: Server-side validation required

### Monitoring

- **Logging**: All authentication attempts logged
- **Alerts**: Suspicious patterns flagged
- **Metrics**: Success/failure rates tracked
- **Rate Limiting**: Automatic protection against brute force

## Testing

### Frontend Testing

```bash
# Run all tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test suites
npm run test -- --grep "password recovery"
npm run test -- --grep "chat interface"
npm run test -- --grep "authentication"
```

### Backend Testing

```bash
# Run Django tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test chatbot

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing Checklist

#### Authentication
- [ ] User registration with valid/invalid data
- [ ] Login with correct/incorrect credentials
- [ ] Password reset flow end-to-end
- [ ] Rate limiting enforcement
- [ ] Token expiration handling

#### Chat System
- [ ] Document upload (PDF)
- [ ] Chat message sending/receiving
- [ ] Conversation creation/management
- [ ] Real-time message updates
- [ ] Error handling for failed uploads

#### UI/UX
- [ ] Responsive design on mobile/desktop
- [ ] Dark/light theme switching
- [ ] Accessibility with keyboard navigation
- [ ] Loading states and error messages
- [ ] Offline functionality

## Deployment

### Environment Variables

#### Frontend
```bash
VITE_API_URL=https://api.traible.com
VITE_APP_NAME=Traible
```

#### Backend
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/traible

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=traible.com,www.traible.com

# Frontend URL
FRONTEND_URL=https://traible.com

# AWS Bedrock (for AI features)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

### Production Checklist

#### Security
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Rate limiting configured at API gateway level
- [ ] Environment variables secured
- [ ] Database connections encrypted
- [ ] CORS properly configured
- [ ] CSP headers implemented

#### Performance
- [ ] Frontend assets minified and compressed
- [ ] CDN configured for static assets
- [ ] Database queries optimized
- [ ] Caching strategy implemented
- [ ] Load balancing configured

#### Monitoring
- [ ] Error tracking (Sentry, etc.)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Log aggregation
- [ ] Security monitoring

#### Backup & Recovery
- [ ] Database backups automated
- [ ] File storage backups
- [ ] Disaster recovery plan
- [ ] Rollback procedures documented

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests and linting**
   ```bash
   npm run test
   npm run lint
   npm run typecheck
   ```
5. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Code Style Guidelines

- **TypeScript**: Use strict mode, prefer interfaces over types
- **React**: Use functional components with hooks
- **CSS**: Use Tailwind classes, avoid custom CSS when possible
- **Naming**: Use camelCase for variables, PascalCase for components
- **Comments**: Write JSDoc comments for public APIs
- **Testing**: Write tests for new features and bug fixes

### Commit Message Format

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support & Troubleshooting

### Common Issues

#### "Invalid or expired token"
- Token may have expired (1 hour limit)
- Token may have been used already
- Check URL parameters are correct

#### "Rate limit exceeded"
- Wait before making another request
- Check if multiple users are using same IP

#### "Email not received"
- Check spam folder
- Verify email address is correct
- Check email service configuration

#### "Password doesn't meet requirements"
- Use password strength indicator
- Try password generator
- Check requirements documentation

### Debug Mode

Enable debug logging in development:
```bash
# Frontend
VITE_DEBUG=true

# Backend
DEBUG=True
DEBUG_PASSWORD_RECOVERY=true
```

### Getting Help

1. Check this documentation
2. Review API specifications
3. Check error logs and console
4. Search existing issues
5. Create a new issue with detailed information

---

**Traible** - Empowering document intelligence with modern technology. Built with ❤️ for seamless user experiences and robust security.
