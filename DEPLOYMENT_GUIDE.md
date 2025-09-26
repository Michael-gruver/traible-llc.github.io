# Traible Backend Deployment Guide

This guide provides comprehensive instructions for deploying the Traible backend application in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Redis Configuration](#redis-configuration)
5. [AWS Configuration](#aws-configuration)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18.18 or higher (for frontend)
- **PostgreSQL**: 12 or higher (production)
- **Redis**: 6.0 or higher
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 20GB free space

### Required Services

- **AWS Account** with Bedrock access
- **Email Service** (SMTP configuration)
- **File Storage** (local or cloud)

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd traible-llc.github.io
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/traible_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS Configuration
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

# Frontend URL
FRONTEND_URL=https://your-frontend-domain.com

# File Storage
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files
```

## Database Configuration

### PostgreSQL Setup

1. **Install PostgreSQL**:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create Database**:
```sql
CREATE DATABASE traible_db;
CREATE USER traible_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE traible_db TO traible_user;
```

3. **Run Migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create Superuser**:
```bash
python manage.py createsuperuser
```

## Redis Configuration

### Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

### Configure Redis

Edit `/etc/redis/redis.conf`:

```conf
# Set memory limit
maxmemory 2gb
maxmemory-policy allkeys-lru

# Enable persistence
save 900 1
save 300 10
save 60 10000

# Set password (optional but recommended)
requirepass your_redis_password
```

### Start Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## AWS Configuration

### 1. Create IAM User

Create an IAM user with the following policies:
- `AmazonBedrockFullAccess`
- `AmazonTextractFullAccess`

### 2. Configure AWS CLI

```bash
aws configure
```

### 3. Test Bedrock Access

```bash
aws bedrock list-foundation-models --region us-east-1
```

## Production Deployment

### 1. Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary
```

### 2. Configure Gunicorn

Create `gunicorn.conf.py`:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 3. Create Systemd Service

Create `/etc/systemd/system/traible.service`:

```ini
[Unit]
Description=Traible Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/traible-llc.github.io
Environment=PATH=/path/to/traible-llc.github.io/venv/bin
ExecStart=/path/to/traible-llc.github.io/venv/bin/gunicorn --config gunicorn.conf.py docbot.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl start traible
sudo systemctl enable traible
```

### 5. Configure Nginx

Create `/etc/nginx/sites-available/traible`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/traible-llc.github.io/static/;
    }

    location /media/ {
        alias /path/to/traible-llc.github.io/media/;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/traible /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create media directory
RUN mkdir -p media static

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "docbot.wsgi:application"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://traible_user:password@db:5432/traible_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./static:/app/static

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=traible_db
      - POSTGRES_USER=traible_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass password

  celery:
    build: .
    command: celery -A docbot worker -l info
    environment:
      - DATABASE_URL=postgresql://traible_user:password@db:5432/traible_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### 3. Deploy with Docker

```bash
docker-compose up -d
```

## Monitoring and Logging

### 1. Configure Logging

Update `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/traible/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Health Monitoring

The application includes health check endpoints:

- `/health/` - Basic health check
- `/health/detailed/` - Detailed system metrics
- `/metrics/` - System performance metrics
- `/readiness/` - Kubernetes readiness probe
- `/liveness/` - Kubernetes liveness probe

### 3. Set up Monitoring

Use tools like:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log aggregation
- **Sentry** for error tracking

## Security Considerations

### 1. Environment Variables

- Never commit `.env` files to version control
- Use strong, unique passwords
- Rotate secrets regularly

### 2. Database Security

- Use strong database passwords
- Enable SSL connections
- Restrict database access by IP

### 3. API Security

- Enable rate limiting
- Use HTTPS in production
- Implement proper CORS policies
- Validate all input data

### 4. File Upload Security

- Validate file types and sizes
- Scan uploaded files for malware
- Store files outside web root
- Use secure file permissions

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Verify database server is running
   - Check network connectivity

2. **Redis Connection Errors**
   - Verify Redis server is running
   - Check Redis configuration
   - Test connection with `redis-cli`

3. **AWS Bedrock Errors**
   - Verify AWS credentials
   - Check IAM permissions
   - Verify region configuration

4. **File Upload Issues**
   - Check file permissions
   - Verify disk space
   - Check file size limits

### Log Analysis

```bash
# View Django logs
tail -f /var/log/traible/django.log

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# View system logs
journalctl -u traible -f
```

### Performance Optimization

1. **Database Optimization**
   - Add database indexes
   - Use connection pooling
   - Optimize queries

2. **Caching**
   - Enable Redis caching
   - Use CDN for static files
   - Implement query caching

3. **File Storage**
   - Use cloud storage (S3)
   - Implement file compression
   - Clean up old files regularly

## Maintenance

### Regular Tasks

1. **Database Maintenance**
   ```bash
   python manage.py cleanup_documents --days=30
   ```

2. **Log Rotation**
   - Configure logrotate
   - Monitor disk space
   - Archive old logs

3. **Security Updates**
   - Update dependencies regularly
   - Monitor security advisories
   - Apply patches promptly

### Backup Strategy

1. **Database Backups**
   ```bash
   pg_dump traible_db > backup_$(date +%Y%m%d).sql
   ```

2. **File Backups**
   ```bash
   tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
   ```

3. **Automated Backups**
   - Set up cron jobs
   - Use cloud backup services
   - Test restore procedures

This deployment guide provides a comprehensive foundation for deploying the Traible backend in production environments. Adjust configurations based on your specific requirements and infrastructure.
