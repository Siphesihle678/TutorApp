import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime, timedelta
import os

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@tutorapp.com")

class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email with HTML and text content"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_quiz_notification(self, student_email: str, student_name: str, quiz_title: str, subject: str) -> bool:
        """Send notification about new quiz"""
        subject = f"New Quiz Available: {quiz_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>🎯 New Quiz Available!</h2>
            <p>Hello {student_name},</p>
            <p>A new quiz has been posted for your class:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>{quiz_title}</h3>
                <p><strong>Subject:</strong> {subject}</p>
                <p>Log in to your dashboard to take the quiz!</p>
            </div>
            <p>Good luck!</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        New Quiz Available!
        
        Hello {student_name},
        
        A new quiz has been posted for your class:
        
        Quiz: {quiz_title}
        Subject: {subject}
        
        Log in to your dashboard to take the quiz!
        
        Good luck!
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_assignment_notification(self, student_email: str, student_name: str, assignment_title: str, subject: str, due_date: datetime) -> bool:
        """Send notification about new assignment"""
        subject = f"New Assignment: {assignment_title}"
        
        due_date_str = due_date.strftime("%B %d, %Y at %I:%M %p")
        
        html_content = f"""
        <html>
        <body>
            <h2>📝 New Assignment Posted!</h2>
            <p>Hello {student_name},</p>
            <p>A new assignment has been posted:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>{assignment_title}</h3>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Due Date:</strong> {due_date_str}</p>
                <p>Log in to your dashboard to view the assignment details and submit your work.</p>
            </div>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        New Assignment Posted!
        
        Hello {student_name},
        
        A new assignment has been posted:
        
        Assignment: {assignment_title}
        Subject: {subject}
        Due Date: {due_date_str}
        
        Log in to your dashboard to view the assignment details and submit your work.
        
        Best regards,
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_grade_notification(self, student_email: str, student_name: str, assessment_title: str, score: float, max_score: float) -> bool:
        """Send notification about graded assessment"""
        subject = f"Grade Available: {assessment_title}"
        percentage = (score / max_score) * 100
        
        html_content = f"""
        <html>
        <body>
            <h2>📊 Your Grade is Available!</h2>
            <p>Hello {student_name},</p>
            <p>Your grade for <strong>{assessment_title}</strong> is now available:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Grade Summary</h3>
                <p><strong>Score:</strong> {score}/{max_score}</p>
                <p><strong>Percentage:</strong> {percentage:.1f}%</p>
                <p>Log in to your dashboard to view detailed feedback and explanations.</p>
            </div>
            <p>Keep up the great work!</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Your Grade is Available!
        
        Hello {student_name},
        
        Your grade for {assessment_title} is now available:
        
        Score: {score}/{max_score}
        Percentage: {percentage:.1f}%
        
        Log in to your dashboard to view detailed feedback and explanations.
        
        Keep up the great work!
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_deadline_reminder(self, student_email: str, student_name: str, assignment_title: str, due_date: datetime, days_remaining: int) -> bool:
        """Send deadline reminder"""
        subject = f"Deadline Reminder: {assignment_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>⏰ Assignment Deadline Reminder</h2>
            <p>Hello {student_name},</p>
            <p>This is a friendly reminder about your upcoming assignment deadline:</p>
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3>{assignment_title}</h3>
                <p><strong>Due Date:</strong> {due_date.strftime("%B %d, %Y at %I:%M %p")}</p>
                <p><strong>Time Remaining:</strong> {days_remaining} day{'s' if days_remaining != 1 else ''}</p>
                <p>Don't forget to submit your work on time!</p>
            </div>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Assignment Deadline Reminder
        
        Hello {student_name},
        
        This is a friendly reminder about your upcoming assignment deadline:
        
        Assignment: {assignment_title}
        Due Date: {due_date.strftime("%B %d, %Y at %I:%M %p")}
        Time Remaining: {days_remaining} day{'s' if days_remaining != 1 else ''}
        
        Don't forget to submit your work on time!
        
        Best regards,
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_performance_alert(self, student_email: str, student_name: str, subject: str, current_percentage: float, threshold: float = 60.0) -> bool:
        """Send performance alert for low scores"""
        subject = f"Performance Alert: {subject}"
        
        html_content = f"""
        <html>
        <body>
            <h2>⚠️ Performance Alert</h2>
            <p>Hello {student_name},</p>
            <p>We noticed that your performance in <strong>{subject}</strong> could use some improvement:</p>
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <h3>Current Performance</h3>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Current Average:</strong> {current_percentage:.1f}%</p>
                <p><strong>Target:</strong> {threshold}%</p>
                <p>Consider reviewing the material or seeking additional help to improve your understanding.</p>
            </div>
            <p>We're here to help you succeed!</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Performance Alert
        
        Hello {student_name},
        
        We noticed that your performance in {subject} could use some improvement:
        
        Current Average: {current_percentage:.1f}%
        Target: {threshold}%
        
        Consider reviewing the material or seeking additional help to improve your understanding.
        
        We're here to help you succeed!
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_weekly_report(self, student_email: str, student_name: str, weekly_stats: dict) -> bool:
        """Send weekly performance report"""
        subject = "Your Weekly Performance Report"
        
        html_content = f"""
        <html>
        <body>
            <h2>📈 Your Weekly Performance Report</h2>
            <p>Hello {student_name},</p>
            <p>Here's your performance summary for this week:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Weekly Summary</h3>
                <p><strong>Assessments Completed:</strong> {weekly_stats.get('assessments_completed', 0)}</p>
                <p><strong>Average Score:</strong> {weekly_stats.get('average_score', 0):.1f}%</p>
                <p><strong>Best Score:</strong> {weekly_stats.get('best_score', 0):.1f}%</p>
                <p><strong>Time Spent:</strong> {weekly_stats.get('time_spent', 0)} minutes</p>
                <p><strong>Current Rank:</strong> {weekly_stats.get('current_rank', 'N/A')}</p>
            </div>
            <p>Keep up the great work!</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Your Weekly Performance Report
        
        Hello {student_name},
        
        Here's your performance summary for this week:
        
        Assessments Completed: {weekly_stats.get('assessments_completed', 0)}
        Average Score: {weekly_stats.get('average_score', 0):.1f}%
        Best Score: {weekly_stats.get('best_score', 0):.1f}%
        Time Spent: {weekly_stats.get('time_spent', 0)} minutes
        Current Rank: {weekly_stats.get('current_rank', 'N/A')}
        
        Keep up the great work!
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_announcement_notification(self, student_email: str, student_name: str, announcement_title: str, announcement_content: str, teacher_name: str) -> bool:
        """Send notification about new announcement"""
        subject = f"Announcement: {announcement_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>📢 New Announcement</h2>
            <p>Hello {student_name},</p>
            <p>Your teacher <strong>{teacher_name}</strong> has posted a new announcement:</p>
            <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3>{announcement_title}</h3>
                <p>{announcement_content}</p>
            </div>
            <p>Log in to your dashboard for more details.</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        New Announcement
        
        Hello {student_name},
        
        Your teacher {teacher_name} has posted a new announcement:
        
        {announcement_title}
        
        {announcement_content}
        
        Log in to your dashboard for more details.
        
        Best regards,
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)
    
    def send_welcome_email(self, student_email: str, student_name: str) -> bool:
        """Send welcome email to new students"""
        subject = "Welcome to TutorApp!"
        
        html_content = f"""
        <html>
        <body>
            <h2>🎉 Welcome to TutorApp!</h2>
            <p>Hello {student_name},</p>
            <p>Welcome to TutorApp! We're excited to have you join our learning community.</p>
            <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3>Getting Started</h3>
                <ul>
                    <li>Complete your profile</li>
                    <li>Explore available quizzes and assignments</li>
                    <li>Check your dashboard for performance insights</li>
                    <li>Join the leaderboard to compete with classmates</li>
                </ul>
            </div>
            <p>If you have any questions, don't hesitate to reach out to your teacher.</p>
            <p>Happy learning!</p>
            <p>Best regards,<br>Your TutorApp Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to TutorApp!
        
        Hello {student_name},
        
        Welcome to TutorApp! We're excited to have you join our learning community.
        
        Getting Started:
        - Complete your profile
        - Explore available quizzes and assignments
        - Check your dashboard for performance insights
        - Join the leaderboard to compete with classmates
        
        If you have any questions, don't hesitate to reach out to your teacher.
        
        Happy learning!
        Your TutorApp Team
        """
        
        return self.send_email(student_email, subject, html_content, text_content)

# Create global email service instance
email_service = EmailService()

# Convenience functions for backward compatibility
def send_quiz_notification(student_email: str, student_name: str, quiz_title: str, subject: str) -> bool:
    return email_service.send_quiz_notification(student_email, student_name, quiz_title, subject)

def send_assignment_notification(student_email: str, student_name: str, assignment_title: str, subject: str, due_date: datetime) -> bool:
    return email_service.send_assignment_notification(student_email, student_name, assignment_title, subject, due_date)

def send_grade_notification(student_email: str, student_name: str, assessment_title: str, score: float, max_score: float) -> bool:
    return email_service.send_grade_notification(student_email, student_name, assessment_title, score, max_score)

def send_deadline_reminder(student_email: str, student_name: str, assignment_title: str, due_date: datetime, days_remaining: int) -> bool:
    return email_service.send_deadline_reminder(student_email, student_name, assignment_title, due_date, days_remaining)

def send_performance_alert(student_email: str, student_name: str, subject: str, current_percentage: float, threshold: float = 60.0) -> bool:
    return email_service.send_performance_alert(student_email, student_name, subject, current_percentage, threshold)

def send_weekly_report(student_email: str, student_name: str, weekly_stats: dict) -> bool:
    return email_service.send_weekly_report(student_email, student_name, weekly_stats)

def send_announcement_notification(student_email: str, student_name: str, announcement_title: str, announcement_content: str, teacher_name: str) -> bool:
    return email_service.send_announcement_notification(student_email, student_name, announcement_title, announcement_content, teacher_name)

def send_welcome_email(student_email: str, student_name: str) -> bool:
    return email_service.send_welcome_email(student_email, student_name)
