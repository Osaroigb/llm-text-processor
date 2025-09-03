# LLM Text Processor

A lightweight FastAPI service that ingests unstructured text, generates LLM-based summaries, extracts structured metadata, and stores results in PostgreSQL. Includes search/filter endpoints, comprehensive testing, and Dockerized deployment.

## 🚀 Features

- **Text Analysis**: LLM-powered text summarization, sentiment analysis, and topic extraction
- **NLP Processing**: Keyword extraction using NLTK with configurable parameters, stored in metadata
- **Structured Storage**: PostgreSQL database with optimized search capabilities
- **RESTful API**: FastAPI endpoints for analysis and search operations
- **Type Safety**: Pydantic schemas and SQLAlchemy models with strong typing
- **Comprehensive Testing**: Unit tests covering all major components
- **Docker Support**: Containerized deployment with Docker Compose

## 🏗️ Architecture & Design Choices

### **Why This Structure?**

The codebase follows a **layered architecture** pattern that separates concerns and promotes maintainability:

1. **`app/core/`** - Configuration and database connection management using Pydantic settings and async SQLAlchemy
2. **`app/models/`** - SQLAlchemy ORM models with enum-based constraints for data integrity
3. **`app/schemas/`** - Pydantic models for API request/response validation and serialization
4. **`app/services/`** - Business logic layer (LLM integration, NLP processing) that's easily testable and mockable
5. **`app/api/`** - FastAPI route handlers that orchestrate services and handle HTTP concerns
6. **`app/tests/`** - Comprehensive test suite with proper mocking and edge case coverage

### **Why These Tools?**

- **FastAPI**: Chosen for its automatic OpenAPI generation, async support, and excellent type hints
- **SQLAlchemy Async**: Provides async database operations without blocking the event loop
- **Poetry**: Modern dependency management with lock files for reproducible builds
- **NLTK**: Mature NLP library with excellent tokenization and POS tagging capabilities
- **Pydantic V2**: Fast data validation and serialization with excellent IDE support
- **PostgreSQL**: Robust database with JSON support and advanced indexing capabilities

### **Key Design Principles**

- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Services are injected into API routes for easy testing
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Async-First**: All I/O operations are async for better performance
- **Error Handling**: Consistent error handling with proper logging and rollbacks

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.12+
- Poetry (dependency manager)
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (if running locally)

### 1. Clone the Repository

```bash
git clone https://github.com/Osaroigb/llm-text-processor.git
cd llm-text-processor
```

### 2. Configure Poetry for In-Project Virtual Environment

```bash
# Configure Poetry to create venv inside the project
poetry config virtualenvs.in-project true

# Remove existing venv if any
rm -rf .venv

# Install dependencies (creates .venv/ in project root)
poetry install
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=llm_processor
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5433/llm_processor

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# App Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
```

### 4. Database Setup

```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Wait for database to be ready, then run migrations
poetry run python scripts/init_db.py
```

### 5. Download NLTK Data

```bash
# Download required NLTK packages
poetry run python scripts/download_nltk_data.py
```

### 6. Run the Application

#### Development Mode

```bash
# Activate virtual environment
poetry shell

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Using Poetry

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Deployment

### Full Stack Deployment

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Individual Services

```bash
# Start only PostgreSQL
docker-compose up postgres -d

# Start only the app
docker-compose up app -d
```

## 🧪 Testing

### Run All Tests

```bash
poetry run pytest
```

### Run Specific Test Categories

```bash
# API endpoint tests
poetry run pytest app/tests/test_api.py -v

# LLM service tests
poetry run pytest app/tests/test_llm_service.py -v

# NLP utilities tests
poetry run pytest app/tests/test_nlp_utils.py -v
```

## 📚 API Usage

### Analyze Text

```bash
curl -X POST "http://localhost:8000/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to analyze goes here. This will be processed by the LLM service to extract summary, sentiment, and keywords."
  }'
```

### Search Analyses

```bash
# Search by keyword
curl "http://localhost:8000/analysis/search?keyword=analysis&limit=5"

# Search by sentiment
curl "http://localhost:8000/analysis/search?sentiment=positive&limit=10"

# Combined search with pagination
curl "http://localhost:8000/analysis/search?keyword=text&sentiment=neutral&limit=5&offset=0"
```

## 🔧 Development

### Code Quality Tools

```bash
# Format code with Black
poetry run black app/

# Sort imports with isort
poetry run isort app/

# Type checking with mypy
poetry run mypy app/

# Lint with pyright (VS Code integration)
poetry run pyright
```

## 📊 Performance Optimizations

The application includes several performance optimizations:

- **JSON Operators**: Native PostgreSQL JSON operations for keyword search
- **Async Operations**: Non-blocking I/O for better concurrency
- **Connection Pooling**: Efficient database connection management
- **Caching**: NLTK data downloaded once and reused

## ⚠️ Trade-offs & Limitations

### **What I Didn't Implement (Due to Time Constraints)**

1. **Database Migrations for Indexes**: No performance indexes are created through Alembic migrations
2. **Comprehensive Integration Tests**: While we have good unit test coverage, end-to-end integration tests are limited
3. **Rate Limiting**: No API rate limiting implemented for production use
4. **Authentication/Authorization**: No user management or access control
5. **Caching Layer**: No Redis or in-memory caching for frequently accessed data
6. **Background Tasks**: No Celery or similar for handling long-running LLM operations
7. **Monitoring & Metrics**: No Prometheus/Grafana integration for production monitoring

### **Design Trade-offs Made**

- **NLTK vs spaCy**: Chose NLTK for simplicity and stability, though spaCy would offer better performance
- **Synchronous vs Async**: Fully async design for better scalability, but adds complexity
- **JSON vs Structured Columns**: Used JSON for metadata flexibility, but loses some query optimization
- **Enum vs String**: Strong typing with enums for data integrity, but less flexible for future sentiment values

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MPL-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Enhancements

- [ ] Add database migrations for performance indexes
- [ ] Implement comprehensive integration tests
- [ ] Add API rate limiting and authentication
- [ ] Integrate Redis for caching
- [ ] Add background task processing with Celery
- [ ] Implement monitoring and metrics collection
- [ ] Add support for multiple LLM providers
- [ ] Implement vector similarity search for semantic matching
