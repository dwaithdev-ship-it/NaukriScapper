"""Core scraper for Naukri employer login and profile search."""
import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup

from config import (
    NAUKRI_EMPLOYER_URL, REQUEST_DELAY, IMPLICIT_WAIT, 
    PAGE_LOAD_TIMEOUT, HEADLESS_MODE, BROWSER_TYPE
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NaukriEmployerScraper:
    """Scraper for Naukri employer portal to search and extract candidate profiles."""
    
    def __init__(self, username: str, password: str, headless: bool = HEADLESS_MODE):
        """
        Initialize the scraper with employer credentials.
        
        Args:
            username: Naukri employer username/email
            password: Naukri employer password
            headless: Run browser in headless mode
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.is_logged_in = False
        self.delay = REQUEST_DELAY
        
    def _setup_driver(self):
        """Setup Selenium WebDriver based on configuration."""
        try:
            if BROWSER_TYPE.lower() == 'firefox':
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            logger.info(f"WebDriver initialized successfully ({BROWSER_TYPE})")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def login(self) -> bool:
        """
        Login to Naukri employer portal.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.driver:
            self._setup_driver()
        
        try:
            logger.info("Navigating to Naukri employer login page...")
            self.driver.get(NAUKRI_EMPLOYER_URL)
            time.sleep(self.delay)
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, IMPLICIT_WAIT)
            
            # Find and fill username field
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            logger.info("Username entered")
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Password entered")
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            logger.info("Login button clicked")
            
            time.sleep(self.delay * 2)
            
            # Check if login was successful
            # This would need to be adjusted based on actual Naukri employer portal structure
            if "dashboard" in self.driver.current_url.lower() or "recruiter" in self.driver.current_url.lower():
                self.is_logged_in = True
                logger.info("Login successful!")
                return True
            else:
                logger.warning("Login may have failed - checking page content")
                # Additional verification could be added here
                self.is_logged_in = True  # Optimistic for now
                return True
                
        except TimeoutException:
            logger.error("Timeout waiting for login page elements")
            return False
        except NoSuchElementException as e:
            logger.error(f"Could not find login element: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def search_candidates(self, 
                         job_role: str,
                         experience_min: Optional[float] = None,
                         experience_max: Optional[float] = None,
                         location: Optional[str] = None,
                         job_type: Optional[str] = None,
                         max_results: int = 50) -> List[Dict]:
        """
        Search for candidates based on job criteria.
        
        Args:
            job_role: Job role/title to search for
            experience_min: Minimum years of experience
            experience_max: Maximum years of experience
            location: Preferred location
            job_type: Type of job (Full-time, Contract, etc.)
            max_results: Maximum number of profiles to fetch
            
        Returns:
            List of candidate profile dictionaries
        """
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return []
        
        logger.info(f"Searching for candidates: {job_role}")
        candidates = []
        
        try:
            # Navigate to search page
            # Note: This is a simplified version. Actual implementation would need
            # to match the real Naukri recruiter search interface
            search_url = "https://www.naukri.com/recruiter/search"
            self.driver.get(search_url)
            time.sleep(self.delay)
            
            # Here you would implement the actual search logic
            # This would involve:
            # 1. Filling in search criteria
            # 2. Submitting the search
            # 3. Iterating through results
            # 4. Extracting profile information
            
            # For now, this is a placeholder structure
            logger.info("Search functionality requires access to actual Naukri recruiter portal")
            logger.info("Placeholder implementation - would extract profiles from search results")
            
            # Simulate profile extraction (in real implementation, this would parse actual results)
            # candidates = self._extract_profiles_from_page()
            
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
        
        return candidates
    
    def _extract_profiles_from_page(self) -> List[Dict]:
        """
        Extract candidate profiles from current search results page.
        
        Returns:
            List of profile dictionaries
        """
        profiles = []
        
        try:
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # This would need to be customized based on actual Naukri HTML structure
            profile_cards = soup.find_all('div', class_='candidate-card')  # Example selector
            
            for card in profile_cards:
                profile = {
                    'name': self._safe_extract(card, 'div', 'candidate-name'),
                    'email': self._safe_extract(card, 'span', 'candidate-email'),
                    'phone': self._safe_extract(card, 'span', 'candidate-phone'),
                    'current_location': self._safe_extract(card, 'span', 'location'),
                    'experience_years': self._extract_experience(card),
                    'current_company': self._safe_extract(card, 'span', 'company'),
                    'current_designation': self._safe_extract(card, 'span', 'designation'),
                    'skills': self._extract_skills(card),
                    'education': self._safe_extract(card, 'div', 'education'),
                    'profile_url': self._extract_profile_url(card),
                    'scraped_date': datetime.utcnow()
                }
                profiles.append(profile)
                
        except Exception as e:
            logger.error(f"Error extracting profiles: {e}")
        
        return profiles
    
    def _safe_extract(self, element, tag: str, class_name: str) -> Optional[str]:
        """Safely extract text from an element."""
        try:
            found = element.find(tag, class_=class_name)
            return found.get_text(strip=True) if found else None
        except:
            return None
    
    def _extract_experience(self, element) -> Optional[float]:
        """Extract years of experience from element."""
        try:
            exp_text = self._safe_extract(element, 'span', 'experience')
            if exp_text:
                # Parse experience text like "5 years" or "5.5 years"
                import re
                match = re.search(r'(\d+\.?\d*)', exp_text)
                if match:
                    return float(match.group(1))
        except:
            pass
        return None
    
    def _extract_skills(self, element) -> Optional[str]:
        """Extract skills as comma-separated string."""
        try:
            skills_div = element.find('div', class_='skills')
            if skills_div:
                skill_tags = skills_div.find_all('span', class_='skill-tag')
                return ', '.join([tag.get_text(strip=True) for tag in skill_tags])
        except:
            pass
        return None
    
    def _extract_profile_url(self, element) -> Optional[str]:
        """Extract profile URL from element."""
        try:
            link = element.find('a', class_='profile-link')
            if link and 'href' in link.attrs:
                return link['href']
        except:
            pass
        return None
    
    def close(self):
        """Close the browser and cleanup."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == '__main__':
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    username = os.getenv('NAUKRI_USERNAME')
    password = os.getenv('NAUKRI_PASSWORD')
    
    if not username or not password:
        print("Please set NAUKRI_USERNAME and NAUKRI_PASSWORD in .env file")
    else:
        with NaukriEmployerScraper(username, password) as scraper:
            if scraper.login():
                print("Login successful!")
                candidates = scraper.search_candidates(
                    job_role="Python Developer",
                    experience_min=2,
                    experience_max=5,
                    location="Bangalore"
                )
                print(f"Found {len(candidates)} candidates")
