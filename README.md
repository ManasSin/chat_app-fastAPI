# Chat Analytics Backend

A scalable, production-ready FastAPI backend for real-time chat analytics with WebSocket support, PostgreSQL, MongoDB, and Redis.

## 🚀 Features

- **Real-time Chat Analytics**: WebSocket-based chat with instant message processing
- **Multi-Database Architecture**: PostgreSQL for user data, MongoDB for chat messages
- **Scalable Infrastructure**: Redis caching, connection pooling, and horizontal scaling support
- **Production Ready**: Docker containerization, health checks, and monitoring
- **Message Analytics**: Word count, sentiment analysis, question detection, and session statistics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (WebSocket)   │◄──►│   Backend       │◄──►│   (User Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │     MongoDB     │
                       │   (Caching)     │    │  (Chat Data)   │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15+
- MongoDB 6+
- Redis 7+

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
cp config.env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/chat/{session_id}

## 🔧 Configuration

### Environment Variables

| Variable       | Description                  | Default                                              |
| -------------- | ---------------------------- | ---------------------------------------------------- |
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/database` |
| `MONGODB_URL`  | MongoDB connection string    | `mongodb://localhost:27017/database`                 |
| `REDIS_URL`    | Redis connection string      | `redis://localhost:6379`                             |
| `DEBUG`        | Debug mode                   | `false`                                              |
| `LOG_LEVEL`    | Logging level                | `INFO`                                               |
| `ENVIRONMENT`  | Environment name             | `development`                                        |

### Database Configuration

- **PostgreSQL**: User management, sessions, and analytics
- **MongoDB**: Chat messages and user interactions
- **Redis**: Caching and session management

## 📊 API Endpoints

### WebSocket

- `GET /ws/chat/{session_id}` - Real-time chat with analytics

### REST API

- `GET /` - Health status
- `GET /health` - Detailed health check
- `GET /session/{session_id}/stats` - Session statistics
- `GET /session/{session_id}/messages` - Session messages

## 🐳 Docker Services

| Service    | Port  | Purpose             |
| ---------- | ----- | ------------------- |
| Backend    | 8000  | FastAPI application |
| PostgreSQL | 5432  | Primary database    |
| MongoDB    | 27017 | Document database   |
| Redis      | 6379  | Caching layer       |

## 🔍 Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "environment": "production",
  "databases": {
    "postgresql": true,
    "mongodb": true
  }
}
```

### Docker Health Checks

All services include health checks:

- **Backend**: HTTP health endpoint
- **PostgreSQL**: Database connectivity
- **MongoDB**: Database ping
- **Redis**: Redis ping

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Production environment
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING
```

### 2. Database Migrations

```bash
# Run migrations
alembic upgrade head

# Check migration status
alembic current
```

### 3. Scaling

```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose up -d nginx
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
python -m pytest test/
```

### Test WebSocket

```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws/chat/test-session

# Send message
{"message": "Hello, world!"}
```

## 📈 Performance

### Connection Pooling

- **PostgreSQL**: 20 connections with 30 overflow
- **MongoDB**: 50 max connections, 10 min connections
- **Redis**: Optimized for high throughput

### Caching Strategy

- **Session Data**: Redis with TTL
- **User Analytics**: Redis with background refresh
- **Message History**: MongoDB with indexes

## 🔒 Security

- **CORS**: Configurable origins for production
- **Input Validation**: Pydantic models with validation
- **Database**: Connection pooling and prepared statements
- **Environment**: Secure configuration management

## 🚧 Development

### Local Development

```bash
# Start only databases
docker-compose up -d postgresql mongo redis

# Run backend locally
python main.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📝 TODO & Roadmap

### ✅ Phase 1: Foundation & Infrastructure (COMPLETED)

- [x] PostgreSQL and MongoDB setup
- [x] Docker containerization
- [x] Database migrations with Alembic
- [x] Connection pooling and optimization
- [x] Environment configuration management

### 🔄 Phase 2: Authentication & Security (NEXT)

- [ ] User authentication with JWT
- [ ] OAuth integration (Auth0)
- [ ] Protected route middleware
- [ ] Rate limiting and security

### 📋 Phase 3: Scalability & Performance

- [ ] Redis implementation for caching
- [ ] Background workers for chat storage
- [ ] Message queuing with Kafka
- [ ] Horizontal scaling support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the health check endpoint

---

**Status**: Phase 1 Complete ✅ | **Next**: Authentication & Security 🔐
