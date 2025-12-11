# NaukriScapper

A Python web scraping utility for Naukri.com with REST API, database management, and AI integration via webhooks.

## Features

- 🔍 **Web Scraping**: Scrape job listings from Naukri.com
- 🗄️ **Database Management**: SQLAlchemy ORM with JobSearch, Candidate, and CallLog models
- 🌐 **REST API**: Flask-based API for programmatic access
- 🤖 **AI Integration**: Webhook support for n8n, Make.com, and custom integrations
- 🔒 **Security**: SSRF protection for webhook URLs
- 📊 **Export**: Export data to CSV and JSON formats
- 🎯 **Filtering**: Advanced filtering by experience, skills, and location
- 💻 **CLI**: Command-line interface for all operations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dwaithdev-ship-it/NaukriScapper.git
cd NaukriScapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

### Command Line Interface

**Scrape jobs:**
```bash
python cli.py scrape "Python developer" --location Bangalore --max-pages 2 --export-csv jobs.csv
```

**List records:**
```bash
python cli.py list searches
python cli.py list candidates
python cli.py list call-logs
```

**Start API server:**
```bash
python cli.py api --host 0.0.0.0 --port 5000
```

**Webhook operations:**
```bash
python cli.py webhook config
python cli.py webhook send --candidate-id 1 --webhook-type n8n
```

### Python API

```python
from naukri_scraper import NaukriScraper
from data_manager import DataManager

# Scrape jobs
scraper = NaukriScraper(delay=2.0)
jobs = scraper.search_jobs(
    keyword='Python developer',
    location='Bangalore',
    max_pages=2
)

# Filter jobs
filtered = scraper.filter_jobs(
    min_experience=2,
    max_experience=5,
    required_skills=['Python', 'Django']
)

# Export to CSV
scraper.export_to_csv('jobs.csv', filtered)

# Database operations
data_manager = DataManager()
candidate = data_manager.create_candidate(
    name='John Doe',
    email='john@example.com',
    experience=3.5,
    skills='Python, Django, Flask'
)
```

### REST API

Start the API server:
```bash
python api.py
# or
python cli.py api
```

**API Endpoints:**

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/scrape` - Scrape jobs
- `GET /api/searches` - List job searches
- `POST /api/candidates` - Create candidate
- `GET /api/candidates` - List candidates
- `GET /api/candidates/search` - Search candidates
- `POST /api/webhook/send` - Send data to webhook
- `POST /api/webhook/callback` - Webhook callback endpoint
- `GET /api/call-logs` - List call logs

**Example API request:**
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Python developer",
    "location": "Bangalore",
    "max_pages": 1
  }'
```

## Configuration

Configuration is managed through environment variables or the `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///naukri_scraper.db

# Scraping
DEFAULT_DELAY=2.0
MAX_RETRIES=3
TIMEOUT=30

# API
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# AI Integration
WEBHOOK_URL=https://your-webhook.com/callback
N8N_WEBHOOK_URL=https://hooks.n8n.cloud/webhook/your-id
MAKE_WEBHOOK_URL=https://hook.us1.make.com/your-id

# Security (set to False in production!)
ALLOW_LOCAL_WEBHOOKS=False

# Export
EXPORT_DIR=./exports
```

## AI Integration

NaukriScapper supports webhook integration with:
- **n8n**: Workflow automation platform
- **Make.com** (formerly Integromat): Integration platform
- **Custom webhooks**: Any HTTP endpoint

### Security

SSRF protection is enabled by default to prevent Server-Side Request Forgery attacks. See [SECURITY.md](SECURITY.md) for details.

## Testing

Run tests:
```bash
python test_scraper.py
```

All tests should pass:
```
....................
----------------------------------------------------------------------
Ran 11 tests in 0.XXXs

OK
```

## Examples

See `example.py` for comprehensive usage examples:
```bash
python example.py
```

## Project Structure

```
NaukriScapper/
├── naukri_scraper.py    # Core scraping functionality
├── models.py            # Database models (SQLAlchemy)
├── data_manager.py      # Data management operations
├── config.py            # Configuration management
├── ai_integration.py    # AI webhook integration
├── api.py               # REST API (Flask)
├── cli.py               # Command-line interface
├── test_scraper.py      # Unit tests
├── example.py           # Usage examples
├── requirements.txt     # Python dependencies
├── SECURITY.md          # Security guidelines
└── README.md            # This file
```

## Database Models

### JobSearch
Stores job search queries and metadata

### Candidate
Stores candidate profile data

### CallLog
Tracks AI call logs and webhook responses

## CLI Commands

### Scrape
```bash
python cli.py scrape KEYWORD [OPTIONS]

Options:
  --location TEXT          Job location
  --experience TEXT        Experience level
  --salary TEXT           Salary range
  --max-pages INT         Maximum pages to scrape
  --delay FLOAT           Delay between requests
  --min-experience FLOAT  Minimum experience filter
  --max-experience FLOAT  Maximum experience filter
  --skills TEXT           Required skills (comma-separated)
  --filter-location TEXT  Filter by location
  --export-csv FILE       Export to CSV
  --export-json FILE      Export to JSON
  --limit INT             Limit displayed results
  --quiet                 Suppress output
```

### List
```bash
python cli.py list {searches|candidates|call-logs} [OPTIONS]

Options:
  --limit INT  Maximum records to display
```

### API
```bash
python cli.py api [OPTIONS]

Options:
  --host TEXT    Host to bind to
  --port INT     Port to bind to
  --debug        Enable debug mode
```

### Webhook
```bash
python cli.py webhook {send|config} [OPTIONS]

Options:
  --candidate-id INT              Candidate ID (for send)
  --webhook-type {n8n|make|custom}  Webhook type
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

See [SECURITY.md](SECURITY.md) for security guidelines and best practices.

## License

MIT License - see LICENSE file for details

## Author

Dwaith Dev (dwaith.dev@gmail.com)

## Disclaimer

This tool is for educational and legitimate job searching purposes only. Always respect:
- Website terms of service
- Rate limiting and robots.txt
- Privacy and data protection laws
- Ethical scraping practices

Use responsibly and in accordance with Naukri.com's terms of service.