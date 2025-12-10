#!/usr/bin/env python3
"""
Example usage of Naukri Scraper
This script demonstrates various ways to use the scraper
"""

from naukri_scraper import NaukriScraper
import time


def example_basic_search():
    """
    Example 1: Basic job search
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Job Search")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search for Python developer jobs
    jobs = scraper.search_jobs(
        keyword="python developer",
        location="",
        max_pages=1
    )
    
    print(f"\nFound {len(jobs)} jobs")
    
    # Display first 3 jobs
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n{i}. {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Experience: {job.get('experience', 'N/A')}")
    
    return scraper


def example_filtered_search():
    """
    Example 2: Search with filters
    """
    print("\n" + "=" * 60)
    print("Example 2: Filtered Search")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search for data scientist jobs in specific location
    jobs = scraper.search_jobs(
        keyword="data scientist",
        location="bangalore",
        max_pages=2
    )
    
    print(f"\nInitial results: {len(jobs)} jobs")
    
    # Filter by experience
    filtered = scraper.filter_jobs(
        min_experience=3,
        max_experience=7
    )
    
    print(f"After filtering (3-7 years exp): {len(filtered)} jobs")
    
    return scraper


def example_save_results():
    """
    Example 3: Save results to files
    """
    print("\n" + "=" * 60)
    print("Example 3: Save Results")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search for Java developer jobs
    jobs = scraper.search_jobs(
        keyword="java developer",
        location="mumbai",
        max_pages=1
    )
    
    if jobs:
        # Save to CSV
        scraper.save_to_csv("example_jobs.csv")
        
        # Save to JSON
        scraper.save_to_json("example_jobs.json")
        
        print("\nResults saved to example_jobs.csv and example_jobs.json")
    else:
        print("\nNo jobs found to save")
    
    return scraper


def example_company_filter():
    """
    Example 4: Filter by company names
    """
    print("\n" + "=" * 60)
    print("Example 4: Company Filter")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search for software engineer jobs
    jobs = scraper.search_jobs(
        keyword="software engineer",
        max_pages=2
    )
    
    print(f"\nTotal jobs found: {len(jobs)}")
    
    # Filter by specific companies (partial match)
    target_companies = ["Google", "Microsoft", "Amazon", "TCS", "Infosys"]
    filtered = scraper.filter_jobs(companies=target_companies)
    
    print(f"Jobs from target companies: {len(filtered)}")
    
    # Show companies found
    companies_found = set(job.get('company', 'N/A') for job in filtered)
    print(f"\nCompanies found: {', '.join(sorted(companies_found)[:10])}")
    
    return scraper


def example_location_filter():
    """
    Example 5: Filter by multiple locations
    """
    print("\n" + "=" * 60)
    print("Example 5: Location Filter")
    print("=" * 60)
    
    scraper = NaukriScraper(delay=2.0)
    
    # Search for analyst jobs
    jobs = scraper.search_jobs(
        keyword="business analyst",
        max_pages=2
    )
    
    print(f"\nTotal jobs found: {len(jobs)}")
    
    # Filter by metro cities
    metro_cities = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune"]
    filtered = scraper.filter_jobs(locations=metro_cities)
    
    print(f"Jobs in metro cities: {len(filtered)}")
    
    # Show location distribution
    location_count = {}
    for job in filtered:
        loc = job.get('location', 'Unknown')
        location_count[loc] = location_count.get(loc, 0) + 1
    
    print("\nTop locations:")
    for loc, count in sorted(location_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {loc}: {count} jobs")
    
    return scraper


def main():
    """
    Run all examples
    """
    print("=" * 60)
    print("Naukri Scraper - Example Usage")
    print("=" * 60)
    print("\nThis script demonstrates various features of the scraper")
    print("Note: This will make multiple requests to Naukri.com")
    
    try:
        # Run examples
        example_basic_search()
        time.sleep(2)
        
        example_filtered_search()
        time.sleep(2)
        
        example_save_results()
        time.sleep(2)
        
        example_company_filter()
        time.sleep(2)
        
        example_location_filter()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
