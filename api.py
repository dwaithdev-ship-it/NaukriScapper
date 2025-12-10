"""REST API for Naukri Scraper using Flask."""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from config import API_HOST, API_PORT, API_DEBUG, API_SECRET_KEY, WEBHOOK_SECRET
from data_manager import DataManager
from ai_integration import AIIntegration
from naukri_scraper import NaukriEmployerScraper
from models import init_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = API_SECRET_KEY
CORS(app)

# Initialize database
init_db()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/job-search', methods=['POST'])
def create_job_search():
    """
    Create a new job search.
    
    Request body:
        {
            "job_role": "Python Developer",
            "experience_min": 2.0,
            "experience_max": 5.0,
            "location": "Bangalore",
            "job_type": "Full-time"
        }
    """
    try:
        data = request.json
        dm = DataManager()
        
        job_search = dm.create_job_search(
            job_role=data['job_role'],
            experience_min=data.get('experience_min'),
            experience_max=data.get('experience_max'),
            location=data.get('location'),
            job_type=data.get('job_type')
        )
        
        dm.close()
        
        return jsonify({
            'status': 'success',
            'job_search_id': job_search.id,
            'job_role': job_search.job_role
        }), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e}'}), 400
    except Exception as e:
        logger.error(f"Error creating job search: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/candidates', methods=['POST'])
def add_candidate():
    """
    Add a new candidate.
    
    Request body:
        {
            "job_search_id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            ...
        }
    """
    try:
        data = request.json
        dm = DataManager()
        
        candidate = dm.add_candidate(
            job_search_id=data['job_search_id'],
            profile_data=data
        )
        
        dm.close()
        
        return jsonify({
            'status': 'success',
            'candidate_id': candidate.id,
            'name': candidate.name
        }), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e}'}), 400
    except Exception as e:
        logger.error(f"Error adding candidate: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/candidates/<int:job_search_id>', methods=['GET'])
def get_candidates(job_search_id):
    """Get all candidates for a job search."""
    try:
        dm = DataManager()
        candidates = dm.get_candidates_by_job_search(job_search_id)
        
        result = [{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'current_location': c.current_location,
            'experience_years': c.experience_years,
            'current_company': c.current_company,
            'current_designation': c.current_designation,
            'skills': c.skills,
            'contacted': c.contacted,
            'interested': c.interested,
            'interview_scheduled': c.interview_scheduled
        } for c in candidates]
        
        dm.close()
        
        return jsonify({
            'status': 'success',
            'count': len(result),
            'candidates': result
        })
        
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/candidates/<int:candidate_id>/status', methods=['PUT'])
def update_candidate_status(candidate_id):
    """
    Update candidate status.
    
    Request body:
        {
            "contacted": true,
            "interested": true,
            "comments": "Interested in the role"
        }
    """
    try:
        data = request.json
        dm = DataManager()
        
        dm.update_candidate_status(
            candidate_id=candidate_id,
            contacted=data.get('contacted'),
            interested=data.get('interested'),
            interview_scheduled=data.get('interview_scheduled'),
            interview_date=data.get('interview_date'),
            comments=data.get('comments')
        )
        
        dm.close()
        
        return jsonify({
            'status': 'success',
            'candidate_id': candidate_id
        })
        
    except Exception as e:
        logger.error(f"Error updating candidate status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<int:job_search_id>', methods=['GET'])
def export_candidates(job_search_id):
    """Export candidates to Excel file."""
    try:
        dm = DataManager()
        filepath = dm.export_to_excel(job_search_id)
        dm.close()
        
        if not filepath:
            return jsonify({'error': 'No candidates to export'}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting candidates: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics/<int:job_search_id>', methods=['GET'])
def get_statistics(job_search_id):
    """Get statistics for a job search."""
    try:
        dm = DataManager()
        stats = dm.get_statistics(job_search_id)
        dm.close()
        
        return jsonify({
            'status': 'success',
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/trigger-calls', methods=['POST'])
def trigger_calls():
    """
    Trigger automated calls for candidates.
    
    Request body:
        {
            "candidate_ids": [1, 2, 3],
            "job_data": {
                "job_role": "Python Developer",
                "location": "Bangalore"
            },
            "ai_tool": "n8n",
            "custom_script": "optional custom script"
        }
    """
    try:
        data = request.json
        ai = AIIntegration()
        
        results = ai.trigger_automated_calls(
            candidate_ids=data['candidate_ids'],
            job_data=data['job_data'],
            ai_tool=data.get('ai_tool', 'n8n'),
            custom_script=data.get('custom_script'),
            custom_webhook=data.get('custom_webhook')
        )
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e}'}), 400
    except Exception as e:
        logger.error(f"Error triggering calls: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhook/callback', methods=['POST'])
def webhook_callback():
    """
    Receive callback from AI tools with call results.
    
    Request body:
        {
            "candidate_id": 1,
            "call_status": "completed",
            "interested": true,
            "response": "Candidate is interested",
            "secret": "webhook_secret"
        }
    """
    try:
        data = request.json
        
        # Verify webhook secret if configured
        if WEBHOOK_SECRET and data.get('secret') != WEBHOOK_SECRET:
            return jsonify({'error': 'Invalid webhook secret'}), 401
        
        ai = AIIntegration()
        result = ai.process_webhook_response(data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_profiles():
    """
    Scrape profiles from Naukri.
    
    Request body:
        {
            "username": "employer@example.com",
            "password": "password",
            "job_search_id": 1,
            "job_role": "Python Developer",
            "experience_min": 2.0,
            "experience_max": 5.0,
            "location": "Bangalore",
            "max_results": 50
        }
    """
    try:
        data = request.json
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Create scraper instance
        scraper = NaukriEmployerScraper(
            username=data['username'],
            password=data['password']
        )
        
        # Login
        if not scraper.login():
            scraper.close()
            return jsonify({'error': 'Login failed'}), 401
        
        # Search candidates
        candidates = scraper.search_candidates(
            job_role=data.get('job_role', ''),
            experience_min=data.get('experience_min'),
            experience_max=data.get('experience_max'),
            location=data.get('location'),
            job_type=data.get('job_type'),
            max_results=data.get('max_results', 50)
        )
        
        scraper.close()
        
        # Save to database if job_search_id provided
        if data.get('job_search_id') and candidates:
            dm = DataManager()
            dm.add_candidates_bulk(data['job_search_id'], candidates)
            dm.close()
        
        return jsonify({
            'status': 'success',
            'count': len(candidates),
            'candidates': candidates
        })
        
    except Exception as e:
        logger.error(f"Error scraping profiles: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
