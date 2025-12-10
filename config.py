"""Configuration management for Naukri Scraper."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/naukri_profiles.db')

# Scraper configuration
NAUKRI_EMPLOYER_URL = 'https://www.naukri.com/recruiter/login'
NAUKRI_SEARCH_URL = 'https://www.naukri.com/recruiter/search'
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.0'))
IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

# Export configuration
EXPORT_DIR = BASE_DIR / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)

# API configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'change-me-in-production')

# AI Integration configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL', '')

# Call script template
DEFAULT_CALL_SCRIPT = """
Hello {candidate_name},

This is regarding the {job_role} position at our company.
We found your profile on Naukri and would like to discuss this opportunity with you.

Are you interested in exploring this opportunity?
"""

# Browser configuration
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')  # chrome or firefox
