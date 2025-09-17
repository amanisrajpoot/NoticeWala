# NoticeWala Setup Guide

## Prerequisites

Before setting up NoticeWala, ensure you have the following installed:

### System Requirements
- **Python 3.9+** (Backend)
- **Node.js 16+** (Mobile app)
- **PostgreSQL 13+** (Database)
- **Redis 6+** (Cache and queues)
- **Elasticsearch 8+** (Search)
- **Docker** (Optional, for containerized setup)

### Development Tools
- **Git** (Version control)
- **VS Code** or **PyCharm** (Code editor)
- **Android Studio** (For Android development)
- **Xcode** (For iOS development, macOS only)

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/NoticeWala.git
cd NoticeWala
```

### 2. Start Services
```bash
cd infrastructure
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Elasticsearch search engine
- Backend API server
- Celery workers
- Flower monitoring dashboard

### 3. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower**: http://localhost:5555

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Load sample data
docker-compose exec backend python scripts/load_sample_data.py
```

## Manual Setup

### Backend Setup

#### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Up Database
```bash
# Install PostgreSQL and create database
createdb noticewala

# Run migrations
alembic upgrade head
```

#### 4. Configure Environment
```bash
cp env.example .env
# Edit .env with your configuration
```

#### 5. Start Services
```bash
# Start Redis
redis-server

# Start Elasticsearch
elasticsearch

# Start backend
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.core.celery worker --loglevel=info
```

### Mobile App Setup

#### 1. Install Dependencies
```bash
cd mobile
npm install
```

#### 2. iOS Setup (macOS only)
```bash
cd ios
pod install
cd ..
```

#### 3. Configure Environment
```bash
# Create .env file
echo "API_BASE_URL=http://localhost:8000/api/v1" > .env
```

#### 4. Start Metro Bundler
```bash
npx react-native start
```

#### 5. Run on Device/Simulator
```bash
# Android
npx react-native run-android

# iOS
npx react-native run-ios
```

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/noticewala

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (for AI extraction)
OPENAI_API_KEY=your-openai-api-key

# Firebase (for push notifications)
FCM_SERVER_KEY=your-fcm-server-key
FCM_PROJECT_ID=your-fcm-project-id

# Security
SECRET_KEY=your-secret-key-here

# Debug mode
DEBUG=True
```

### Mobile App Configuration

Edit `mobile/.env`:

```env
# API Configuration
API_BASE_URL=http://localhost:8000/api/v1

# Firebase Configuration (for push notifications)
FCM_SENDER_ID=your-sender-id
FCM_PROJECT_ID=your-project-id

# App Configuration
APP_NAME=NoticeWala
APP_VERSION=1.0.0
```

## Database Setup

### 1. Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE noticewala;
CREATE USER noticewala WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE noticewala TO noticewala;
```

### 2. Run Migrations
```bash
cd backend
alembic upgrade head
```

### 3. Load Sample Data
```bash
python scripts/load_sample_data.py
```

## Development Workflow

### 1. Backend Development
```bash
# Start development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run linting
black .
isort .
flake8 .

# Type checking
mypy .
```

### 2. Mobile Development
```bash
# Start Metro bundler
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run tests
npm test

# Linting
npm run lint
```

### 3. Database Changes
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Mobile Tests
```bash
cd mobile
npm test
```

### Integration Tests
```bash
# Run with Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Monitoring and Debugging

### 1. Application Logs
```bash
# Backend logs
docker-compose logs -f backend

# Celery logs
docker-compose logs -f celery-worker
```

### 2. Database Monitoring
```bash
# Connect to database
docker-compose exec postgres psql -U noticewala -d noticewala

# Monitor queries
SELECT * FROM pg_stat_activity;
```

### 3. Performance Monitoring
- **Flower**: http://localhost:5555 (Celery tasks)
- **Elasticsearch**: http://localhost:9200/_cluster/health
- **Redis**: `redis-cli monitor`

## Production Deployment

### 1. Environment Configuration
```bash
# Set production environment variables
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@prod-db:5432/noticewala
```

### 2. Build and Deploy
```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### 3. SSL/HTTPS Setup
```bash
# Use nginx reverse proxy with SSL
# Configure Let's Encrypt certificates
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if PostgreSQL is running
pg_ctl status

# Check connection
psql -h localhost -U noticewala -d noticewala
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# Should return "PONG"
```

#### 3. Mobile App Build Issues
```bash
# Clean and rebuild
cd mobile
npm run clean
npm install
cd ios && pod install && cd ..
npm run android
```

#### 4. Celery Worker Issues
```bash
# Check Celery status
celery -A app.core.celery inspect active

# Restart workers
docker-compose restart celery-worker
```

### Getting Help

1. **Check Logs**: Always check application logs first
2. **Documentation**: Refer to API documentation
3. **GitHub Issues**: Search existing issues or create new ones
4. **Community**: Join our Discord/Slack community

## Next Steps

After successful setup:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the Mobile App**: Install on your device
3. **Add Sources**: Configure web sources to crawl
4. **Set Up Notifications**: Configure push notifications
5. **Monitor Performance**: Use Flower and logs for monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
