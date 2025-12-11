"""Database models for NaukriScapper."""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()


class JobSearch(Base):
    """Job search queries and metadata."""
    __tablename__ = 'job_searches'
    
    id = Column(Integer, primary_key=True)
    query = Column(String(500), nullable=False)
    location = Column(String(200))
    experience = Column(String(50))
    salary = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    results_count = Column(Integer, default=0)
    status = Column(String(50), default='pending')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'query': self.query,
            'location': self.location,
            'experience': self.experience,
            'salary': self.salary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'results_count': self.results_count,
            'status': self.status
        }


class Candidate(Base):
    """Candidate profile data."""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    experience = Column(Float)
    skills = Column(Text)
    location = Column(String(200))
    current_company = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'experience': self.experience,
            'skills': self.skills,
            'location': self.location,
            'current_company': self.current_company,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CallLog(Base):
    """AI call tracking and logging."""
    __tablename__ = 'call_logs'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer)
    call_status = Column(String(50))
    duration = Column(Integer)
    notes = Column(Text)
    webhook_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'call_status': self.call_status,
            'duration': self.duration,
            'notes': self.notes,
            'webhook_response': self.webhook_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'success': self.success
        }


# Database setup
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Get database session."""
    return SessionLocal()
