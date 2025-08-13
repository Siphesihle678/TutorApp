# Tutor-Student Linking System

## Overview

The TutorApp now includes a comprehensive tutor-student linking system that ensures every student account is automatically associated with their assigned tutor upon signup. This system provides tutors with the ability to see and manage only their own students, creating a secure and organized learning environment.

## Features

### 🔗 **Automatic Student-Tutor Association**
- Students can be assigned to a tutor during registration
- Existing students are automatically assigned to the first available teacher
- Tutors can only view and manage their assigned students

### 👨‍🏫 **Tutor Management Dashboard**
- View all assigned students
- See student performance and progress
- Manage student assignments and removals

### 🔒 **Security & Privacy**
- Tutors can only access their own students' data
- Students are isolated to their assigned tutor's view
- Secure API endpoints with proper authentication

## Database Changes

### New Column Added
- `tutor_id` (Integer, nullable) - Links students to their assigned tutor
- Foreign key constraint to `users.id`
- Index for better query performance

### Relationships
- `User.tutor` - Student's assigned tutor
- `User.students` - Tutor's assigned students (backref)

## API Endpoints

### Authentication & Registration
```
POST /api/auth/register
- Now accepts optional tutor_id parameter
- Validates tutor exists and is active
- Automatically links student to tutor

PUT /api/auth/me
- Allows updating tutor assignment
- Validates new tutor exists and is active
```

### Tutor Management
```
GET /api/dashboard/teacher/available-tutors
- List all available tutors for assignment

GET /api/dashboard/teacher/my-students
- Get list of students assigned to current teacher

POST /api/dashboard/teacher/assign-student/{student_id}
- Assign a student to the current teacher

DELETE /api/dashboard/teacher/unassign-student/{student_id}
- Unassign a student from the current teacher
```

### Dashboard Updates
```
GET /api/dashboard/teacher/overview
- Now filters students by tutor_id
- Shows only assigned students count

GET /api/dashboard/teacher/students
- Returns only students assigned to current teacher

GET /api/dashboard/leaderboard
- Teachers see only their students
- Students see all students (configurable)
```

## Usage Examples

### Student Registration with Tutor Assignment
```json
POST /api/auth/register
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword",
    "role": "student",
    "tutor_id": 1
}
```

### Assign Student to Tutor
```json
POST /api/dashboard/teacher/assign-student/5
Authorization: Bearer <teacher_token>

Response:
{
    "message": "Student John Doe successfully assigned to you",
    "student": {
        "id": 5,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

### Get Teacher's Students
```json
GET /api/dashboard/teacher/my-students
Authorization: Bearer <teacher_token>

Response:
[
    {
        "id": 5,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2024-01-15T10:30:00Z",
        "is_active": true
    }
]
```

## Migration

### Running the Migration
```bash
cd TutorApp
python migrate_add_tutor_id.py
```

### What the Migration Does
1. Adds `tutor_id` column to `users` table
2. Creates index for better performance
3. Adds foreign key constraint
4. Assigns existing students to the first available teacher

### Manual Assignment
If you need to manually assign students to specific tutors:

```sql
-- Assign student with ID 5 to teacher with ID 1
UPDATE users SET tutor_id = 1 WHERE id = 5 AND role = 'student';

-- Unassign a student
UPDATE users SET tutor_id = NULL WHERE id = 5 AND role = 'student';
```

## Frontend Integration

### Registration Form
Add a tutor selection dropdown to the student registration form:

```javascript
// Get available tutors
const tutors = await fetch('/api/dashboard/teacher/available-tutors').then(r => r.json());

// Include tutor_id in registration
const registrationData = {
    name: "John Doe",
    email: "john@example.com",
    password: "password",
    role: "student",
    tutor_id: selectedTutorId
};
```

### Teacher Dashboard
Update the teacher dashboard to show only assigned students:

```javascript
// Get teacher's students
const myStudents = await fetch('/api/dashboard/teacher/my-students', {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
```

## Security Considerations

### Access Control
- All tutor-specific endpoints require teacher authentication
- Students can only be assigned to active teachers
- Teachers can only manage their own students

### Data Isolation
- Dashboard queries filter by `tutor_id`
- Performance records are scoped to teacher's students
- Quiz and assignment access is restricted

### Validation
- Tutor ID validation during registration
- Student existence checks before assignment
- Role-based access control on all endpoints

## Benefits

### For Teachers
- Clear view of assigned students only
- Better organization and management
- Focused teaching approach

### For Students
- Dedicated tutor support
- Personalized learning experience
- Clear accountability structure

### For Administrators
- Better user organization
- Improved data security
- Scalable user management

## Future Enhancements

### Planned Features
- Bulk student assignment
- Tutor capacity limits
- Student transfer between tutors
- Tutor performance analytics
- Automated student-tutor matching

### Advanced Features
- Subject-specific tutor assignment
- Temporary tutor assignments
- Tutor availability scheduling
- Student-tutor communication tools
