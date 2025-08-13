# Tutor-Student Linking System

## Overview

The TutorApp now includes a comprehensive tutor-student linking system using **Tutor Codes**. When a tutor signs up, they receive a unique 6-character code that they can share with their students. Students then use this code during registration to automatically link to their assigned tutor.

## How It Works

### 🔑 **Tutor Code System**
1. **Tutor signs up** → Gets a unique 6-character Tutor Code (e.g., "ABC123")
2. **Tutor shares their code** with students via email, WhatsApp, etc.
3. **Student signs up** → Enters the Tutor Code → Automatically linked to that tutor
4. **Tutor dashboard** → Shows only students who used their code

### 🎯 **Benefits**
- **Simple & User-Friendly**: No complex IDs, just easy-to-remember codes
- **Secure**: Each code is unique and validated
- **Automatic**: No manual assignment needed
- **Scalable**: Works for any number of tutors and students

## Features

### 🔑 **Tutor Code System**
- Tutors receive unique 6-character codes upon registration
- Students enter tutor codes during signup for automatic linking
- Real-time validation of tutor codes
- Tutors can view and share their codes easily

### 👨‍🏫 **Tutor Management Dashboard**
- View all assigned students
- See student performance and progress
- Manage student assignments and removals

### 🔒 **Security & Privacy**
- Tutors can only access their own students' data
- Students are isolated to their assigned tutor's view
- Secure API endpoints with proper authentication

## Database Changes

### New Columns Added
- `tutor_id` (Integer, nullable) - Links students to their assigned tutor
- `tutor_code` (String, unique) - Unique 6-character code for tutor identification
- Foreign key constraint to `users.id`
- Indexes for better query performance

### Relationships
- `User.tutor` - Student's assigned tutor
- `User.students` - Tutor's assigned students (backref)

## API Endpoints

### Authentication & Registration
```
POST /api/auth/register
- Teachers: Automatically generates unique tutor_code
- Students: Accepts tutor_code parameter for automatic linking
- Validates tutor code exists and is active

GET /api/auth/validate-tutor-code/{tutor_code}
- Validates tutor code and returns tutor information

GET /api/auth/me/tutor-code
- Teachers: Get their unique tutor code for sharing

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

### Teacher Registration (Gets Tutor Code)
```json
POST /api/auth/register
{
    "name": "Dr. Smith",
    "email": "smith@example.com",
    "password": "securepassword",
    "role": "teacher"
}

Response:
{
    "id": 1,
    "name": "Dr. Smith",
    "email": "smith@example.com",
    "role": "teacher",
    "tutor_code": "ABC123",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Student Registration with Tutor Code
```json
POST /api/auth/register
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword",
    "role": "student",
    "tutor_code": "ABC123"
}
```

### Validate Tutor Code
```json
GET /api/auth/validate-tutor-code/ABC123

Response:
{
    "valid": true,
    "tutor_name": "Dr. Smith",
    "tutor_email": "smith@example.com",
    "student_count": 5
}
```

### Get Teacher's Tutor Code
```json
GET /api/auth/me/tutor-code
Authorization: Bearer <teacher_token>

Response:
{
    "tutor_code": "ABC123",
    "name": "Dr. Smith",
    "email": "smith@example.com"
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
