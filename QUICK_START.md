# Quick Start Guide

## Local Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (or use SQLite for development)
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd online-learning-platform
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost/learning_platform
SECRET_KEY=your-secret-key-for-development
DEBUG=True
```

### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 5. Frontend Setup
Open `frontend/index.html` in your browser or serve it with a local server:
```bash
cd frontend
python -m http.server 8080
```

### 6. Test the Platform
1. Open http://localhost:8080
2. Register a teacher account
3. Register a student account
4. Test the functionality

## Features Available

### For Teachers:
- ✅ User registration and authentication
- ✅ Dashboard with overview statistics
- ✅ View quizzes and assignments
- ✅ View student performance
- ⏳ Create quizzes (coming soon)
- ⏳ Create assignments (coming soon)
- ⏳ Send announcements (coming soon)

### For Students:
- ✅ User registration and authentication
- ✅ Dashboard with performance overview
- ✅ View available quizzes and assignments
- ✅ Take quizzes with automatic grading
- ✅ View leaderboard
- ⏳ Submit assignments (coming soon)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Quizzes
- `GET /api/quizzes/` - List all quizzes
- `GET /api/quizzes/{id}` - Get quiz details
- `POST /api/quizzes/{id}/start` - Start quiz attempt
- `POST /api/quizzes/{id}/submit` - Submit quiz answers

### Assignments
- `GET /api/assignments/` - List all assignments
- `GET /api/assignments/{id}` - Get assignment details
- `POST /api/assignments/{id}/submit` - Submit assignment

### Dashboard
- `GET /api/dashboard/teacher/overview` - Teacher overview
- `GET /api/dashboard/teacher/students` - Student performance
- `GET /api/dashboard/leaderboard` - Class leaderboard
- `GET /api/dashboard/student/my-performance` - Student performance

## Next Steps

1. **Deploy to Railway**: Follow the `DEPLOYMENT.md` guide
2. **Add More Features**: Implement quiz creation, assignment submission
3. **Enhance UI**: Add more interactive elements and better styling
4. **Add Email Notifications**: Configure SMTP settings
5. **Add File Uploads**: For assignment submissions

## Support

- Check the API documentation at http://localhost:8000/docs
- Review the deployment guide in `DEPLOYMENT.md`
- Check the main README for detailed information
