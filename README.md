# NoticeWala - Exam Notification Aggregator

A comprehensive system that automatically discovers, extracts, and delivers exam notifications from various web sources to users via a React Native mobile application.

## 🎯 Project Overview

NoticeWala solves the critical problem of students missing important exam deadlines by providing:
- **Automated Discovery**: Continuous monitoring of 500+ official sources
- **Intelligent Extraction**: AI-powered parsing of announcements from HTML, PDFs, and images
- **Personalized Notifications**: Smart filtering and push notifications based on user preferences
- **Mobile-First Experience**: React Native app for easy access and real-time notifications

## 🏗️ Architecture

```
Web Sources → Crawlers → AI Extraction → Database → API → Mobile App → Notifications
```

### Core Components
- **Backend**: Python FastAPI with PostgreSQL, Redis, and Elasticsearch
- **Mobile App**: React Native with Redux state management
- **Data Pipeline**: Scrapy crawlers + AI extraction + Celery workers
- **Notifications**: Firebase Cloud Messaging (FCM)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

### Mobile App Setup
```bash
cd mobile
npm install
npx react-native run-android  # or run-ios
```

### Using Docker
```bash
docker-compose up -d
```

## 📱 Features

### Core Features
- ✅ Real-time exam notification discovery
- ✅ Smart filtering by category, location, and keywords
- ✅ Push notifications for approaching deadlines
- ✅ Offline access to cached content
- ✅ Search and bookmark functionality

### Advanced Features (Coming Soon)
- 🔄 AI-powered personalized recommendations
- 🔄 Multi-language support (Hindi, English, regional)
- 🔄 Exam calendar integration
- 🔄 Social sharing and community features
- 🔄 Premium features and early access

## 🛠️ Development

### Project Structure
```
NoticeWala/
├── backend/          # FastAPI backend
├── mobile/           # React Native app
├── infrastructure/   # Docker, K8s configs
├── docs/            # Documentation
└── data/            # Sample data
```

### Development Phases
- **Phase 0 (MVP)**: 6-8 weeks - Core functionality
- **Phase 1 (Enhanced)**: 8-12 weeks - AI features
- **Phase 2 (Scale)**: 12-16 weeks - Premium features

## 📊 Monitoring

- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:8000/admin
- **Monitoring**: Prometheus + Grafana
- **Logs**: ELK Stack

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/NoticeWala/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/NoticeWala/discussions)

## 🙏 Acknowledgments

- Built with ❤️ for students and job seekers
- Inspired by the need for better educational information access
- Powered by modern web scraping and AI technologies
