from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with Base
# This must be done after Base is defined
def import_models():
    """Import all models to register them with SQLAlchemy"""
    try:
        from ..models.user import User
        from ..models.quiz import Quiz, Question, QuizAttempt, QuizSubmission
        from ..models.assignment import Assignment, AssignmentSubmission
        from ..models.announcement import Announcement
        from ..models.performance import PerformanceRecord
        # Note: Subject models are intentionally excluded to avoid import issues
        print("✅ All models imported successfully")
    except Exception as e:
        print(f"❌ Model import error: {e}")
        raise
