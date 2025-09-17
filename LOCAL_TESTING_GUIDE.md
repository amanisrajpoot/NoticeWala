# NoticeWala Local Testing Guide

## 🚀 Quick Start - Local Testing

This guide will help you test the complete NoticeWala system locally before moving to production.

## 📋 Prerequisites

### Required Software
- **Docker & Docker Compose**: For running the complete system
- **Node.js (v18+)**: For React Native mobile app testing
- **Python (v3.11+)**: For backend testing
- **Git**: For version control

### Optional Software
- **Postman**: For API testing
- **Android Studio**: For Android app testing
- **Xcode**: For iOS app testing (macOS only)

## 🏗️ Step 1: Environment Setup

### 1.1 Clone and Navigate
```bash
# Already in the project directory
cd C:\Users\USER\Documents\gen\projects\NoticeWala
```

### 1.2 Create Environment Files
```bash
# Copy environment template
cp backend/env.example backend/.env
```

### 1.3 Edit Environment Variables
Edit `backend/.env` with your local settings:
```env
# Database
DATABASE_URL=postgresql://noticewala:password@localhost:5432/noticewala

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Security
SECRET_KEY=your-super-secret-key-for-local-testing

# OpenAI (optional for testing)
OPENAI_API_KEY=your-openai-api-key

# FCM (optional for testing)
FCM_SERVER_KEY=your-fcm-server-key

# Debug
DEBUG=True
```

## 🐳 Step 2: Docker Setup and Testing

### 2.1 Start Infrastructure Services
```bash
# Start database, Redis, and Elasticsearch
cd infrastructure
docker-compose up -d postgres redis elasticsearch
```

### 2.2 Verify Services
```bash
# Check if services are running
docker-compose ps

# Test database connection
docker-compose exec postgres psql -U noticewala -d noticewala -c "SELECT version();"

# Test Redis connection
docker-compose exec redis redis-cli ping

# Test Elasticsearch
curl http://localhost:9200/_cluster/health
```

## 🔧 Step 3: Backend Testing

### 3.1 Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3.2 Run Database Migrations
```bash
# Install Alembic if not already installed
pip install alembic

# Run migrations
alembic upgrade head
```

### 3.3 Start Backend Server
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.4 Test Backend API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
# Open browser: http://localhost:8000/docs
```

### 3.5 Test API Endpoints
```bash
# Test announcements endpoint
curl http://localhost:8000/api/v1/announcements

# Test authentication (register user)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'

# Test authentication (login)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

## 📱 Step 4: Mobile App Testing

### 4.1 Install Mobile Dependencies
```bash
cd mobile
npm install
```

### 4.2 Configure Mobile App
Update `mobile/src/services/apiService.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000'; // For local testing
// or use your computer's IP address for device testing:
// const API_BASE_URL = 'http://192.168.1.100:8000';
```

### 4.3 Start Metro Bundler
```bash
# Start React Native Metro bundler
npx react-native start
```

### 4.4 Run Mobile App
```bash
# For Android (requires Android Studio setup)
npx react-native run-android

# For iOS (macOS only, requires Xcode setup)
npx react-native run-ios

# For web testing (if configured)
npx react-native run-web
```

## 🔄 Step 5: Complete System Testing

### 5.1 Start All Services with Docker
```bash
# Start complete system
cd infrastructure
docker-compose up -d

# Check all services
docker-compose ps
```

### 5.2 Test System Integration
```bash
# Test backend health
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/health/database

# Test Redis connection
curl http://localhost:8000/health/redis

# Test Elasticsearch connection
curl http://localhost:8000/health/elasticsearch
```

### 5.3 Monitor Services
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# Monitor Celery tasks
# Open browser: http://localhost:5555
```

## 🧪 Step 6: Functional Testing

### 6.1 Test User Registration and Login
```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepassword123",
    "full_name": "Test User"
  }'

# Login with the user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepassword123"
  }'
```

### 6.2 Test Announcements
```bash
# Get announcements (should return empty array initially)
curl http://localhost:8000/api/v1/announcements

# Create a test announcement (requires authentication)
# First get the token from login response, then:
curl -X POST http://localhost:8000/api/v1/announcements \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Test Exam Announcement",
    "description": "This is a test announcement for local testing",
    "source_url": "https://example.com/test",
    "published_date": "2024-09-17T10:00:00Z",
    "exam_date": "2024-12-15T09:00:00Z"
  }'
```

### 6.3 Test Search Functionality
```bash
# Test search
curl "http://localhost:8000/api/v1/announcements/search?q=exam"

# Test filtering
curl "http://localhost:8000/api/v1/announcements?category=entrance&limit=10"
```

### 6.4 Test Subscriptions
```bash
# Create a subscription
curl -X POST http://localhost:8000/api/v1/subscriptions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Test Subscription",
    "keywords": ["exam", "university"],
    "categories": ["entrance"],
    "notification_enabled": true
  }'
```

## 🕷️ Step 7: Crawler Testing

### 7.1 Test Base Crawler
```bash
# Run crawler tests
cd backend
python -c "
from app.crawlers.base_crawler import BaseCrawler
print('Base crawler import successful')
"
```

### 7.2 Test Sample Data
```bash
# Load sample data
cd backend
python -c "
import json
from app.models.announcement import Announcement
from app.core.database import SessionLocal

# Load sample sources
with open('../data/sample_sources.json', 'r') as f:
    sources = json.load(f)
    print(f'Loaded {len(sources)} sample sources')
"
```

## 📊 Step 8: Performance Testing

### 8.1 Run Basic Performance Tests
```bash
# Install k6 if not already installed
# Windows: Download from https://k6.io/docs/getting-started/installation/

# Run performance tests
cd scripts
chmod +x performance-test.sh
./performance-test.sh
```

### 8.2 Monitor System Resources
```bash
# Monitor Docker resources
docker stats

# Monitor database performance
docker-compose exec postgres psql -U noticewala -d noticewala -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;
"
```

## 🐛 Step 9: Debugging and Troubleshooting

### 9.1 Common Issues and Solutions

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose exec postgres pg_isready -U noticewala

# Reset database if needed
docker-compose down -v
docker-compose up -d postgres
```

#### Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

#### Backend API Issues
```bash
# Check backend logs
docker-compose logs backend

# Restart backend service
docker-compose restart backend
```

#### Mobile App Issues
```bash
# Clear Metro cache
npx react-native start --reset-cache

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### 9.2 Log Analysis
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs celery-worker
docker-compose logs postgres
```

## ✅ Step 10: Validation Checklist

### 10.1 Backend Validation
- [ ] FastAPI server starts successfully
- [ ] Database migrations run without errors
- [ ] All API endpoints respond correctly
- [ ] Authentication works (register/login)
- [ ] CRUD operations work for all entities
- [ ] Search functionality works
- [ ] Celery workers process tasks

### 10.2 Mobile App Validation
- [ ] React Native app builds successfully
- [ ] App connects to backend API
- [ ] Authentication flow works
- [ ] All screens load correctly
- [ ] Navigation works between screens
- [ ] Data displays correctly
- [ ] Offline functionality works

### 10.3 Integration Validation
- [ ] Backend and database communicate
- [ ] Redis caching works
- [ ] Elasticsearch indexing works
- [ ] Background tasks execute
- [ ] Push notifications work (if configured)
- [ ] File uploads work (if implemented)

## 🚀 Step 11: Production Readiness Check

### 11.1 Security Checklist
- [ ] Environment variables are properly configured
- [ ] No hardcoded secrets in code
- [ ] Database connections use proper credentials
- [ ] API endpoints require authentication where needed
- [ ] CORS is properly configured

### 11.2 Performance Checklist
- [ ] API response times are acceptable (< 500ms)
- [ ] Database queries are optimized
- [ ] Caching is working effectively
- [ ] Background tasks process efficiently
- [ ] Memory usage is within acceptable limits

### 11.3 Monitoring Checklist
- [ ] Health check endpoints work
- [ ] Logs are properly structured
- [ ] Error handling is comprehensive
- [ ] Metrics are being collected
- [ ] Alerts are configured (for production)

## 📝 Testing Results Template

Create a file `LOCAL_TEST_RESULTS.md` to document your testing:

```markdown
# Local Testing Results

## Test Date: [DATE]
## Tester: [YOUR_NAME]
## Environment: Local Docker Setup

## ✅ Passed Tests
- [ ] Backend API endpoints
- [ ] Database connectivity
- [ ] Redis caching
- [ ] Mobile app functionality
- [ ] Authentication flow
- [ ] Search functionality
- [ ] Background tasks

## ❌ Failed Tests
- [ ] [Describe any failures]

## 🔧 Issues Found
- [ ] [List any issues]

## 📊 Performance Metrics
- API Response Time: [X]ms
- Database Query Time: [X]ms
- Memory Usage: [X]MB
- CPU Usage: [X]%

## 🚀 Ready for Production?
- [ ] Yes, all tests passed
- [ ] No, issues need to be resolved
```

## 🎯 Next Steps

After successful local testing:

1. **Fix any issues** found during testing
2. **Document test results** in the template above
3. **Prepare for production deployment** using the deployment scripts
4. **Set up monitoring** for production environment
5. **Plan user acceptance testing** with real users

## 📞 Support

If you encounter any issues during local testing:

1. Check the logs: `docker-compose logs [service-name]`
2. Verify environment variables are set correctly
3. Ensure all services are running: `docker-compose ps`
4. Check the troubleshooting section above
5. Review the API documentation at `http://localhost:8000/docs`

---

**Happy Testing! 🚀**

Remember: Local testing is crucial before moving to production. Take your time to thoroughly test all functionality and document any issues you find.
