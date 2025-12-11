"""Data management for NaukriScapper."""
from typing import List, Dict, Optional
from models import JobSearch, Candidate, CallLog, get_session


class DataManager:
    """Manages database operations for job searches, candidates, and call logs."""
    
    def __init__(self):
        """Initialize data manager."""
        self.session = get_session()
    
    def create_job_search(self, query: str, location: str = None, 
                         experience: str = None, salary: str = None) -> JobSearch:
        """Create a new job search record.
        
        Args:
            query: Search query
            location: Job location
            experience: Experience level
            salary: Salary range
            
        Returns:
            Created JobSearch object
        """
        job_search = JobSearch(
            query=query,
            location=location,
            experience=experience,
            salary=salary
        )
        self.session.add(job_search)
        self.session.commit()
        return job_search
    
    def update_job_search(self, search_id: int, results_count: int = None, 
                         status: str = None) -> Optional[JobSearch]:
        """Update job search record.
        
        Args:
            search_id: ID of the job search
            results_count: Number of results found
            status: Search status
            
        Returns:
            Updated JobSearch object or None
        """
        job_search = self.session.query(JobSearch).filter_by(id=search_id).first()
        if job_search:
            if results_count is not None:
                job_search.results_count = results_count
            if status:
                job_search.status = status
            self.session.commit()
        return job_search
    
    def get_job_search(self, search_id: int) -> Optional[JobSearch]:
        """Get job search by ID.
        
        Args:
            search_id: ID of the job search
            
        Returns:
            JobSearch object or None
        """
        return self.session.query(JobSearch).filter_by(id=search_id).first()
    
    def list_job_searches(self, limit: int = 100) -> List[JobSearch]:
        """List all job searches.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of JobSearch objects
        """
        return self.session.query(JobSearch).order_by(JobSearch.created_at.desc()).limit(limit).all()
    
    def create_candidate(self, name: str, email: str = None, phone: str = None,
                        experience: float = None, skills: str = None, 
                        location: str = None, current_company: str = None) -> Candidate:
        """Create a new candidate record.
        
        Args:
            name: Candidate name
            email: Email address
            phone: Phone number
            experience: Years of experience
            skills: Skills (comma-separated)
            location: Location
            current_company: Current company
            
        Returns:
            Created Candidate object
        """
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            experience=experience,
            skills=skills,
            location=location,
            current_company=current_company
        )
        self.session.add(candidate)
        self.session.commit()
        return candidate
    
    def get_candidate(self, candidate_id: int) -> Optional[Candidate]:
        """Get candidate by ID.
        
        Args:
            candidate_id: ID of the candidate
            
        Returns:
            Candidate object or None
        """
        return self.session.query(Candidate).filter_by(id=candidate_id).first()
    
    def list_candidates(self, limit: int = 100) -> List[Candidate]:
        """List all candidates.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of Candidate objects
        """
        return self.session.query(Candidate).order_by(Candidate.created_at.desc()).limit(limit).all()
    
    def search_candidates(self, skills: str = None, location: str = None, 
                         min_experience: float = None) -> List[Candidate]:
        """Search candidates by criteria.
        
        Args:
            skills: Skills to search for
            location: Location to filter by
            min_experience: Minimum experience required
            
        Returns:
            List of matching Candidate objects
        """
        query = self.session.query(Candidate)
        
        if skills:
            query = query.filter(Candidate.skills.contains(skills))
        if location:
            query = query.filter(Candidate.location.contains(location))
        if min_experience is not None:
            query = query.filter(Candidate.experience >= min_experience)
        
        return query.all()
    
    def create_call_log(self, candidate_id: int, call_status: str = None,
                       duration: int = None, notes: str = None, 
                       webhook_response: str = None, success: bool = False) -> CallLog:
        """Create a new call log record.
        
        Args:
            candidate_id: ID of the candidate
            call_status: Status of the call
            duration: Call duration in seconds
            notes: Call notes
            webhook_response: Webhook response data
            success: Whether call was successful
            
        Returns:
            Created CallLog object
        """
        call_log = CallLog(
            candidate_id=candidate_id,
            call_status=call_status,
            duration=duration,
            notes=notes,
            webhook_response=webhook_response,
            success=success
        )
        self.session.add(call_log)
        self.session.commit()
        return call_log
    
    def get_call_log(self, log_id: int) -> Optional[CallLog]:
        """Get call log by ID.
        
        Args:
            log_id: ID of the call log
            
        Returns:
            CallLog object or None
        """
        return self.session.query(CallLog).filter_by(id=log_id).first()
    
    def list_call_logs(self, candidate_id: int = None, limit: int = 100) -> List[CallLog]:
        """List call logs.
        
        Args:
            candidate_id: Filter by candidate ID
            limit: Maximum number of results
            
        Returns:
            List of CallLog objects
        """
        query = self.session.query(CallLog)
        if candidate_id:
            query = query.filter_by(candidate_id=candidate_id)
        return query.order_by(CallLog.created_at.desc()).limit(limit).all()
    
    def close(self):
        """Close database session."""
        self.session.close()
