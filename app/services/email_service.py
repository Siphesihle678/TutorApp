import emails
from typing import List
from ..core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_config = {
            'host': settings.SMTP_HOST,
            'port': settings.SMTP_PORT,
            'user': settings.SMTP_USERNAME,
            'password': settings.SMTP_PASSWORD,
            'tls': True,
        }
    
    def send_announcement_notification(self, student_emails: List[str], announcement_title: str, announcement_content: str):
        """Send announcement notification to students"""
        subject = f"New Announcement: {announcement_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>New Announcement</h2>
            <h3>{announcement_title}</h3>
            <p>{announcement_content}</p>
            <p>Please log in to your learning platform to view the full announcement.</p>
            <br>
            <p>Best regards,<br>Your Learning Platform</p>
        </body>
        </html>
        """
        
        return self._send_email(student_emails, subject, html_content)
    
    def send_quiz_reminder(self, student_email: str, student_name: str, quiz_title: str, due_date: str):
        """Send quiz reminder to student"""
        subject = f"Quiz Reminder: {quiz_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Quiz Reminder</h2>
            <p>Hello {student_name},</p>
            <p>This is a reminder that you have a quiz due:</p>
            <ul>
                <li><strong>Quiz:</strong> {quiz_title}</li>
                <li><strong>Due Date:</strong> {due_date}</li>
            </ul>
            <p>Please log in to your learning platform to complete the quiz.</p>
            <br>
            <p>Best regards,<br>Your Learning Platform</p>
        </body>
        </html>
        """
        
        return self._send_email([student_email], subject, html_content)
    
    def send_assignment_reminder(self, student_email: str, student_name: str, assignment_title: str, due_date: str):
        """Send assignment reminder to student"""
        subject = f"Assignment Reminder: {assignment_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Assignment Reminder</h2>
            <p>Hello {student_name},</p>
            <p>This is a reminder that you have an assignment due:</p>
            <ul>
                <li><strong>Assignment:</strong> {assignment_title}</li>
                <li><strong>Due Date:</strong> {due_date}</li>
            </ul>
            <p>Please log in to your learning platform to submit your assignment.</p>
            <br>
            <p>Best regards,<br>Your Learning Platform</p>
        </body>
        </html>
        """
        
        return self._send_email([student_email], subject, html_content)
    
    def send_grade_notification(self, student_email: str, student_name: str, assessment_title: str, score: float, max_score: float):
        """Send grade notification to student"""
        percentage = (score / max_score) * 100
        subject = f"Grade Available: {assessment_title}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Grade Available</h2>
            <p>Hello {student_name},</p>
            <p>Your grade for {assessment_title} is now available:</p>
            <ul>
                <li><strong>Score:</strong> {score}/{max_score}</li>
                <li><strong>Percentage:</strong> {percentage:.1f}%</li>
            </ul>
            <p>Please log in to your learning platform to view detailed feedback.</p>
            <br>
            <p>Best regards,<br>Your Learning Platform</p>
        </body>
        </html>
        """
        
        return self._send_email([student_email], subject, html_content)
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str):
        """Send email using SMTP"""
        try:
            message = emails.Message(
                subject=subject,
                html=html_content,
                mail_from=settings.FROM_EMAIL
            )
            
            response = message.send(
                to=to_emails,
                smtp=self.smtp_config
            )
            
            return response.status_code == 250
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

email_service = EmailService()
