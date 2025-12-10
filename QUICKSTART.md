# Quick Start Guide

Get up and running with Naukri Scraper in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Chrome or Firefox browser

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dwaithdev-ship-it/NaukriScapper.git
cd NaukriScapper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Add your Naukri employer credentials:
```bash
NAUKRI_USERNAME=your_employer_email@example.com
NAUKRI_PASSWORD=your_password
```

### 4. Initialize Database

```bash
python cli.py init
```

## Basic Usage

### Search for Candidates (Demo with Sample Data)

Since actual Naukri scraping requires employer portal access, let's start with sample data:

```bash
python example_usage.py
```

This will:
- Create a job search
- Add sample candidates
- Export to Excel
- Show statistics

### View the Results

Check the `exports/` directory for the Excel file with candidate data.

## Using Real Naukri Data

Once you have valid employer credentials:

```bash
python cli.py search \
  --job-role "Python Developer" \
  --exp-min 2 \
  --exp-max 5 \
  --location "Bangalore" \
  --max-results 20
```

This will:
1. Login to Naukri employer portal
2. Search for matching candidates
3. Save profiles to database
4. Export to Excel

## Managing Candidates

### List All Candidates

```bash
python cli.py list-candidates --job-search-id 1
```

### Update Candidate Status

```bash
python cli.py update \
  --candidate-id 1 \
  --contacted true \
  --interested true \
  --comments "Scheduled interview for next week"
```

### View Statistics

```bash
python cli.py stats --job-search-id 1
```

### Export to Excel

```bash
python cli.py export --job-search-id 1 --output my_candidates.xlsx
```

## Using the REST API

### Start API Server

```bash
python cli.py serve
```

Or directly:
```bash
python api.py
```

The API will be available at `http://localhost:5000`

### Test API

```bash
# Health check
curl http://localhost:5000/health

# Create job search
curl -X POST http://localhost:5000/api/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "job_role": "Python Developer",
    "experience_min": 2,
    "experience_max": 5,
    "location": "Bangalore"
  }'

# Get candidates
curl http://localhost:5000/api/candidates/1
```

## AI Integration (Optional)

### Setup n8n

1. Install n8n:
```bash
npm install -g n8n
n8n start
```

2. Create a webhook in n8n and copy the URL

3. Add to .env:
```bash
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/naukri
WEBHOOK_SECRET=your-secret-key
```

### Trigger Automated Calls

```bash
python cli.py trigger-calls \
  --job-search-id 1 \
  --ai-tool n8n \
  --job-role "Python Developer" \
  --company-name "Tech Corp"
```

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed AI integration instructions.

## Python API Usage

```python
from naukri_scraper import NaukriEmployerScraper
from data_manager import DataManager

# Initialize
scraper = NaukriEmployerScraper(
    username="employer@example.com",
    password="password"
)

# Login and search
if scraper.login():
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
        location="Bangalore"
    )
    dm.add_candidates_bulk(job_search.id, candidates)
    
    # Export
    dm.export_to_excel(job_search.id)
    
    dm.close()

scraper.close()
```

## Common Tasks

### Add Candidates Manually

```python
from data_manager import DataManager

dm = DataManager()
job_search = dm.create_job_search(job_role="Developer")

candidate_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+91-9876543210',
    'experience_years': 3.5,
    'skills': 'Python, Django, REST API'
}

dm.add_candidate(job_search.id, candidate_data)
dm.close()
```

### Query Database

```python
from models import get_session, Candidate, JobSearch

session = get_session()

# Get all candidates with 3+ years experience
candidates = session.query(Candidate).filter(
    Candidate.experience_years >= 3.0
).all()

for c in candidates:
    print(f"{c.name} - {c.experience_years} years")

session.close()
```

## Directory Structure

```
NaukriScapper/
├── api.py                 # REST API server
├── cli.py                 # Command-line interface
├── config.py              # Configuration
├── models.py              # Database models
├── naukri_scraper.py      # Core scraper
├── data_manager.py        # Data management
├── ai_integration.py      # AI/webhook integration
├── test_scraper.py        # Unit tests
├── example_usage.py       # Example scripts
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README.md             # Full documentation
├── QUICKSTART.md         # This file
└── INTEGRATION_GUIDE.md  # AI integration guide
```

## Next Steps

1. **Read the full [README.md](README.md)** for comprehensive documentation
2. **Set up AI integration** using [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
3. **Run tests** to verify everything works: `python test_scraper.py`
4. **Customize** the call script in `config.py`
5. **Explore** the API endpoints in `api.py`

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Errors

```bash
# Reinitialize database
rm naukri_profiles.db
python cli.py init
```

### Browser Driver Issues

```bash
# Update webdriver-manager
pip install --upgrade selenium webdriver-manager
```

### Login Failures

- Verify credentials in .env file
- Try running in non-headless mode: `--no-headless` flag
- Check if Naukri has updated their login page

## Getting Help

- **Documentation**: [README.md](README.md)
- **AI Integration**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Examples**: Run `python example_usage.py`
- **Tests**: Run `python test_scraper.py`
- **Issues**: Open an issue on GitHub

## Security Note

⚠️ Never commit your `.env` file to version control. It contains sensitive credentials.

## License

MIT License - See LICENSE file for details
