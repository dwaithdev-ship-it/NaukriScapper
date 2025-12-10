"""
Naukri.com Job Scraper
A utility to scrape job listings from Naukri.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus


class NaukriScraper:
    """
    A scraper class for extracting job listings from Naukri.com
    """
    
    BASE_URL = "https://www.naukri.com"
    SEARCH_URL = f"{BASE_URL}/{{keyword}}-jobs"
    
    def __init__(self, delay: float = 2.0):
        """
        Initialize the scraper
        
        Args:
            delay: Delay between requests in seconds (for rate limiting)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.jobs = []
    
    def search_jobs(self, 
                   keyword: str, 
                   location: str = "", 
                   experience: str = "",
                   max_pages: int = 1) -> List[Dict]:
        """
        Search for jobs on Naukri.com
        
        Args:
            keyword: Job search keyword (e.g., "python developer")
            location: Location filter (e.g., "bangalore")
            experience: Experience filter (e.g., "2", "5")
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        print(f"Searching for '{keyword}' jobs...")
        
        # Build search URL
        search_keyword = keyword.replace(" ", "-")
        if location:
            location_param = location.replace(" ", "-")
            search_keyword = f"{search_keyword}-in-{location_param}"
        
        self.jobs = []
        
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}/{max_pages}...")
            
            url = self.SEARCH_URL.format(keyword=search_keyword)
            if page > 1:
                url = f"{url}-{page}"
            
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = self._parse_job_listings(soup)
                
                if not job_listings:
                    print(f"No more jobs found on page {page}")
                    break
                
                self.jobs.extend(job_listings)
                print(f"Found {len(job_listings)} jobs on page {page}")
                
                # Rate limiting
                if page < max_pages:
                    time.sleep(self.delay)
                    
            except requests.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        print(f"Total jobs scraped: {len(self.jobs)}")
        return self.jobs
    
    def _parse_job_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse job listings from the page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Try different selectors as Naukri's structure may vary
        job_containers = soup.find_all('article', class_=re.compile('jobTuple'))
        
        if not job_containers:
            job_containers = soup.find_all('div', class_=re.compile('job'))
        
        for container in job_containers:
            try:
                job_data = self._extract_job_data(container)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                print(f"Error parsing job listing: {e}")
                continue
        
        return jobs
    
    def _extract_job_data(self, container) -> Optional[Dict]:
        """
        Extract job data from a job container
        
        Args:
            container: BeautifulSoup element containing job data
            
        Returns:
            Dictionary with job data or None
        """
        job_data = {}
        
        # Job Title
        title_elem = container.find('a', class_=re.compile('title'))
        if not title_elem:
            title_elem = container.find('a', attrs={'title': True})
        
        if title_elem:
            job_data['title'] = title_elem.get_text(strip=True)
            job_data['link'] = title_elem.get('href', '')
            if job_data['link'] and not job_data['link'].startswith('http'):
                job_data['link'] = self.BASE_URL + job_data['link']
        else:
            return None
        
        # Company Name
        company_elem = container.find('a', class_=re.compile('company'))
        if not company_elem:
            company_elem = container.find('div', class_=re.compile('company'))
        if company_elem:
            job_data['company'] = company_elem.get_text(strip=True)
        else:
            job_data['company'] = 'N/A'
        
        # Experience
        exp_elem = container.find('span', class_=re.compile('experience'))
        if not exp_elem:
            exp_elem = container.find('li', class_=re.compile('experience'))
        if exp_elem:
            job_data['experience'] = exp_elem.get_text(strip=True)
        else:
            job_data['experience'] = 'N/A'
        
        # Salary
        salary_elem = container.find('span', class_=re.compile('salary'))
        if not salary_elem:
            salary_elem = container.find('li', class_=re.compile('salary'))
        if salary_elem:
            job_data['salary'] = salary_elem.get_text(strip=True)
        else:
            job_data['salary'] = 'Not disclosed'
        
        # Location
        location_elem = container.find('span', class_=re.compile('location'))
        if not location_elem:
            location_elem = container.find('li', class_=re.compile('location'))
        if location_elem:
            job_data['location'] = location_elem.get_text(strip=True)
        else:
            job_data['location'] = 'N/A'
        
        # Job Description/Skills
        desc_elem = container.find('div', class_=re.compile('job-description'))
        if not desc_elem:
            desc_elem = container.find('ul', class_=re.compile('tags'))
        if desc_elem:
            job_data['description'] = desc_elem.get_text(strip=True)
        else:
            job_data['description'] = 'N/A'
        
        # Posted Date
        date_elem = container.find('span', class_=re.compile('date'))
        if date_elem:
            job_data['posted_date'] = date_elem.get_text(strip=True)
        else:
            job_data['posted_date'] = 'N/A'
        
        return job_data
    
    def save_to_csv(self, filename: str = "naukri_jobs.csv"):
        """
        Save scraped jobs to a CSV file
        
        Args:
            filename: Output filename
        """
        if not self.jobs:
            print("No jobs to save!")
            return
        
        df = pd.DataFrame(self.jobs)
        df.to_csv(filename, index=False)
        print(f"Saved {len(self.jobs)} jobs to {filename}")
    
    def save_to_json(self, filename: str = "naukri_jobs.json"):
        """
        Save scraped jobs to a JSON file
        
        Args:
            filename: Output filename
        """
        if not self.jobs:
            print("No jobs to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.jobs)} jobs to {filename}")
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed information about a specific job
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        try:
            response = self.session.get(job_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': job_url,
                'full_description': '',
                'key_skills': [],
                'role': '',
                'industry_type': '',
                'functional_area': '',
                'employment_type': '',
                'role_category': ''
            }
            
            # Full job description
            desc_div = soup.find('div', class_=re.compile('job-description'))
            if desc_div:
                details['full_description'] = desc_div.get_text(strip=True)
            
            # Key skills
            skills_section = soup.find('div', class_=re.compile('key-skill'))
            if skills_section:
                skill_tags = skills_section.find_all('a')
                details['key_skills'] = [tag.get_text(strip=True) for tag in skill_tags]
            
            time.sleep(self.delay)
            return details
            
        except Exception as e:
            print(f"Error fetching job details: {e}")
            return {}
    
    def filter_jobs(self, 
                   min_experience: Optional[int] = None,
                   max_experience: Optional[int] = None,
                   locations: Optional[List[str]] = None,
                   companies: Optional[List[str]] = None) -> List[Dict]:
        """
        Filter scraped jobs based on criteria
        
        Args:
            min_experience: Minimum years of experience
            max_experience: Maximum years of experience
            locations: List of locations to filter by
            companies: List of companies to filter by
            
        Returns:
            Filtered list of jobs
        """
        filtered = self.jobs.copy()
        
        if min_experience is not None or max_experience is not None:
            filtered = [job for job in filtered 
                       if self._check_experience(job.get('experience', ''), 
                                                min_experience, max_experience)]
        
        if locations:
            locations_lower = [loc.lower() for loc in locations]
            filtered = [job for job in filtered 
                       if any(loc in job.get('location', '').lower() 
                             for loc in locations_lower)]
        
        if companies:
            companies_lower = [comp.lower() for comp in companies]
            filtered = [job for job in filtered 
                       if any(comp in job.get('company', '').lower() 
                             for comp in companies_lower)]
        
        return filtered
    
    def _check_experience(self, exp_str: str, min_exp: Optional[int], max_exp: Optional[int]) -> bool:
        """
        Check if experience string matches criteria
        
        Args:
            exp_str: Experience string from job listing
            min_exp: Minimum experience
            max_exp: Maximum experience
            
        Returns:
            True if matches criteria
        """
        # Extract numbers from experience string
        numbers = re.findall(r'\d+', exp_str)
        if not numbers:
            return True  # Include if can't parse
        
        try:
            exp_value = int(numbers[0])
            if min_exp is not None and exp_value < min_exp:
                return False
            if max_exp is not None and exp_value > max_exp:
                return False
            return True
        except:
            return True


if __name__ == "__main__":
    # Example usage
    scraper = NaukriScraper(delay=2.0)
    
    # Search for Python developer jobs
    jobs = scraper.search_jobs(
        keyword="python developer",
        location="bangalore",
        max_pages=2
    )
    
    # Save results
    scraper.save_to_csv("python_jobs.csv")
    scraper.save_to_json("python_jobs.json")
    
    # Filter jobs
    filtered = scraper.filter_jobs(min_experience=2, max_experience=5)
    print(f"Jobs with 2-5 years experience: {len(filtered)}")
