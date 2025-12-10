"""Example usage of Naukri Scraper."""
import os
from dotenv import load_dotenv

from naukri_scraper import NaukriEmployerScraper
from data_manager import DataManager
from ai_integration import AIIntegration
from models import init_db

# Load environment variables
load_dotenv()


def example_basic_search():
    """Example: Basic candidate search and storage."""
    print("=== Example: Basic Search ===\n")
    
    # Get credentials from environment
    username = os.getenv('NAUKRI_USERNAME')
    password = os.getenv('NAUKRI_PASSWORD')
    
    if not username or not password:
        print("Please set NAUKRI_USERNAME and NAUKRI_PASSWORD in .env file")
        return
    
    # Initialize database
    init_db()
    
    # Create data manager
    dm = DataManager()
    
    # Create job search
    job_search = dm.create_job_search(
        job_role="Python Developer",
        experience_min=2.0,
        experience_max=5.0,
        location="Bangalore",
        job_type="Full-time"
    )
    print(f"Created job search: {job_search.id}")
    
    # Initialize scraper
    with NaukriEmployerScraper(username, password) as scraper:
        print("Logging in...")
        if not scraper.login():
            print("Login failed!")
            return
        
        print("Login successful!")
        
        # Search candidates
        print("Searching for candidates...")
        candidates = scraper.search_candidates(
            job_role="Python Developer",
            experience_min=2,
            experience_max=5,
            location="Bangalore",
            max_results=20
        )
        
        print(f"Found {len(candidates)} candidates")
        
        if candidates:
            # Save to database
            dm.add_candidates_bulk(job_search.id, candidates)
            print(f"Saved {len(candidates)} candidates to database")
            
            # Export to Excel
            excel_file = dm.export_to_excel(job_search.id)
            print(f"Exported to: {excel_file}")
    
    dm.close()


def example_with_sample_data():
    """Example: Working with sample data (no actual scraping)."""
    print("\n=== Example: Sample Data ===\n")
    
    # Initialize database
    init_db()
    
    # Create data manager
    dm = DataManager()
    
    # Create job search
    job_search = dm.create_job_search(
        job_role="Full Stack Developer",
        experience_min=3.0,
        experience_max=7.0,
        location="Mumbai",
        job_type="Full-time"
    )
    print(f"Created job search: {job_search.id}")
    
    # Sample candidate data
    sample_candidates = [
        {
            'name': 'Rajesh Kumar',
            'email': 'rajesh.kumar@example.com',
            'phone': '+91-9876543210',
            'current_location': 'Mumbai',
            'experience_years': 4.5,
            'current_company': 'Tech Solutions Ltd',
            'current_designation': 'Senior Software Engineer',
            'skills': 'React, Node.js, MongoDB, Docker, AWS',
            'education': 'B.Tech in Computer Science',
            'notice_period': '30 days',
            'current_salary': '12 LPA',
            'expected_salary': '15 LPA'
        },
        {
            'name': 'Priya Sharma',
            'email': 'priya.sharma@example.com',
            'phone': '+91-9876543211',
            'current_location': 'Mumbai',
            'experience_years': 5.0,
            'current_company': 'Digital Innovations',
            'current_designation': 'Tech Lead',
            'skills': 'Python, Django, React, PostgreSQL, Kubernetes',
            'education': 'M.Tech in Computer Science',
            'notice_period': '60 days',
            'current_salary': '18 LPA',
            'expected_salary': '22 LPA'
        },
        {
            'name': 'Amit Patel',
            'email': 'amit.patel@example.com',
            'phone': '+91-9876543212',
            'current_location': 'Mumbai',
            'experience_years': 3.5,
            'current_company': 'StartupXYZ',
            'current_designation': 'Full Stack Developer',
            'skills': 'Angular, Node.js, MySQL, Redis',
            'education': 'B.E. in Information Technology',
            'notice_period': '15 days',
            'current_salary': '10 LPA',
            'expected_salary': '13 LPA'
        }
    ]
    
    # Add candidates
    candidates = dm.add_candidates_bulk(job_search.id, sample_candidates)
    print(f"Added {len(candidates)} sample candidates")
    
    # List all candidates
    print("\nCandidates:")
    for c in candidates:
        print(f"  - {c.name} ({c.experience_years}y, {c.current_company})")
    
    # Update status for first candidate
    if candidates:
        dm.update_candidate_status(
            candidate_id=candidates[0].id,
            contacted=True,
            interested=True,
            comments="Very interested in the role, available for interview next week"
        )
        print(f"\nUpdated status for {candidates[0].name}")
    
    # Get statistics
    stats = dm.get_statistics(job_search.id)
    print(f"\nStatistics:")
    print(f"  Total: {stats['total_candidates']}")
    print(f"  Contacted: {stats['contacted']}")
    print(f"  Interested: {stats['interested']}")
    
    # Export to Excel
    excel_file = dm.export_to_excel(job_search.id)
    print(f"\nExported to: {excel_file}")
    
    dm.close()


def example_ai_integration():
    """Example: AI integration for automated calls."""
    print("\n=== Example: AI Integration ===\n")
    
    # Initialize database
    init_db()
    
    # Create sample data
    dm = DataManager()
    job_search = dm.create_job_search(
        job_role="DevOps Engineer",
        experience_min=2.0,
        experience_max=5.0,
        location="Pune"
    )
    
    sample_candidate = {
        'name': 'Suresh Reddy',
        'email': 'suresh.reddy@example.com',
        'phone': '+91-9876543213',
        'current_location': 'Pune',
        'experience_years': 3.0,
        'current_company': 'Cloud Services Inc',
        'current_designation': 'DevOps Engineer',
        'skills': 'Docker, Kubernetes, Jenkins, AWS, Terraform'
    }
    
    candidate = dm.add_candidate(job_search.id, sample_candidate)
    print(f"Added candidate: {candidate.name}")
    
    # Initialize AI integration
    ai = AIIntegration()
    
    # Prepare candidate and job data
    candidate_data = {
        'name': candidate.name,
        'phone': candidate.phone,
        'experience_years': candidate.experience_years
    }
    
    job_data = {
        'job_role': 'DevOps Engineer',
        'location': 'Pune',
        'company_name': 'Tech Innovations Ltd'
    }
    
    # Format call script
    script = ai.format_call_script(candidate_data, job_data)
    print(f"\nCall Script:")
    print(script)
    
    # Note: Actual webhook calls require configured URLs
    print("\nTo trigger actual calls, configure N8N_WEBHOOK_URL or MAKE_WEBHOOK_URL in .env")
    
    # Simulate webhook response
    webhook_data = {
        'candidate_id': candidate.id,
        'call_status': 'completed',
        'interested': True,
        'response': 'Candidate is very interested in the position',
        'ai_tool': 'n8n'
    }
    
    result = ai.process_webhook_response(webhook_data)
    print(f"\nProcessed webhook response: {result}")
    
    # Check updated status
    dm.session.refresh(candidate)
    print(f"Candidate contacted: {candidate.contacted}")
    print(f"Candidate interested: {candidate.interested}")
    
    dm.close()


def example_api_usage():
    """Example: Using the REST API programmatically."""
    print("\n=== Example: API Usage ===\n")
    print("To use the REST API:")
    print("1. Start the API server:")
    print("   python api.py")
    print("\n2. Make requests using curl or any HTTP client:")
    print("\nCreate job search:")
    print("""
curl -X POST http://localhost:5000/api/job-search \\
  -H "Content-Type: application/json" \\
  -d '{
    "job_role": "Python Developer",
    "experience_min": 2,
    "experience_max": 5,
    "location": "Bangalore"
  }'
""")
    
    print("\nGet candidates:")
    print("curl http://localhost:5000/api/candidates/1")
    
    print("\nExport to Excel:")
    print("curl http://localhost:5000/api/export/1 --output candidates.xlsx")


if __name__ == '__main__':
    print("Naukri Scraper - Example Usage\n")
    print("=" * 50)
    
    # Run examples
    # Uncomment the example you want to run
    
    # example_basic_search()  # Requires actual Naukri credentials
    example_with_sample_data()  # Works without credentials
    example_ai_integration()    # Demonstrates AI integration
    example_api_usage()         # Shows API usage
    
    print("\n" + "=" * 50)
    print("Examples completed!")
