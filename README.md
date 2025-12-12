# Haikudo Backend

A FastAPI backend application with PostgreSQL database, containerized with Docker and configured for Docker Swarm deployment.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Docker** - Containerization
- **Docker Swarm** - Container orchestration
- **Pydantic** - Data validation using Python type hints

## Project Structure

```
haikudo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Application configuration
│   ├── database.py      # Database connection and session management
│   ├── models.py        # SQLAlchemy models
│   └── schemas.py       # Pydantic schemas for API serialization
├── alembic/
│   ├── env.py           # Alembic environment configuration
│   └── script.py.mako   # Migration script template
├── alembic.ini          # Alembic configuration
├── docker-compose.yml   # Docker Swarm stack configuration
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
├── deploy.sh           # Deployment script
├── .env                # Environment variables (development)
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Docker Swarm mode enabled

### 1. Clone and Setup

```bash
cd /Users/sajith/Documents/Haikudo/Hakudu-Backend
```

### 2. Environment Configuration

Edit `.env` file with your configuration:

```env
DATABASE_URL=postgresql://haikudo_user:haikudo_password@localhost:5432/haikudo_db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Deploy with Docker Swarm

```bash
# Make deploy script executable (already done)
chmod +x deploy.sh

# Deploy the stack
./deploy.sh
```

### 4. Manual Deployment Steps

If you prefer manual deployment:

```bash
# Initialize Docker Swarm
docker swarm init

# Build the image
docker build -t haikudo-backend:latest .

# Deploy the stack
docker stack deploy -c docker-compose.yml haikudo

# Check service status
docker service ls
```

### 5. Database Migrations

Once the services are running, create and run migrations:

```bash
# Access the API container
docker exec -it $(docker ps -q -f name=haikudo_haikudo-api) /bin/bash

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## API Endpoints

- **GET /** - Welcome message
- **GET /health** - Health check endpoint
- **GET /api/v1/test-db** - Database connection test

Access the API at: http://localhost:8000

## Docker Swarm Management

### View Services

```bash
docker service ls
docker service ps haikudo_haikudo-api
```

### Scale Services

```bash
# Scale API service to 3 replicas
docker service scale haikudo_haikudo-api=3
```

### View Logs

```bash
docker service logs haikudo_haikudo-api
docker service logs haikudo_postgres
```

### Update Services

```bash
# Update API service
docker service update --image haikudo-backend:latest haikudo_haikudo-api
```

### Remove Stack

```bash
docker stack rm haikudo
```

## Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local database configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Models

The application includes basic models:

- **User**: User management with authentication fields
- **Post**: Basic content model

### Adding New Features

1. Create/modify models in `app/models.py`
2. Create/modify schemas in `app/schemas.py`
3. Generate migration: `alembic revision --autogenerate -m "Description"`
4. Apply migration: `alembic upgrade head`
5. Add API endpoints to `app/main.py` or create new router modules

## Security Notes

- Change `SECRET_KEY` in production
- Configure CORS properly for production
- Use environment-specific `.env` files
- Consider using Docker secrets for sensitive data
- Review database credentials and access controls

## Monitoring and Health Checks

The application includes:

- Health check endpoint at `/health`
- Database connection testing at `/api/v1/test-db`
- Docker health checks for both API and database services

## Production Considerations

1. **Environment Variables**: Use Docker secrets or external secret management
2. **Database**: Consider using managed PostgreSQL service
3. **Logging**: Configure proper logging and log aggregation
4. **Monitoring**: Add application and infrastructure monitoring
5. **Load Balancing**: Configure external load balancer if needed
6. **SSL/TLS**: Add HTTPS termination
7. **Backup**: Implement database backup strategy
