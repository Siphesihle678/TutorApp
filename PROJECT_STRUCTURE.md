# TutorApp Project Structure

## Overview
TutorApp is a comprehensive Online Learning Platform built with FastAPI (Python) and HTML/CSS/JavaScript frontend.

## Directory Structure

```
TutorApp/
├── app/                          # Main application package
│   ├── __init__.py              # Makes app a Python package
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication utilities
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   └── security.py          # Security utilities
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── quiz.py              # Quiz model
│   │   ├── assignment.py        # Assignment model
│   │   ├── announcement.py      # Announcement model
│   │   └── performance.py       # Performance tracking
│   ├── routes/                  # API routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── quiz.py              # Quiz routes
│   │   ├── assignment.py        # Assignment routes
│   │   ├── announcement.py      # Announcement routes
│   │   └── dashboard.py         # Dashboard routes
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py              # User schemas
│   │   ├── quiz.py              # Quiz schemas
│   │   ├── assignment.py        # Assignment schemas
│   │   ├── announcement.py      # Announcement schemas
│   │   └── performance.py       # Performance schemas
│   └── services/                # Business logic services
│       ├── __init__.py
│       └── email_service.py     # Email functionality
├── student/                     # Student frontend
│   ├── __init__.py
│   └── dashboard.html           # Student dashboard
├── teacher/                     # Teacher frontend
│   ├── __init__.py
│   └── dashboard.html           # Teacher dashboard
├── main.py                      # FastAPI application entry point
├── start.py                     # Railway deployment startup script
├── test_app.py                  # Application testing script
├── requirements.txt             # Python dependencies
├── Procfile                     # Railway deployment configuration
├── runtime.txt                  # Python version specification
├── railway.json                 # Railway deployment settings
├── .gitignore                   # Git ignore rules
├── README.md                    # Project documentation
├── QUICK_START.md               # Quick start guide
├── DEPLOYMENT.md                # Deployment instructions
└── index.html                   # Main landing page
```

## Key Files Explained

### Backend (FastAPI)
- **main.py**: Main application entry point with FastAPI app configuration
- **start.py**: Railway deployment startup script with proper path handling
- **requirements.txt**: All Python dependencies with specific versions
- **Procfile**: Tells Railway how to start the application

### Frontend (HTML/CSS/JavaScript)
- **index.html**: Main landing page with login/registration
- **student/dashboard.html**: Student dashboard with quiz taking, assignments
- **teacher/dashboard.html**: Teacher dashboard with quiz creation, grading

### Configuration
- **railway.json**: Railway-specific deployment configuration
- **runtime.txt**: Specifies Python version (3.11.7)
- **.gitignore**: Excludes unnecessary files from Git tracking

## Deployment Files

### Railway Deployment
- **Procfile**: `web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
- **railway.json**: Health check configuration and deployment settings
- **start.py**: Alternative startup script with better error handling

### Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT token secret key
- `DEBUG`: Set to `False` for production

## Features

### For Students
- Take quizzes with automatic grading
- Submit assignments
- View performance and leaderboard
- Access announcements

### For Teachers
- Create and manage quizzes
- Grade assignments
- Track student performance
- Send announcements
- View analytics

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Quizzes
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/` - Create quiz
- `POST /api/quizzes/{quiz_id}/submit` - Submit quiz answers

### Assignments
- `GET /api/assignments/` - List assignments
- `POST /api/assignments/` - Create assignment
- `POST /api/assignments/{assignment_id}/submit` - Submit assignment

### Dashboard
- `GET /api/dashboard/student` - Student dashboard data
- `GET /api/dashboard/teacher` - Teacher dashboard data

## Database Models

### Core Models
- **User**: Students and teachers with role-based access
- **Quiz**: Quiz questions and answers
- **Assignment**: Assignment submissions and grading
- **Announcement**: System announcements
- **Performance**: Student performance tracking

## Security Features
- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- CORS middleware for frontend integration

## Deployment Notes
- All directories have `__init__.py` files for proper Python package structure
- Health check endpoint at `/health` for Railway monitoring
- Error handling for database initialization during deployment
- Comprehensive logging for debugging deployment issues
