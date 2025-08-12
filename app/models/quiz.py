from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    subject = Column(String, nullable=False)
    time_limit = Column(Integer)  # in minutes
    passing_score = Column(Float, default=60.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="quizzes_created")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    options = Column(JSON)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    points = Column(Float, default=1.0)
    explanation = Column(Text)  # For feedback
    
    # Foreign Keys
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    submissions = relationship("QuizSubmission", back_populates="question", cascade="all, delete-orphan")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    score = Column(Float)
    is_passed = Column(Boolean)
    time_taken = Column(Integer)  # in seconds
    
    # Foreign Keys
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", back_populates="quiz_attempts")
    submissions = relationship("QuizSubmission", back_populates="attempt", cascade="all, delete-orphan")

class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean)
    points_earned = Column(Float, default=0.0)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="submissions")
    attempt = relationship("QuizAttempt", back_populates="submissions")
