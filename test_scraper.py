"""Unit tests for Naukri Scraper."""
import unittest
import os
import tempfile
from datetime import datetime
from pathlib import Path

from models import init_db, get_session, JobSearch, Candidate, CallLog
from data_manager import DataManager
from ai_integration import AIIntegration
from config import DEFAULT_CALL_SCRIPT


class TestDatabaseModels(unittest.TestCase):
    """Test database models and initialization."""
    
    def setUp(self):
        """Set up test database."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f'sqlite:///{self.db_file.name}'
        init_db(self.db_url)
        self.session = get_session(self.db_url)
    
    def tearDown(self):
        """Clean up test database."""
        self.session.close()
        os.unlink(self.db_file.name)
    
    def test_create_job_search(self):
        """Test creating a job search."""
        job_search = JobSearch(
            job_role="Python Developer",
            experience_min=2.0,
            experience_max=5.0,
            location="Bangalore"
        )
        self.session.add(job_search)
        self.session.commit()
        
        self.assertIsNotNone(job_search.id)
        self.assertEqual(job_search.job_role, "Python Developer")
    
    def test_create_candidate(self):
        """Test creating a candidate."""
        job_search = JobSearch(job_role="Python Developer")
        self.session.add(job_search)
        self.session.commit()
        
        candidate = Candidate(
            job_search_id=job_search.id,
            name="John Doe",
            email="john@example.com",
            experience_years=3.5
        )
        self.session.add(candidate)
        self.session.commit()
        
        self.assertIsNotNone(candidate.id)
        self.assertEqual(candidate.name, "John Doe")
        self.assertEqual(candidate.job_search_id, job_search.id)
    
    def test_create_call_log(self):
        """Test creating a call log."""
        job_search = JobSearch(job_role="Python Developer")
        self.session.add(job_search)
        self.session.commit()
        
        candidate = Candidate(
            job_search_id=job_search.id,
            name="John Doe"
        )
        self.session.add(candidate)
        self.session.commit()
        
        call_log = CallLog(
            candidate_id=candidate.id,
            call_status="completed",
            interested=True
        )
        self.session.add(call_log)
        self.session.commit()
        
        self.assertIsNotNone(call_log.id)
        self.assertEqual(call_log.call_status, "completed")
        self.assertTrue(call_log.interested)


class TestDataManager(unittest.TestCase):
    """Test data manager functionality."""
    
    def setUp(self):
        """Set up test database and data manager."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f'sqlite:///{self.db_file.name}'
        
        # Temporarily modify DATABASE_URL
        import config
        self.original_db_url = config.DATABASE_URL
        config.DATABASE_URL = self.db_url
        
        init_db(self.db_url)
        self.dm = DataManager()
        self.dm.session = get_session(self.db_url)
    
    def tearDown(self):
        """Clean up test database."""
        self.dm.close()
        os.unlink(self.db_file.name)
        
        # Restore original DATABASE_URL
        import config
        config.DATABASE_URL = self.original_db_url
    
    def test_create_job_search(self):
        """Test creating a job search via data manager."""
        job_search = self.dm.create_job_search(
            job_role="Python Developer",
            experience_min=2.0,
            experience_max=5.0,
            location="Bangalore"
        )
        
        self.assertIsNotNone(job_search.id)
        self.assertEqual(job_search.job_role, "Python Developer")
    
    def test_add_candidate(self):
        """Test adding a candidate."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        
        profile_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+91-9876543210',
            'experience_years': 4.0
        }
        
        candidate = self.dm.add_candidate(job_search.id, profile_data)
        
        self.assertIsNotNone(candidate.id)
        self.assertEqual(candidate.name, 'Jane Smith')
        self.assertEqual(candidate.job_search_id, job_search.id)
    
    def test_add_candidates_bulk(self):
        """Test adding multiple candidates."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        
        profiles = [
            {'name': 'Candidate 1', 'experience_years': 2.0},
            {'name': 'Candidate 2', 'experience_years': 3.0},
            {'name': 'Candidate 3', 'experience_years': 4.0}
        ]
        
        candidates = self.dm.add_candidates_bulk(job_search.id, profiles)
        
        self.assertEqual(len(candidates), 3)
        self.assertEqual(candidates[0].name, 'Candidate 1')
    
    def test_update_candidate_status(self):
        """Test updating candidate status."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        candidate = self.dm.add_candidate(job_search.id, {'name': 'Test User'})
        
        self.dm.update_candidate_status(
            candidate_id=candidate.id,
            contacted=True,
            interested=True,
            comments="Very interested"
        )
        
        self.dm.session.refresh(candidate)
        self.assertTrue(candidate.contacted)
        self.assertTrue(candidate.interested)
        self.assertEqual(candidate.comments, "Very interested")
    
    def test_get_statistics(self):
        """Test getting statistics."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        
        # Add candidates with different statuses
        c1 = self.dm.add_candidate(job_search.id, {'name': 'C1'})
        c2 = self.dm.add_candidate(job_search.id, {'name': 'C2'})
        c3 = self.dm.add_candidate(job_search.id, {'name': 'C3'})
        
        self.dm.update_candidate_status(c1.id, contacted=True, interested=True)
        self.dm.update_candidate_status(c2.id, contacted=True, interested=False)
        
        stats = self.dm.get_statistics(job_search.id)
        
        self.assertEqual(stats['total_candidates'], 3)
        self.assertEqual(stats['contacted'], 2)
        self.assertEqual(stats['interested'], 1)
        self.assertEqual(stats['not_interested'], 1)
        self.assertEqual(stats['pending_contact'], 1)
    
    def test_log_call(self):
        """Test logging a call."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        candidate = self.dm.add_candidate(job_search.id, {'name': 'Test User'})
        
        call_log = self.dm.log_call(
            candidate_id=candidate.id,
            script_used="Test script",
            call_status="completed",
            interested=True,
            ai_tool_used="n8n"
        )
        
        self.assertIsNotNone(call_log.id)
        self.assertEqual(call_log.call_status, "completed")
        self.assertTrue(call_log.interested)
        self.assertEqual(call_log.ai_tool_used, "n8n")


class TestAIIntegration(unittest.TestCase):
    """Test AI integration functionality."""
    
    def test_format_call_script(self):
        """Test formatting call script with data."""
        ai = AIIntegration()
        
        candidate_data = {
            'name': 'John Doe',
            'experience_years': 3.5
        }
        
        job_data = {
            'job_role': 'Python Developer',
            'location': 'Bangalore',
            'company_name': 'Tech Corp'
        }
        
        script = ai.format_call_script(candidate_data, job_data)
        
        self.assertIn('John Doe', script)
        self.assertIn('Python Developer', script)
    
    def test_format_call_script_with_custom_template(self):
        """Test formatting with custom template."""
        ai = AIIntegration()
        
        candidate_data = {'name': 'Jane Smith'}
        job_data = {'job_role': 'Developer'}
        
        custom_template = "Hello {candidate_name}, we have a {job_role} position."
        script = ai.format_call_script(candidate_data, job_data, custom_template)
        
        self.assertEqual(script, "Hello Jane Smith, we have a Developer position.")
    
    def test_process_webhook_response(self):
        """Test processing webhook response."""
        # Set up test database
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_url = f'sqlite:///{db_file.name}'
        
        import config
        original_db_url = config.DATABASE_URL
        config.DATABASE_URL = db_url
        
        try:
            init_db(db_url)
            dm = DataManager()
            dm.session = get_session(db_url)
            
            # Create test data
            job_search = dm.create_job_search(job_role="Test Role")
            candidate = dm.add_candidate(job_search.id, {'name': 'Test User'})
            
            # Create AI integration with same database
            ai = AIIntegration()
            ai.data_manager.session = dm.session
            
            webhook_data = {
                'candidate_id': candidate.id,
                'call_status': 'completed',
                'interested': True,
                'response': 'Very interested in the position'
            }
            
            result = ai.process_webhook_response(webhook_data)
            
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['candidate_id'], candidate.id)
            
            dm.close()
        finally:
            os.unlink(db_file.name)
            config.DATABASE_URL = original_db_url


class TestExcelExport(unittest.TestCase):
    """Test Excel export functionality."""
    
    def setUp(self):
        """Set up test database and export directory."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_url = f'sqlite:///{self.db_file.name}'
        self.export_dir = tempfile.mkdtemp()
        
        import config
        self.original_db_url = config.DATABASE_URL
        self.original_export_dir = config.EXPORT_DIR
        config.DATABASE_URL = self.db_url
        config.EXPORT_DIR = Path(self.export_dir)
        
        init_db(self.db_url)
        self.dm = DataManager()
        self.dm.session = get_session(self.db_url)
    
    def tearDown(self):
        """Clean up test files."""
        self.dm.close()
        os.unlink(self.db_file.name)
        
        # Clean up export directory
        import shutil
        shutil.rmtree(self.export_dir, ignore_errors=True)
        
        # Restore config
        import config
        config.DATABASE_URL = self.original_db_url
        config.EXPORT_DIR = self.original_export_dir
    
    def test_export_to_excel(self):
        """Test exporting candidates to Excel."""
        job_search = self.dm.create_job_search(job_role="Python Developer")
        
        profiles = [
            {
                'name': 'Candidate 1',
                'email': 'c1@example.com',
                'experience_years': 3.0
            },
            {
                'name': 'Candidate 2',
                'email': 'c2@example.com',
                'experience_years': 4.0
            }
        ]
        
        self.dm.add_candidates_bulk(job_search.id, profiles)
        
        filepath = self.dm.export_to_excel(job_search.id)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.xlsx'))


if __name__ == '__main__':
    unittest.main()
