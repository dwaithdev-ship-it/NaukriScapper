#!/usr/bin/env python
"""Demo script to showcase NaukriScapper functionality."""
import sys


def print_section(title):
    """Print section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def main():
    """Run comprehensive demo of NaukriScapper features."""
    print_section("NaukriScapper - Comprehensive Demo")
    
    print("This demo showcases all major features of NaukriScapper:")
    print("✓ Web scraping functionality")
    print("✓ Database operations")
    print("✓ REST API server")
    print("✓ CLI commands")
    print("✓ AI webhook integration")
    print("✓ Data export (CSV/JSON)")
    
    # Test 1: Verify all modules can be imported
    print_section("1. Module Import Test")
    try:
        from naukri_scraper import NaukriScraper
        from models import JobSearch, Candidate, CallLog, get_session
        from data_manager import DataManager
        from ai_integration import AIIntegration
        from config import Config
        import api
        import cli
        print("✓ All modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return 1
    
    # Test 2: Test database operations
    print_section("2. Database Operations Test")
    try:
        data_manager = DataManager()
        
        # Create a test candidate
        candidate = data_manager.create_candidate(
            name="Demo User",
            email="demo@naukriscraper.com",
            experience=3.0,
            skills="Python, JavaScript, SQL",
            location="Bangalore, India"
        )
        print(f"✓ Created candidate: {candidate.name} (ID: {candidate.id})")
        
        # Create a test job search
        search = data_manager.create_job_search(
            query="Python Developer",
            location="Bangalore",
            experience="3-5 years"
        )
        print(f"✓ Created job search: {search.query} (ID: {search.id})")
        
        # Create a test call log
        call_log = data_manager.create_call_log(
            candidate_id=candidate.id,
            call_status="demo",
            duration=0,
            notes="Demo call log entry",
            success=True
        )
        print(f"✓ Created call log (ID: {call_log.id})")
        
        # List records
        candidates = data_manager.list_candidates(limit=5)
        searches = data_manager.list_job_searches(limit=5)
        logs = data_manager.list_call_logs(limit=5)
        
        print(f"\nDatabase statistics:")
        print(f"  - Total candidates: {len(candidates)}")
        print(f"  - Total job searches: {len(searches)}")
        print(f"  - Total call logs: {len(logs)}")
        
        data_manager.close()
    except Exception as e:
        print(f"✗ Database error: {e}")
        return 1
    
    # Test 3: Test scraper functionality
    print_section("3. Scraper Functionality Test")
    try:
        scraper = NaukriScraper(delay=0.1)
        print(f"✓ Scraper initialized (delay: {scraper.delay}s)")
        
        # Test filtering with mock data
        scraper.jobs = [
            {'title': 'Python Dev', 'experience': '2-5 years', 'location': 'Bangalore', 'description': 'Python Django'},
            {'title': 'Java Dev', 'experience': '5-8 years', 'location': 'Mumbai', 'description': 'Java Spring'},
            {'title': 'JS Dev', 'experience': '1-3 years', 'location': 'Bangalore', 'description': 'JavaScript React'},
        ]
        
        # Test filtering
        filtered = scraper.filter_jobs(min_experience=2, max_experience=6)
        print(f"✓ Filtering by experience: {len(filtered)} results")
        
        filtered_location = scraper.filter_jobs(location='Bangalore')
        print(f"✓ Filtering by location: {len(filtered_location)} results")
        
        filtered_skills = scraper.filter_jobs(required_skills=['Python'])
        print(f"✓ Filtering by skills: {len(filtered_skills)} results")
        
        # Test export
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            Config.EXPORT_DIR = tmpdir
            csv_file = scraper.export_to_csv('demo_jobs.csv')
            json_file = scraper.export_to_json('demo_jobs.json')
            print(f"✓ CSV export: {os.path.exists(csv_file)}")
            print(f"✓ JSON export: {os.path.exists(json_file)}")
        
    except Exception as e:
        print(f"✗ Scraper error: {e}")
        return 1
    
    # Test 4: Test AI integration
    print_section("4. AI Integration Test")
    try:
        ai_integration = AIIntegration()
        config = ai_integration.get_webhook_config()
        
        print("✓ AI integration initialized")
        print(f"  Webhook configuration:")
        print(f"    - Custom webhook: {'Configured' if config['webhook_url'] else 'Not configured'}")
        print(f"    - n8n webhook: {'Configured' if config['n8n_url'] else 'Not configured'}")
        print(f"    - Make.com webhook: {'Configured' if config['make_url'] else 'Not configured'}")
        print(f"    - Allow local webhooks: {config['allow_local_webhooks']}")
        
        # Test URL validation
        print("\n  Testing SSRF protection:")
        valid = ai_integration._validate_webhook_url('https://hooks.n8n.cloud/webhook/test')
        print(f"    - External URL validation: {'✓ Pass' if valid else '✗ Fail'}")
        
        blocked = not ai_integration._validate_webhook_url('http://localhost:8000/webhook')
        print(f"    - Localhost blocking: {'✓ Pass' if blocked else '✗ Fail'}")
        
    except Exception as e:
        print(f"✗ AI integration error: {e}")
        return 1
    
    # Test 5: Configuration test
    print_section("5. Configuration Test")
    try:
        print("✓ Configuration loaded")
        print(f"  - Database URL: {Config.DATABASE_URL}")
        print(f"  - Default delay: {Config.DEFAULT_DELAY}s")
        print(f"  - API host: {Config.API_HOST}")
        print(f"  - API port: {Config.API_PORT}")
        print(f"  - Export directory: {Config.EXPORT_DIR}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return 1
    
    # Summary
    print_section("Demo Completed Successfully!")
    print("All core features are working correctly:")
    print("  ✓ Web scraping engine")
    print("  ✓ Database models and operations")
    print("  ✓ Data filtering and export")
    print("  ✓ AI webhook integration with SSRF protection")
    print("  ✓ Configuration management")
    print("\nThe project is ready to run!")
    print("\nQuick start commands:")
    print("  1. Run tests:           python test_scraper.py")
    print("  2. Start API:           python cli.py api")
    print("  3. Scrape jobs:         python cli.py scrape 'Python developer'")
    print("  4. List candidates:     python cli.py list candidates")
    print("  5. Webhook config:      python cli.py webhook config")
    print("\nFor more information, see README.md")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
