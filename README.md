# Naukri Employer Automation Utility

A comprehensive Python-based automation utility for Naukri.com employer portal that enables automated candidate profile searching, data management, Excel export, and AI-powered call integration.

## Features

- 🔐 **Employer Login**: Secure authentication to Naukri employer portal
- 🔍 **Advanced Search**: Search candidates by job role, experience, location, and job type
- 💾 **Data Storage**: SQLite database for storing candidate profiles and tracking
- 📊 **Excel Export**: Generate formatted Excel spreadsheets with candidate details
- 🤖 **AI Integration**: Built-in webhook support for n8n, make.com, and custom AI tools
- 📞 **Automated Calling**: Trigger automated calls to candidates with custom scripts
- 📈 **Status Tracking**: Track contacted candidates, interested responses, and interview scheduling
- 🌐 **REST API**: Full-featured API for external integrations
- 💻 **CLI Interface**: Command-line interface for easy operation

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser (for Selenium)
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dwaithdev-ship-it/NaukriScapper.git
cd NaukriScapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file with your credentials and settings:
```bash
# Naukri Employer Credentials
NAUKRI_USERNAME=your_employer_email@example.com
NAUKRI_PASSWORD=your_password

# AI Integration (optional)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/naukri
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-id
WEBHOOK_SECRET=your-webhook-secret
```

5. Initialize the database:
```bash
python cli.py init
```

## Usage

### Command-Line Interface

#### Search for Candidates

```bash
python cli.py search \
  --username employer@example.com \
  --password yourpassword \
  --job-role "Python Developer" \
  --exp-min 2 \
  --exp-max 5 \
  --location "Bangalore" \
  --max-results 50
```

#### List Candidates

```bash
python cli.py list-candidates --job-search-id 1
```

#### Export to Excel

```bash
python cli.py export --job-search-id 1 --output candidates.xlsx
```

#### View Statistics

```bash
python cli.py stats --job-search-id 1
```

#### Update Candidate Status

```bash
python cli.py update --candidate-id 1 --contacted true --interested true --comments "Interested in the role"
```

#### Trigger Automated Calls

```bash
python cli.py trigger-calls \
  --job-search-id 1 \
  --ai-tool n8n \
  --job-role "Python Developer" \
  --company-name "Tech Corp"
```

#### Start API Server

```bash
python cli.py serve --host 0.0.0.0 --port 5000
```

### REST API

Start the API server:

```bash
python api.py
```

#### API Endpoints

**Health Check**
```
GET /health
```

**Create Job Search**
```
POST /api/job-search
Content-Type: application/json

{
  "job_role": "Python Developer",
  "experience_min": 2.0,
  "experience_max": 5.0,
  "location": "Bangalore",
  "job_type": "Full-time"
}
```

**Add Candidate**
```
POST /api/candidates
Content-Type: application/json

{
  "job_search_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "experience_years": 3.5
}
```

**Get Candidates**
```
GET /api/candidates/<job_search_id>
```

**Update Candidate Status**
```
PUT /api/candidates/<candidate_id>/status
Content-Type: application/json

{
  "contacted": true,
  "interested": true,
  "comments": "Interested in the role"
}
```

**Export to Excel**
```
GET /api/export/<job_search_id>
```

**Trigger Automated Calls**
```
POST /api/ai/trigger-calls
Content-Type: application/json

{
  "candidate_ids": [1, 2, 3],
  "job_data": {
    "job_role": "Python Developer",
    "location": "Bangalore"
  },
  "ai_tool": "n8n"
}
```

**Webhook Callback (for AI tools)**
```
POST /api/webhook/callback
Content-Type: application/json

{
  "candidate_id": 1,
  "call_status": "completed",
  "interested": true,
  "response": "Candidate is interested",
  "secret": "your_webhook_secret"
}
```

### Python API

```python
from naukri_scraper import NaukriEmployerScraper
from data_manager import DataManager
from ai_integration import AIIntegration

# Initialize scraper
scraper = NaukriEmployerScraper(
    username="employer@example.com",
    password="password"
)

# Login
if scraper.login():
    # Search candidates
    candidates = scraper.search_candidates(
        job_role="Python Developer",
        experience_min=2,
        experience_max=5,
        location="Bangalore"
    )
    
    # Save to database
    dm = DataManager()
    job_search = dm.create_job_search(
        job_role="Python Developer",
        experience_min=2,
        experience_max=5,
        location="Bangalore"
    )
    dm.add_candidates_bulk(job_search.id, candidates)
    
    # Export to Excel
    excel_file = dm.export_to_excel(job_search.id)
    print(f"Exported to: {excel_file}")
    
    dm.close()

scraper.close()
```

## AI Integration

### n8n Integration

1. Create a webhook node in n8n
2. Set the webhook URL in `.env` file
3. Configure the webhook to receive candidate data
4. Use the response webhook to send back call results

**Example n8n Workflow:**
- Webhook Trigger (receives candidate data)
- AI Voice Call Node (makes the call)
- HTTP Request Node (sends results back to `/api/webhook/callback`)

### make.com Integration

1. Create a new scenario in make.com
2. Add a webhook module
3. Configure the webhook URL in `.env` file
4. Add modules for calling and processing responses
5. Send results back to the callback endpoint

### Custom Integration

Send candidate data to any webhook URL:

```python
from ai_integration import AIIntegration

ai = AIIntegration()
candidate_data = {
    'name': 'John Doe',
    'phone': '+91-9876543210',
    'email': 'john@example.com'
}

response = ai.send_to_webhook(
    webhook_url='https://your-webhook-url.com',
    candidate_data=candidate_data,
    script='Your custom call script'
)
```

## Database Schema

The application uses SQLite with the following tables:

- **job_searches**: Store job search queries
- **candidates**: Store candidate profiles
- **call_logs**: Track AI call interactions

## Excel Export Format

The exported Excel file includes:
- Candidate ID
- Name, Email, Phone
- Location, Experience
- Current Company and Designation
- Skills, Education
- Contact Status (Contacted, Interested, Interview Scheduled)
- Comments
- Timestamps

## Security

- Store credentials in `.env` file (never commit this file)
- Use webhook secrets for AI integrations
- API endpoints can be protected with authentication
- All passwords are hidden in CLI prompts

## Configuration

Edit `config.py` or use environment variables to configure:

- Database URL
- Request delays (rate limiting)
- Browser settings (headless mode, browser type)
- API settings (host, port, debug mode)
- Webhook URLs and secrets

## Rate Limiting

Default delay between requests is 2.0 seconds to avoid overwhelming the server. Adjust `REQUEST_DELAY` in `.env` or `config.py`.

## Troubleshooting

**Browser driver issues:**
```bash
# The webdriver-manager package automatically downloads drivers
# If issues persist, try updating:
pip install --upgrade selenium webdriver-manager
```

**Database issues:**
```bash
# Reinitialize the database:
python cli.py init
```

**Login failures:**
- Verify credentials in `.env` file
- Check if Naukri has changed their login page structure
- Try running in non-headless mode for debugging

## Development

### Project Structure

```
NaukriScapper/
├── api.py              # REST API using Flask
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── models.py           # Database models
├── naukri_scraper.py   # Core scraper logic
├── data_manager.py     # Data storage and export
├── ai_integration.py   # AI/webhook integration
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment config
└── README.md          # Documentation
```

### Running Tests

```bash
# Add tests in test_*.py files
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational and legitimate business purposes only. Always comply with Naukri.com's Terms of Service and respect candidate privacy. Use appropriate rate limiting and obtain necessary permissions before contacting candidates.

## Support

For issues and questions, please open an issue on GitHub.