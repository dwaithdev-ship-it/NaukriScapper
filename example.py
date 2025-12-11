"""Example usage of NaukriScapper."""
from naukri_scraper import NaukriScraper
from data_manager import DataManager
from ai_integration import AIIntegration


def basic_scraping_example():
    """Basic job scraping example."""
    print("="*80)
    print("Basic Scraping Example")
    print("="*80)
    
    # Initialize scraper
    scraper = NaukriScraper(delay=2.0)
    
    # Search for Python developer jobs in Bangalore
    jobs = scraper.search_jobs(
        keyword='Python developer',
        location='Bangalore',
        max_pages=1
    )
    
    print(f"\nFound {len(jobs)} jobs")
    
    # Display first 3 jobs
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n{i}. {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")


def filtering_example():
    """Job filtering example."""
    print("\n" + "="*80)
    print("Filtering Example")
    print("="*80)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search jobs
    scraper.search_jobs(keyword='Developer', max_pages=1)
    
    # Filter by experience and skills
    filtered = scraper.filter_jobs(
        min_experience=2,
        max_experience=5,
        required_skills=['Python', 'Django']
    )
    
    print(f"\nFiltered jobs: {len(filtered)}")


def export_example():
    """Export jobs example."""
    print("\n" + "="*80)
    print("Export Example")
    print("="*80)
    
    scraper = NaukriScraper()
    scraper.search_jobs(keyword='Python', max_pages=1)
    
    # Export to CSV
    csv_file = scraper.export_to_csv('jobs.csv')
    print(f"\nExported to CSV: {csv_file}")
    
    # Export to JSON
    json_file = scraper.export_to_json('jobs.json')
    print(f"Exported to JSON: {json_file}")


def database_example():
    """Database operations example."""
    print("\n" + "="*80)
    print("Database Example")
    print("="*80)
    
    data_manager = DataManager()
    
    # Create job search
    search = data_manager.create_job_search(
        query='Python developer',
        location='Bangalore',
        experience='2-5'
    )
    print(f"\nCreated job search: ID {search.id}")
    
    # Create candidate
    candidate = data_manager.create_candidate(
        name='John Doe',
        email='john@example.com',
        experience=3.5,
        skills='Python, Django, REST APIs',
        location='Bangalore'
    )
    print(f"Created candidate: ID {candidate.id}")
    
    # List all candidates
    candidates = data_manager.list_candidates(limit=5)
    print(f"\nTotal candidates: {len(candidates)}")
    
    data_manager.close()


def webhook_example():
    """Webhook integration example."""
    print("\n" + "="*80)
    print("Webhook Integration Example")
    print("="*80)
    
    ai_integration = AIIntegration()
    
    # Get webhook configuration
    config = ai_integration.get_webhook_config()
    print("\nWebhook Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value if value else 'Not configured'}")
    
    # Example: Send candidate data to webhook
    # Uncomment when you have a candidate and webhook configured
    # result = ai_integration.send_candidate_data(candidate_id=1, webhook_type='custom')
    # print(f"\nWebhook result: {result}")


def main():
    """Run all examples."""
    print("\nNaukriScapper Examples")
    print("=" * 80)
    print("\nNote: These examples demonstrate the API.")
    print("Actual scraping requires valid Naukri.com access.\n")
    
    try:
        basic_scraping_example()
        filtering_example()
        export_example()
        database_example()
        webhook_example()
        
        print("\n" + "="*80)
        print("Examples completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: Some examples may fail without proper configuration or network access.")


if __name__ == '__main__':
    main()
