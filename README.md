# Blog Platform API

A modern blog platform built with Django REST Framework, featuring articles, comments, likes, and user authentication.

## Features

- **User Authentication** - JWT-based authentication with dj-rest-auth
- **Articles** - Create, read, update, and delete blog articles
- **Comments** - Comment on articles with ownership-based permissions
- **Likes** - Like/unlike articles with toggle functionality
- **Soft Delete** - All models support soft deletion
- **API Documentation** - Auto-generated Swagger/ReDoc documentation
- **Dockerized** - Complete Docker setup for easy development

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT, dj-rest-auth
- **Documentation**: DRF Spectacular (Swagger/OpenAPI)
- **Container**: Docker & Docker Compose
- **Package Manager**: uv (fast Python package installer)

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://github.com/astral-sh/uv) (optional, for local development)

### Running with Docker Compose (Recommended)

1. **Clone and setup the project:**
```bash
git clone https://github.com/Vlad-the-programmer/Mini-Articles-Posting-Platform-DRF.git
cd blogPlatform
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your configuration if needed and set passwords
```

3. **Build and start the services:**
```bash
docker compose up --build
```

4. **Create superuser (optional):**
```bash
docker compose exec web python manage.py createsuperuser
```

5 **Access the application:**
```
API: http://localhost:8000/api/
Admin: http://localhost:8000/admin/
Swagger Docs: http://localhost:8000/api/schema/swagger-ui/
ReDoc Docs: http://localhost:8000/api/schema/redoc/
```

### Development with uv (Alternative)
If you prefer to run without Docker:
1. **Clone and setup the project:**
```bash
git clone https://github.com/Vlad-the-programmer/Mini-Articles-Posting-Platform-DRF.git
cd blogPlatform
```

2. **Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Setup virtual environment and install dependencies:**
```bash
cd blogPlatform
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env to set your configuration if needed and set passwords
# Edit .env to use SQLite for local development
```

5. **Run database migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Start development server:**
```bash
python manage.py runserver
```

### Project Structure
```
blogPlatform/
├── blogPlatform/          # Django project settings
├── common/               # Common models and utilities
├── users/               # User management app
├── articles/            # Articles app
├── comments/            # Comments app  
├── likes/               # Likes app
├── docker-compose.yml   # Docker configuration
├── Dockerfile          # Web service Dockerfile
├── pyproject.toml      # Python dependencies
├── .env.example        # Environment variables template
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

