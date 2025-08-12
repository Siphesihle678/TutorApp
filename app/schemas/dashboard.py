from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==================== TEACHER DASHBOARD SCHEMAS ====================

class RecentActivity(BaseModel):
    type: str  # "quiz_attempt" or "assignment_submission"
    student_name: str
    quiz_title: Optional[str] = None
    assignment_title: Optional[str] = None
    score: Optional[float] = None
    date: datetime

class SubjectBreakdown(BaseModel):
    quizzes: int
    assignments: int

class TeacherDashboard(BaseModel):
    total_students: int
    total_quizzes: int
    total_assignments: int
    recent_quiz_attempts: int
    recent_assignment_submissions: int
    average_performance: float
    recent_activity: List[RecentActivity] = []
    subject_breakdown: Dict[str, SubjectBreakdown] = {}

# ==================== STUDENT DASHBOARD SCHEMAS ====================

class RecentPerformance(BaseModel):
    assessment_type: str
    subject: str
    score: float
    max_score: float
    percentage: float
    date: datetime

class UpcomingDeadline(BaseModel):
    assignment_id: int
    title: str
    subject: str
    due_date: datetime
    days_remaining: int

class StudentDashboard(BaseModel):
    total_assessments: int
    average_percentage: float
    best_score: float
    current_rank: int
    recent_performance: List[RecentPerformance] = []
    subject_breakdown: Dict[str, float] = {}
    upcoming_deadlines: List[UpcomingDeadline] = []

# ==================== PERFORMANCE ANALYTICS SCHEMAS ====================

class PerformanceTrend(BaseModel):
    date: datetime
    average_percentage: float
    count: int

class SubjectAnalytics(BaseModel):
    subject: str
    average_percentage: float
    total_assessments: int
    best_score: float
    worst_score: float

class DifficultyAnalysis(BaseModel):
    easy: Dict[str, Any]
    medium: Dict[str, Any]
    hard: Dict[str, Any]

class PerformanceAnalytics(BaseModel):
    total_assessments: int
    average_performance: float
    performance_trend: List[PerformanceTrend] = []
    subject_analytics: List[SubjectAnalytics] = []
    difficulty_analysis: DifficultyAnalysis

# ==================== TIME SERIES DATA SCHEMAS ====================

class TimeSeriesData(BaseModel):
    date: datetime
    value: float
    label: str

class ProgressReport(BaseModel):
    student_id: int
    student_name: str
    start_date: datetime
    end_date: datetime
    initial_percentage: float
    final_percentage: float
    improvement: float
    assessments_taken: int
    trend_data: List[TimeSeriesData] = []

# ==================== COMPARATIVE ANALYTICS SCHEMAS ====================

class ClassComparison(BaseModel):
    class_average: float
    student_percentage: float
    percentile: int
    rank_in_class: int
    total_students: int

class SubjectComparison(BaseModel):
    subject: str
    class_average: float
    student_average: float
    difference: float
    rank_in_subject: int

class ComparativeAnalytics(BaseModel):
    overall_comparison: ClassComparison
    subject_comparisons: List[SubjectComparison] = []

# ==================== ENGAGEMENT ANALYTICS SCHEMAS ====================

class EngagementMetrics(BaseModel):
    total_logins: int
    average_session_duration: int  # in minutes
    quizzes_completed: int
    assignments_submitted: int
    last_active: datetime
    streak_days: int

class ActivityTimeline(BaseModel):
    date: datetime
    activity_type: str
    duration: int  # in minutes
    items_completed: int

class EngagementAnalytics(BaseModel):
    metrics: EngagementMetrics
    activity_timeline: List[ActivityTimeline] = []
    weekly_activity: Dict[str, int] = {}  # day of week -> activity count

# ==================== PREDICTIVE ANALYTICS SCHEMAS ====================

class PerformancePrediction(BaseModel):
    predicted_percentage: float
    confidence_level: float
    factors: List[str]
    recommendations: List[str]

class RiskAssessment(BaseModel):
    risk_level: str  # "low", "medium", "high"
    risk_factors: List[str]
    intervention_suggestions: List[str]
    predicted_outcome: str

class PredictiveAnalytics(BaseModel):
    performance_prediction: PerformancePrediction
    risk_assessment: RiskAssessment
    next_assessment_prediction: Optional[float] = None

# ==================== EXPORT AND REPORTING SCHEMAS ====================

class ExportOptions(BaseModel):
    format: str  # "csv", "pdf", "excel"
    date_range: Optional[str] = None
    include_charts: bool = True
    include_details: bool = True

class ReportSummary(BaseModel):
    report_id: str
    generated_at: datetime
    date_range: str
    total_students: int
    total_assessments: int
    average_performance: float
    key_insights: List[str] = []

class CustomReport(BaseModel):
    title: str
    description: str
    filters: Dict[str, Any]
    metrics: List[str]
    visualization_type: str
    schedule: Optional[str] = None  # cron expression for automated reports

# ==================== NOTIFICATION SCHEMAS ====================

class NotificationSettings(BaseModel):
    email_notifications: bool = True
    performance_alerts: bool = True
    deadline_reminders: bool = True
    weekly_reports: bool = False
    custom_alerts: Dict[str, bool] = {}

class AlertThreshold(BaseModel):
    performance_below: float = 60.0
    missing_deadlines: int = 2
    declining_trend: float = 10.0

class NotificationPreferences(BaseModel):
    settings: NotificationSettings
    thresholds: AlertThreshold
    preferred_time: str = "09:00"  # HH:MM format

# ==================== DASHBOARD CONFIGURATION SCHEMAS ====================

class WidgetConfig(BaseModel):
    widget_type: str
    position: Dict[str, int]  # x, y coordinates
    size: Dict[str, int]  # width, height
    settings: Dict[str, Any] = {}

class DashboardLayout(BaseModel):
    user_id: int
    layout_name: str
    widgets: List[WidgetConfig] = []
    theme: str = "default"
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds

class UserPreferences(BaseModel):
    dashboard_layout: DashboardLayout
    notification_preferences: NotificationPreferences
    display_settings: Dict[str, Any] = {}
