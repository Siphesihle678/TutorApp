import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.routes import auth, quiz, assignment, announcement, dashboard

# Create database tables (with error handling for Railway deployment)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("This is normal during initial deployment before database is configured")

# Create FastAPI app
app = FastAPI(
    title="Online Learning Platform",
    description="A comprehensive learning management system for teachers and students",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(assignment.router, prefix="/api/assignments", tags=["Assignments"])
app.include_router(announcement.router, prefix="/api/announcements", tags=["Announcements"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Online Learning Platform API is running",
        "version": "1.0.0"
    }

@app.get("/student")
def student_dashboard():
    try:
        return FileResponse("student/Studentdashboard.html")
    except FileNotFoundError:
        return {"error": "Student dashboard not found"}, 404

@app.get("/teacher")
def teacher_dashboard():
    try:
        return FileResponse("teacher/dashboard.html")
    except FileNotFoundError:
        return {"error": "Teacher dashboard not found"}, 404

@app.get("/api")
def api_info():
    return {
        "message": "Online Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }
