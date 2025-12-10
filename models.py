"""Database models for Naukri Scraper."""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

Base = declarative_base()


class JobSearch(Base):
    """Model for job search queries."""
    __tablename__ = 'job_searches'
    
    id = Column(Integer, primary_key=True)
    job_role = Column(String(200), nullable=False)
    experience_min = Column(Float, nullable=True)
    experience_max = Column(Float, nullable=True)
    location = Column(String(200), nullable=True)
    job_type = Column(String(100), nullable=True)  # Full-time, Part-time, Contract, etc.
    search_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with candidates
    candidates = relationship('Candidate', back_populates='job_search', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<JobSearch(id={self.id}, role='{self.job_role}', location='{self.location}')>"


class Candidate(Base):
    """Model for candidate profiles."""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    job_search_id = Column(Integer, ForeignKey('job_searches.id'), nullable=False)
    
    # Profile information
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    current_location = Column(String(200), nullable=True)
    experience_years = Column(Float, nullable=True)
    current_company = Column(String(200), nullable=True)
    current_designation = Column(String(200), nullable=True)
    skills = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    profile_url = Column(String(500), nullable=True)
    resume_url = Column(String(500), nullable=True)
    
    # Additional details
    notice_period = Column(String(100), nullable=True)
    current_salary = Column(String(100), nullable=True)
    expected_salary = Column(String(100), nullable=True)
    
    # Tracking information
    scraped_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comments = Column(Text, nullable=True)
    
    # Contact status
    contacted = Column(Boolean, default=False)
    interested = Column(Boolean, nullable=True)
    interview_scheduled = Column(Boolean, default=False)
    interview_date = Column(DateTime, nullable=True)
    
    # Relationship
    job_search = relationship('JobSearch', back_populates='candidates')
    call_logs = relationship('CallLog', back_populates='candidate', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', experience={self.experience_years})>"


class CallLog(Base):
    """Model for tracking AI call interactions."""
    __tablename__ = 'call_logs'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    
    # Call details
    call_date = Column(DateTime, default=datetime.utcnow)
    script_used = Column(Text, nullable=True)
    call_duration = Column(Integer, nullable=True)  # in seconds
    call_status = Column(String(50), nullable=True)  # completed, failed, no-answer, etc.
    
    # Response tracking
    candidate_response = Column(Text, nullable=True)
    interested = Column(Boolean, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # AI integration
    ai_tool_used = Column(String(100), nullable=True)  # n8n, make.com, etc.
    webhook_response = Column(Text, nullable=True)
    
    # Relationship
    candidate = relationship('Candidate', back_populates='call_logs')
    
    def __repr__(self):
        return f"<CallLog(id={self.id}, candidate_id={self.candidate_id}, status='{self.call_status}')>"


# Database initialization
def init_db(database_url=None):
    """Initialize the database with all tables."""
    url = database_url or DATABASE_URL
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(database_url=None):
    """Get a database session."""
    url = database_url or DATABASE_URL
    engine = create_engine(url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
    print("Database initialized successfully!")
