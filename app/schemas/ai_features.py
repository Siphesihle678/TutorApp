from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# ==================== QUIZ GENERATION ====================

class QuizGenerationRequest(BaseModel):
    subject: str = Field(..., description="Subject for the quiz")
    topic: str = Field(..., description="Specific topic for the quiz")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions to generate")

class QuizGenerationResponse(BaseModel):
    success: bool
    quiz_data: Dict[str, Any]
    message: str

# ==================== ASSIGNMENT GRADING ====================

class AssignmentGradingRequest(BaseModel):
    submission: str = Field(..., description="Student's assignment submission")
    rubric: str = Field(..., description="Grading rubric")
    subject: str = Field(..., description="Subject of the assignment")

class AssignmentGradingResponse(BaseModel):
    success: bool
    grade: float = Field(..., ge=0, le=100, description="Grade out of 100")
    feedback: str = Field(..., description="Detailed feedback")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    next_steps: List[str] = Field(default_factory=list, description="Suggestions for next steps")

# ==================== LESSON PLANNING ====================

class LessonPlanRequest(BaseModel):
    subject: str = Field(..., description="Subject for the lesson plan")
    topic: str = Field(..., description="Specific topic for the lesson")
    grade_level: str = Field(..., description="Grade level of students")
    duration: str = Field(default="60 minutes", description="Lesson duration")

class LessonPlanResponse(BaseModel):
    success: bool
    lesson_plan: Dict[str, Any]
    message: str

# ==================== PRACTICE PROBLEMS ====================

class PracticeProblemsRequest(BaseModel):
    subject: str = Field(..., description="Subject for practice problems")
    topic: str = Field(..., description="Specific topic")
    difficulty: str = Field(default="medium", description="Difficulty level")
    num_problems: int = Field(default=5, ge=1, le=15, description="Number of problems")

class PracticeProblemsResponse(BaseModel):
    success: bool
    problems: List[Dict[str, Any]]
    message: str

# ==================== PERFORMANCE ANALYSIS ====================

class PerformanceAnalysisRequest(BaseModel):
    student_data: Dict[str, Any] = Field(..., description="Student performance data for analysis")

class PerformanceAnalysisResponse(BaseModel):
    success: bool
    summary: str = Field(..., description="Performance summary")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas needing improvement")
    teaching_strategies: List[str] = Field(default_factory=list, description="Teaching strategies to support student")
    interventions: List[str] = Field(default_factory=list, description="Intervention recommendations")
    monitoring: List[str] = Field(default_factory=list, description="Progress monitoring suggestions")

# ==================== RUBRIC CREATION ====================

class RubricCreationRequest(BaseModel):
    assignment_type: str = Field(..., description="Type of assignment (essay, project, presentation, etc.)")
    subject: str = Field(..., description="Subject for the rubric")
    grade_level: str = Field(..., description="Grade level of students")

class RubricCreationResponse(BaseModel):
    success: bool
    rubric: Dict[str, Any]
    message: str

# ==================== CONTENT GENERATION ====================

class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., description="Type of content (lesson, summary, notes, review, etc.)")
    subject: str = Field(..., description="Subject for the content")
    topic: str = Field(..., description="Specific topic")
    grade_level: str = Field(..., description="Grade level of students")

class ContentGenerationResponse(BaseModel):
    success: bool
    content: str = Field(..., description="Generated educational content")
    message: str

# ==================== TEACHING FEEDBACK ====================

class TeachingFeedbackRequest(BaseModel):
    lesson_description: str = Field(..., description="Description of the lesson taught")
    student_responses: List[str] = Field(..., description="Student responses or feedback")
    subject: str = Field(..., description="Subject taught")

class TeachingFeedbackResponse(BaseModel):
    success: bool
    effectiveness: str = Field(..., description="Teaching effectiveness assessment")
    strengths: List[str] = Field(default_factory=list, description="What worked well")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    strategies: List[str] = Field(default_factory=list, description="Alternative teaching strategies")
    engagement: List[str] = Field(default_factory=list, description="Student engagement suggestions")
    understanding: str = Field(..., description="Assessment of student understanding")
