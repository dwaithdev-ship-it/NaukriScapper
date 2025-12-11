"""Unit tests for NaukriScapper."""
import unittest
import os
import tempfile
from naukri_scraper import NaukriScraper
from data_manager import DataManager
from models import get_session, Base, engine


class TestNaukriScraper(unittest.TestCase):
    """Test cases for NaukriScraper."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = NaukriScraper(delay=0.1)
    
    def test_initialization(self):
        """Test scraper initialization."""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.delay, 0.1)
        self.assertEqual(self.scraper.jobs, [])
    
    def test_default_delay(self):
        """Test default delay value."""
        scraper = NaukriScraper()
        self.assertEqual(scraper.delay, 2.0)
    
    def test_filter_jobs_empty(self):
        """Test filtering with no jobs."""
        filtered = self.scraper.filter_jobs()
        self.assertEqual(filtered, [])
    
    def test_filter_by_experience(self):
        """Test filtering by experience."""
        self.scraper.jobs = [
            {'experience': '2-5 years', 'description': 'Python developer'},
            {'experience': '5-8 years', 'description': 'Senior developer'},
            {'experience': '0-2 years', 'description': 'Junior developer'},
        ]
        
        filtered = self.scraper.filter_jobs(min_experience=3)
        self.assertEqual(len(filtered), 1)
    
    def test_filter_by_skills(self):
        """Test filtering by required skills."""
        self.scraper.jobs = [
            {'description': 'Python and Django experience required'},
            {'description': 'Java Spring Boot developer'},
            {'description': 'Python Flask developer'},
        ]
        
        filtered = self.scraper.filter_jobs(required_skills=['Python'])
        self.assertEqual(len(filtered), 2)
    
    def test_filter_by_location(self):
        """Test filtering by location."""
        self.scraper.jobs = [
            {'location': 'Bangalore'},
            {'location': 'Mumbai'},
            {'location': 'Bangalore/Hyderabad'},
        ]
        
        filtered = self.scraper.filter_jobs(location='Bangalore')
        self.assertEqual(len(filtered), 2)
    
    def test_export_to_csv(self):
        """Test CSV export."""
        self.scraper.jobs = [
            {'title': 'Python Developer', 'company': 'Tech Corp', 'location': 'Bangalore'},
            {'title': 'Java Developer', 'company': 'IT Inc', 'location': 'Mumbai'},
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import Config
            Config.EXPORT_DIR = tmpdir
            
            filepath = self.scraper.export_to_csv('test_jobs.csv')
            self.assertTrue(os.path.exists(filepath))
            
            # Verify file content
            with open(filepath, 'r') as f:
                content = f.read()
                self.assertIn('Python Developer', content)
                self.assertIn('Java Developer', content)
    
    def test_export_to_json(self):
        """Test JSON export."""
        self.scraper.jobs = [
            {'title': 'Python Developer', 'company': 'Tech Corp'},
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            from config import Config
            Config.EXPORT_DIR = tmpdir
            
            filepath = self.scraper.export_to_json('test_jobs.json')
            self.assertTrue(os.path.exists(filepath))
            
            # Verify file content
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['title'], 'Python Developer')


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use in-memory database for testing
        from config import Config
        Config.DATABASE_URL = 'sqlite:///:memory:'
        
        # Recreate tables
        Base.metadata.create_all(engine)
        
        self.data_manager = DataManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.data_manager.close()
    
    def test_create_job_search(self):
        """Test creating job search."""
        search = self.data_manager.create_job_search(
            query='Python developer',
            location='Bangalore'
        )
        self.assertIsNotNone(search.id)
        self.assertEqual(search.query, 'Python developer')
        self.assertEqual(search.location, 'Bangalore')
    
    def test_create_candidate(self):
        """Test creating candidate."""
        candidate = self.data_manager.create_candidate(
            name='John Doe',
            email='john@example.com',
            experience=5.5
        )
        self.assertIsNotNone(candidate.id)
        self.assertEqual(candidate.name, 'John Doe')
        self.assertEqual(candidate.experience, 5.5)
    
    def test_create_call_log(self):
        """Test creating call log."""
        log = self.data_manager.create_call_log(
            candidate_id=1,
            call_status='completed',
            duration=300,
            success=True
        )
        self.assertIsNotNone(log.id)
        self.assertEqual(log.call_status, 'completed')
        self.assertTrue(log.success)


if __name__ == '__main__':
    unittest.main()
