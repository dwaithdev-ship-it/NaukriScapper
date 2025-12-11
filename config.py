"""Configuration management for NaukriScapper."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///naukri_scraper.db')
    
    # Scraping configuration
    DEFAULT_DELAY = float(os.getenv('DEFAULT_DELAY', '2.0'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    TIMEOUT = int(os.getenv('TIMEOUT', '30'))
    
    # API configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    # AI Integration configuration
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
    MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL', '')
    
    # Security configuration
    ALLOW_LOCAL_WEBHOOKS = os.getenv('ALLOW_LOCAL_WEBHOOKS', 'False').lower() == 'true'
    
    # File export configuration
    EXPORT_DIR = os.getenv('EXPORT_DIR', './exports')
