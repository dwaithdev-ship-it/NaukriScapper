"""Command-line interface for NaukriScapper."""
import argparse
import sys
from naukri_scraper import NaukriScraper
from data_manager import DataManager
from ai_integration import AIIntegration
from api import run_api


def scrape_command(args):
    """Execute scrape command."""
    scraper = NaukriScraper(delay=args.delay)
    data_manager = DataManager()
    
    print(f"Searching for: {args.keyword}")
    if args.location:
        print(f"Location: {args.location}")
    if args.experience:
        print(f"Experience: {args.experience}")
    
    # Create job search record
    job_search = data_manager.create_job_search(
        query=args.keyword,
        location=args.location,
        experience=args.experience,
        salary=args.salary
    )
    
    print(f"\nScraping up to {args.max_pages} page(s)...")
    jobs = scraper.search_jobs(
        keyword=args.keyword,
        location=args.location,
        experience=args.experience,
        salary=args.salary,
        max_pages=args.max_pages
    )
    
    print(f"\nFound {len(jobs)} jobs")
    
    # Update job search
    data_manager.update_job_search(
        search_id=job_search.id,
        results_count=len(jobs),
        status='completed'
    )
    
    # Apply filters if specified
    if args.min_experience or args.max_experience or args.skills or args.filter_location:
        print("\nApplying filters...")
        skills_list = args.skills.split(',') if args.skills else None
        jobs = scraper.filter_jobs(
            min_experience=args.min_experience,
            max_experience=args.max_experience,
            required_skills=skills_list,
            location=args.filter_location
        )
        print(f"After filtering: {len(jobs)} jobs")
    
    # Export if requested
    if args.export_csv:
        filepath = scraper.export_to_csv(args.export_csv, jobs)
        print(f"\nExported to CSV: {filepath}")
    
    if args.export_json:
        filepath = scraper.export_to_json(args.export_json, jobs)
        print(f"\nExported to JSON: {filepath}")
    
    # Display results
    if not args.quiet and jobs:
        print("\n" + "="*80)
        print("Job Listings:")
        print("="*80)
        for i, job in enumerate(jobs[:args.limit], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   Company: {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Experience: {job.get('experience', 'N/A')}")
            print(f"   Salary: {job.get('salary', 'N/A')}")
            if job.get('url'):
                print(f"   URL: {job.get('url')}")
    
    data_manager.close()


def list_command(args):
    """Execute list command."""
    data_manager = DataManager()
    
    if args.type == 'searches':
        searches = data_manager.list_job_searches(limit=args.limit)
        print(f"\nJob Searches ({len(searches)}):")
        print("="*80)
        for search in searches:
            print(f"\nID: {search.id}")
            print(f"Query: {search.query}")
            print(f"Location: {search.location or 'N/A'}")
            print(f"Results: {search.results_count}")
            print(f"Status: {search.status}")
            print(f"Created: {search.created_at}")
    
    elif args.type == 'candidates':
        candidates = data_manager.list_candidates(limit=args.limit)
        print(f"\nCandidates ({len(candidates)}):")
        print("="*80)
        for candidate in candidates:
            print(f"\nID: {candidate.id}")
            print(f"Name: {candidate.name}")
            print(f"Email: {candidate.email or 'N/A'}")
            print(f"Experience: {candidate.experience or 'N/A'} years")
            print(f"Location: {candidate.location or 'N/A'}")
            print(f"Skills: {candidate.skills or 'N/A'}")
    
    elif args.type == 'call-logs':
        logs = data_manager.list_call_logs(limit=args.limit)
        print(f"\nCall Logs ({len(logs)}):")
        print("="*80)
        for log in logs:
            print(f"\nID: {log.id}")
            print(f"Candidate ID: {log.candidate_id}")
            print(f"Status: {log.call_status}")
            print(f"Duration: {log.duration}s")
            print(f"Success: {log.success}")
            print(f"Created: {log.created_at}")
    
    data_manager.close()


def api_command(args):
    """Execute API server command."""
    print(f"Starting API server on {args.host}:{args.port}")
    print("Press Ctrl+C to stop\n")
    
    from config import Config
    Config.API_HOST = args.host
    Config.API_PORT = args.port
    Config.API_DEBUG = args.debug
    
    run_api()


def webhook_command(args):
    """Execute webhook command."""
    ai_integration = AIIntegration()
    
    if args.action == 'send':
        if not args.candidate_id:
            print("Error: candidate_id is required for send action")
            sys.exit(1)
        
        print(f"Sending candidate {args.candidate_id} data to {args.webhook_type} webhook...")
        result = ai_integration.send_candidate_data(args.candidate_id, args.webhook_type)
        
        if result.get('success'):
            print("✓ Successfully sent data to webhook")
            print(f"Status: {result.get('status_code')}")
        else:
            print("✗ Failed to send data to webhook")
            print(f"Error: {result.get('error')}")
    
    elif args.action == 'config':
        config = ai_integration.get_webhook_config()
        print("\nWebhook Configuration:")
        print("="*80)
        for key, value in config.items():
            print(f"{key}: {value if value else 'Not configured'}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='NaukriScapper - Web scraping utility for Naukri.com'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape jobs from Naukri.com')
    scrape_parser.add_argument('keyword', help='Job keyword to search')
    scrape_parser.add_argument('--location', help='Job location')
    scrape_parser.add_argument('--experience', help='Experience level (e.g., "2-5")')
    scrape_parser.add_argument('--salary', help='Salary range')
    scrape_parser.add_argument('--max-pages', type=int, default=1, help='Maximum pages to scrape')
    scrape_parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    scrape_parser.add_argument('--min-experience', type=float, help='Minimum experience filter')
    scrape_parser.add_argument('--max-experience', type=float, help='Maximum experience filter')
    scrape_parser.add_argument('--skills', help='Required skills (comma-separated)')
    scrape_parser.add_argument('--filter-location', help='Filter by location')
    scrape_parser.add_argument('--export-csv', help='Export to CSV file')
    scrape_parser.add_argument('--export-json', help='Export to JSON file')
    scrape_parser.add_argument('--limit', type=int, default=10, help='Limit displayed results')
    scrape_parser.add_argument('--quiet', action='store_true', help='Suppress output')
    scrape_parser.set_defaults(func=scrape_command)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List records from database')
    list_parser.add_argument('type', choices=['searches', 'candidates', 'call-logs'], 
                            help='Type of records to list')
    list_parser.add_argument('--limit', type=int, default=10, help='Maximum records to display')
    list_parser.set_defaults(func=list_command)
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start REST API server')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    api_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    api_parser.set_defaults(func=api_command)
    
    # Webhook command
    webhook_parser = subparsers.add_parser('webhook', help='Webhook operations')
    webhook_parser.add_argument('action', choices=['send', 'config'], help='Webhook action')
    webhook_parser.add_argument('--candidate-id', type=int, help='Candidate ID (for send action)')
    webhook_parser.add_argument('--webhook-type', default='custom', 
                               choices=['n8n', 'make', 'custom'], 
                               help='Webhook type')
    webhook_parser.set_defaults(func=webhook_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
