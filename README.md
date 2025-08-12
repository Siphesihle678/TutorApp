# Online Learning & Assessment Platform

A comprehensive web-based learning management system designed for teachers to create quizzes, assign homework, track student performance, and communicate with students.

## Features

### For Teachers
- **Dashboard**: View all students' performance and analytics
- **Quiz Creation**: Create interactive quizzes with automatic grading
- **Assignment Management**: Post homework and track submissions
- **Performance Tracking**: Monitor individual student progress
- **Leaderboard**: Rank students based on performance
- **Diagnostic Reports**: Generate detailed knowledge level assessments
- **Communication**: Send announcements and notifications to students
- **Email Notifications**: Automated email alerts for students

### For Students
- **Interactive Quizzes**: Take quizzes with immediate feedback
- **Homework Submission**: Complete and submit assignments remotely
- **Performance Tracking**: View personal progress and scores
- **Leaderboard**: See rankings and compare with peers
- **Notifications**: Receive updates and announcements

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT tokens
- **Email**: SMTP integration
- **Deployment**: Railway

## Project Structure

```
online-learning-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── core/           # Configuration and utilities
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── main.py
├── frontend/               # HTML/CSS/JS frontend
│   ├── teacher/           # Teacher dashboard
│   ├── student/           # Student interface
│   └── shared/            # Shared components
├── database/              # Database migrations
└── docs/                  # Documentation
```

## Quick Start

1. Clone the repository
2. Set up environment variables
3. Install dependencies
4. Run database migrations
5. Start the application

## Deployment

This platform is designed to be deployed on Railway for easy hosting and scalability.
