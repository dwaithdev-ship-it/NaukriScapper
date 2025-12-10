#!/usr/bin/env python3
"""
Basic tests for Naukri Scraper
"""

import unittest
from naukri_scraper import NaukriScraper
import os


class TestNaukriScraper(unittest.TestCase):
    """
    Test cases for NaukriScraper class
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = NaukriScraper(delay=1.0)
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.delay, 1.0)
        self.assertEqual(len(self.scraper.jobs), 0)
    
    def test_base_url(self):
        """Test base URL is set correctly"""
        self.assertEqual(self.scraper.BASE_URL, "https://www.naukri.com")
    
    def test_session_headers(self):
        """Test session headers are set"""
        self.assertIn('User-Agent', self.scraper.session.headers)
        self.assertIn('Accept', self.scraper.session.headers)
    
    def test_filter_jobs_empty(self):
        """Test filtering with no jobs"""
        result = self.scraper.filter_jobs(min_experience=2)
        self.assertEqual(len(result), 0)
    
    def test_filter_jobs_with_data(self):
        """Test filtering with sample data"""
        self.scraper.jobs = [
            {'title': 'Python Developer', 'experience': '2-5 Yrs', 'location': 'Bangalore'},
            {'title': 'Java Developer', 'experience': '5-8 Yrs', 'location': 'Mumbai'},
            {'title': 'Data Scientist', 'experience': '1-3 Yrs', 'location': 'Bangalore'},
        ]
        
        # Test location filter
        bangalore_jobs = self.scraper.filter_jobs(locations=['Bangalore'])
        self.assertEqual(len(bangalore_jobs), 2)
    
    def test_experience_check(self):
        """Test experience checking logic"""
        self.assertTrue(self.scraper._check_experience('2-5 Yrs', 1, 10))
        self.assertTrue(self.scraper._check_experience('5 Yrs', 3, 7))
        self.assertFalse(self.scraper._check_experience('8-10 Yrs', 1, 5))
    
    def test_save_to_csv_no_jobs(self):
        """Test CSV save with no jobs"""
        # Should handle gracefully
        self.scraper.save_to_csv("test_empty.csv")
        self.assertFalse(os.path.exists("test_empty.csv"))
    
    def test_save_to_json_no_jobs(self):
        """Test JSON save with no jobs"""
        # Should handle gracefully
        self.scraper.save_to_json("test_empty.json")
        self.assertFalse(os.path.exists("test_empty.json"))
    
    def test_save_to_csv_with_data(self):
        """Test CSV save with sample data"""
        self.scraper.jobs = [
            {'title': 'Test Job', 'company': 'Test Company', 'location': 'Test Location'}
        ]
        
        filename = "test_output.csv"
        self.scraper.save_to_csv(filename)
        
        # Check file exists
        self.assertTrue(os.path.exists(filename))
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_save_to_json_with_data(self):
        """Test JSON save with sample data"""
        self.scraper.jobs = [
            {'title': 'Test Job', 'company': 'Test Company', 'location': 'Test Location'}
        ]
        
        filename = "test_output.json"
        self.scraper.save_to_json(filename)
        
        # Check file exists
        self.assertTrue(os.path.exists(filename))
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)


class TestExperienceFilter(unittest.TestCase):
    """
    Test cases for experience filtering
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = NaukriScraper()
    
    def test_experience_extraction(self):
        """Test experience value extraction"""
        test_cases = [
            ('2-5 Yrs', 2, True),
            ('5-8 Years', 5, True),
            ('1 Year', 1, True),
            ('10+ Years', 10, True),
            ('Fresher', None, True),  # Should return True for unparseable
        ]
        
        for exp_str, expected_val, should_pass in test_cases:
            if expected_val is not None:
                result = self.scraper._check_experience(exp_str, 0, 20)
                self.assertTrue(result)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNaukriScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestExperienceFilter))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
