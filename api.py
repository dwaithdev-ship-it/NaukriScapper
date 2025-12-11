"""REST API for NaukriScapper."""
from flask import Flask, request, jsonify
from config import Config
from naukri_scraper import NaukriScraper
from data_manager import DataManager
from ai_integration import AIIntegration

app = Flask(__name__)
data_manager = DataManager()
ai_integration = AIIntegration()


@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        'name': 'NaukriScapper API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /api/scrape': 'Scrape jobs',
            'GET /api/searches': 'List job searches',
            'GET /api/searches/<id>': 'Get job search',
            'POST /api/candidates': 'Create candidate',
            'GET /api/candidates': 'List candidates',
            'GET /api/candidates/<id>': 'Get candidate',
            'GET /api/candidates/search': 'Search candidates',
            'POST /api/webhook/send': 'Send data to webhook',
            'POST /api/webhook/callback': 'Webhook callback endpoint',
            'GET /api/call-logs': 'List call logs',
            'GET /api/config/webhooks': 'Get webhook configuration'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/api/scrape', methods=['POST'])
def scrape_jobs():
    """Scrape jobs from Naukri.com.
    
    Request body:
        {
            "keyword": "python developer",
            "location": "bangalore",
            "experience": "2-5",
            "salary": "10-20",
            "max_pages": 2
        }
    """
    data = request.json
    keyword = data.get('keyword', '')
    location = data.get('location', '')
    experience = data.get('experience', '')
    salary = data.get('salary', '')
    max_pages = data.get('max_pages', 1)
    
    if not keyword:
        return jsonify({'error': 'keyword is required'}), 400
    
    # Create job search record
    job_search = data_manager.create_job_search(
        query=keyword,
        location=location,
        experience=experience,
        salary=salary
    )
    
    # Scrape jobs
    scraper = NaukriScraper()
    jobs = scraper.search_jobs(
        keyword=keyword,
        location=location,
        experience=experience,
        salary=salary,
        max_pages=max_pages
    )
    
    # Update job search with results
    data_manager.update_job_search(
        search_id=job_search.id,
        results_count=len(jobs),
        status='completed'
    )
    
    return jsonify({
        'search_id': job_search.id,
        'results_count': len(jobs),
        'jobs': jobs
    })


@app.route('/api/searches', methods=['GET'])
def list_searches():
    """List all job searches."""
    limit = request.args.get('limit', 100, type=int)
    searches = data_manager.list_job_searches(limit=limit)
    return jsonify({
        'count': len(searches),
        'searches': [s.to_dict() for s in searches]
    })


@app.route('/api/searches/<int:search_id>', methods=['GET'])
def get_search(search_id):
    """Get job search by ID."""
    search = data_manager.get_job_search(search_id)
    if not search:
        return jsonify({'error': 'Job search not found'}), 404
    return jsonify(search.to_dict())


@app.route('/api/candidates', methods=['POST'])
def create_candidate():
    """Create a new candidate.
    
    Request body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "experience": 5.5,
            "skills": "Python, Django, Flask",
            "location": "Bangalore",
            "current_company": "Tech Corp"
        }
    """
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    candidate = data_manager.create_candidate(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone'),
        experience=data.get('experience'),
        skills=data.get('skills'),
        location=data.get('location'),
        current_company=data.get('current_company')
    )
    
    return jsonify(candidate.to_dict()), 201


@app.route('/api/candidates', methods=['GET'])
def list_candidates():
    """List all candidates."""
    limit = request.args.get('limit', 100, type=int)
    candidates = data_manager.list_candidates(limit=limit)
    return jsonify({
        'count': len(candidates),
        'candidates': [c.to_dict() for c in candidates]
    })


@app.route('/api/candidates/<int:candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get candidate by ID."""
    candidate = data_manager.get_candidate(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    return jsonify(candidate.to_dict())


@app.route('/api/candidates/search', methods=['GET'])
def search_candidates():
    """Search candidates by criteria.
    
    Query parameters:
        - skills: Skills to search for
        - location: Location to filter by
        - min_experience: Minimum experience required
    """
    skills = request.args.get('skills')
    location = request.args.get('location')
    min_experience = request.args.get('min_experience', type=float)
    
    candidates = data_manager.search_candidates(
        skills=skills,
        location=location,
        min_experience=min_experience
    )
    
    return jsonify({
        'count': len(candidates),
        'candidates': [c.to_dict() for c in candidates]
    })


@app.route('/api/webhook/send', methods=['POST'])
def send_webhook():
    """Send data to configured webhook.
    
    Request body:
        {
            "candidate_id": 1,
            "webhook_type": "n8n"  // or "make" or "custom"
        }
    """
    data = request.json
    candidate_id = data.get('candidate_id')
    webhook_type = data.get('webhook_type', 'custom')
    
    if not candidate_id:
        return jsonify({'error': 'candidate_id is required'}), 400
    
    result = ai_integration.send_candidate_data(candidate_id, webhook_type)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@app.route('/api/webhook/callback', methods=['POST'])
def webhook_callback():
    """Callback endpoint for webhooks.
    
    Request body:
        {
            "candidate_id": 1,
            "call_status": "completed",
            "duration": 300,
            "notes": "Interview completed successfully",
            "success": true
        }
    """
    data = request.json
    result = ai_integration.process_webhook_callback(data)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@app.route('/api/call-logs', methods=['GET'])
def list_call_logs():
    """List call logs.
    
    Query parameters:
        - candidate_id: Filter by candidate ID
        - limit: Maximum number of results
    """
    candidate_id = request.args.get('candidate_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    
    logs = data_manager.list_call_logs(candidate_id=candidate_id, limit=limit)
    
    return jsonify({
        'count': len(logs),
        'logs': [log.to_dict() for log in logs]
    })


@app.route('/api/config/webhooks', methods=['GET'])
def get_webhook_config():
    """Get webhook configuration."""
    config = ai_integration.get_webhook_config()
    return jsonify(config)


def run_api():
    """Run the Flask API server."""
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.API_DEBUG
    )


if __name__ == '__main__':
    run_api()
