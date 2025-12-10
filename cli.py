#!/usr/bin/env python3
"""
Command-line interface for Naukri Scraper
"""

import argparse
import sys
from naukri_scraper import NaukriScraper


def main():
    """
    Main CLI function
    """
    parser = argparse.ArgumentParser(
        description='Naukri.com Job Scraper - Extract job listings from Naukri.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Search for Python developer jobs
  python cli.py --keyword "python developer" --pages 2
  
  # Search with location filter
  python cli.py --keyword "data scientist" --location "bangalore" --pages 3
  
  # Save to specific file
  python cli.py --keyword "java developer" --output jobs.csv --format csv
  
  # Filter by experience
  python cli.py --keyword "software engineer" --min-exp 2 --max-exp 5
        '''
    )
    
    # Required arguments
    parser.add_argument(
        '--keyword', '-k',
        type=str,
        required=True,
        help='Job search keyword (e.g., "python developer", "data scientist")'
    )
    
    # Optional search parameters
    parser.add_argument(
        '--location', '-l',
        type=str,
        default='',
        help='Location filter (e.g., "bangalore", "mumbai")'
    )
    
    parser.add_argument(
        '--pages', '-p',
        type=int,
        default=1,
        help='Number of pages to scrape (default: 1)'
    )
    
    # Experience filters
    parser.add_argument(
        '--min-exp',
        type=int,
        help='Minimum years of experience'
    )
    
    parser.add_argument(
        '--max-exp',
        type=int,
        help='Maximum years of experience'
    )
    
    # Company filter
    parser.add_argument(
        '--companies',
        type=str,
        nargs='+',
        help='Filter by company names'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='naukri_jobs',
        help='Output filename (without extension, default: naukri_jobs)'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['csv', 'json', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    
    # Rate limiting
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    
    # Verbose mode
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.min_exp is not None and args.max_exp is not None:
        if args.min_exp > args.max_exp:
            print("Error: min-exp cannot be greater than max-exp")
            sys.exit(1)
    
    if args.pages < 1:
        print("Error: pages must be at least 1")
        sys.exit(1)
    
    # Create scraper instance
    print("=" * 60)
    print("Naukri.com Job Scraper")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=args.delay)
    
    # Search for jobs
    try:
        jobs = scraper.search_jobs(
            keyword=args.keyword,
            location=args.location,
            max_pages=args.pages
        )
        
        if not jobs:
            print("\nNo jobs found matching your criteria.")
            return
        
        # Apply filters if specified
        if args.min_exp or args.max_exp or args.companies:
            print("\nApplying filters...")
            original_count = len(jobs)
            scraper.jobs = scraper.filter_jobs(
                min_experience=args.min_exp,
                max_experience=args.max_exp,
                companies=args.companies
            )
            print(f"Filtered: {original_count} -> {len(scraper.jobs)} jobs")
        
        # Display summary
        print("\n" + "=" * 60)
        print(f"SUMMARY: Found {len(scraper.jobs)} jobs")
        print("=" * 60)
        
        if args.verbose and scraper.jobs:
            print("\nFirst 5 jobs:")
            for i, job in enumerate(scraper.jobs[:5], 1):
                print(f"\n{i}. {job.get('title', 'N/A')}")
                print(f"   Company: {job.get('company', 'N/A')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Experience: {job.get('experience', 'N/A')}")
                print(f"   Salary: {job.get('salary', 'N/A')}")
        
        # Save results
        print("\nSaving results...")
        if args.format in ['csv', 'both']:
            csv_filename = f"{args.output}.csv"
            scraper.save_to_csv(csv_filename)
        
        if args.format in ['json', 'both']:
            json_filename = f"{args.output}.json"
            scraper.save_to_json(json_filename)
        
        print("\n" + "=" * 60)
        print("Scraping completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
