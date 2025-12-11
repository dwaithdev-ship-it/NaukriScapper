"""Core web scraping functionality for Naukri.com."""
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import Config


class NaukriScraper:
    """Web scraper for Naukri.com job listings."""
    
    def __init__(self, delay: float = None):
        """Initialize scraper.
        
        Args:
            delay: Delay between requests in seconds (default: 2.0)
        """
        self.delay = delay if delay is not None else Config.DEFAULT_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.jobs = []
    
    def search_jobs(self, keyword: str, location: str = "", experience: str = "", 
                   salary: str = "", max_pages: int = 1) -> List[Dict]:
        """Search for jobs on Naukri.com.
        
        Args:
            keyword: Job title or keyword to search
            location: Job location
            experience: Experience level
            salary: Salary range
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of job dictionaries
        """
        self.jobs = []
        base_url = "https://www.naukri.com"
        
        # Build search URL
        search_params = []
        if keyword:
            search_params.append(f"k={keyword}")
        if location:
            search_params.append(f"l={location}")
        if experience:
            search_params.append(f"experience={experience}")
        
        search_url = f"{base_url}/job-listings?{'&'.join(search_params)}" if search_params else base_url
        
        for page in range(1, max_pages + 1):
            page_url = f"{search_url}&page={page}" if page > 1 else search_url
            
            try:
                response = self.session.get(page_url, timeout=Config.TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs_on_page = self._parse_job_listings(soup)
                self.jobs.extend(jobs_on_page)
                
                # Respect rate limiting
                if page < max_pages:
                    time.sleep(self.delay)
                    
            except requests.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return self.jobs
    
    def _parse_job_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse job listings from HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # This is a simplified parser - actual Naukri.com structure may vary
        job_cards = soup.find_all('article', class_='jobTuple') or soup.find_all('div', class_='job-card')
        
        for card in job_cards:
            try:
                job = {
                    'title': self._extract_text(card, ['h3', 'h2', 'a'], class_='title'),
                    'company': self._extract_text(card, ['div', 'span'], class_='company'),
                    'experience': self._extract_text(card, ['span'], class_='experience'),
                    'salary': self._extract_text(card, ['span'], class_='salary'),
                    'location': self._extract_text(card, ['span'], class_='location'),
                    'description': self._extract_text(card, ['div'], class_='job-description'),
                }
                
                # Extract job URL
                link = card.find('a', href=True)
                if link:
                    job['url'] = link['href'] if link['href'].startswith('http') else f"https://www.naukri.com{link['href']}"
                
                jobs.append(job)
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def _extract_text(self, element, tags: List[str], class_: str = None) -> str:
        """Extract text from element.
        
        Args:
            element: BeautifulSoup element
            tags: List of tag names to try
            class_: CSS class to match
            
        Returns:
            Extracted text or empty string
        """
        for tag in tags:
            found = element.find(tag, class_=class_) if class_ else element.find(tag)
            if found:
                return found.get_text(strip=True)
        return ""
    
    def filter_jobs(self, min_experience: float = None, max_experience: float = None,
                   required_skills: List[str] = None, location: str = None) -> List[Dict]:
        """Filter scraped jobs based on criteria.
        
        Args:
            min_experience: Minimum years of experience
            max_experience: Maximum years of experience
            required_skills: List of required skills
            location: Required location
            
        Returns:
            Filtered list of jobs
        """
        filtered = self.jobs
        
        if min_experience is not None or max_experience is not None:
            filtered = [
                job for job in filtered
                if self._check_experience(job.get('experience', ''), min_experience, max_experience)
            ]
        
        if required_skills:
            filtered = [
                job for job in filtered
                if any(skill.lower() in job.get('description', '').lower() for skill in required_skills)
            ]
        
        if location:
            filtered = [
                job for job in filtered
                if location.lower() in job.get('location', '').lower()
            ]
        
        return filtered
    
    def _check_experience(self, exp_str: str, min_exp: Optional[float], max_exp: Optional[float]) -> bool:
        """Check if experience string matches criteria.
        
        Args:
            exp_str: Experience string from job listing
            min_exp: Minimum experience required
            max_exp: Maximum experience allowed
            
        Returns:
            True if matches criteria
        """
        try:
            # Extract numbers from experience string
            import re
            numbers = re.findall(r'\d+\.?\d*', exp_str)
            if not numbers:
                return True  # No experience info, include by default
            
            exp_value = float(numbers[0])
            
            if min_exp is not None and exp_value < min_exp:
                return False
            if max_exp is not None and exp_value > max_exp:
                return False
            
            return True
        except (ValueError, IndexError):
            return True
    
    def export_to_csv(self, filename: str, jobs: List[Dict] = None) -> str:
        """Export jobs to CSV file.
        
        Args:
            filename: Output filename
            jobs: List of jobs to export (default: all scraped jobs)
            
        Returns:
            Path to exported file
        """
        import csv
        import os
        
        jobs = jobs or self.jobs
        
        # Ensure export directory exists
        os.makedirs(Config.EXPORT_DIR, exist_ok=True)
        filepath = os.path.join(Config.EXPORT_DIR, filename)
        
        if not jobs:
            return filepath
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
            writer.writeheader()
            writer.writerows(jobs)
        
        return filepath
    
    def export_to_json(self, filename: str, jobs: List[Dict] = None) -> str:
        """Export jobs to JSON file.
        
        Args:
            filename: Output filename
            jobs: List of jobs to export (default: all scraped jobs)
            
        Returns:
            Path to exported file
        """
        import json
        import os
        
        jobs = jobs or self.jobs
        
        # Ensure export directory exists
        os.makedirs(Config.EXPORT_DIR, exist_ok=True)
        filepath = os.path.join(Config.EXPORT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed information about a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        try:
            response = self.session.get(job_url, timeout=Config.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': job_url,
                'title': self._extract_text(soup, ['h1'], class_='jd-header-title'),
                'company': self._extract_text(soup, ['div', 'span'], class_='jd-header-comp-name'),
                'experience': self._extract_text(soup, ['span'], class_='exp'),
                'salary': self._extract_text(soup, ['span'], class_='salary'),
                'location': self._extract_text(soup, ['span'], class_='loc'),
                'description': self._extract_text(soup, ['div'], class_='dang-inner-html'),
                'skills': self._extract_text(soup, ['div'], class_='key-skill'),
            }
            
            return details
        except requests.RequestException as e:
            print(f"Error fetching job details: {e}")
            return {'url': job_url, 'error': str(e)}
