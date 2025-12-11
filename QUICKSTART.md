# Quick Start Guide

Get up and running with NaukriScapper in 5 minutes!

## 1. Installation

```bash
# Clone the repository
git clone https://github.com/dwaithdev-ship-it/NaukriScapper.git
cd NaukriScapper

# Install dependencies
pip install -r requirements.txt
```

## 2. Verify Installation

Run the demo to verify everything is working:

```bash
python run_demo.py
```

You should see:
```
================================================================================
  Demo Completed Successfully!
================================================================================
```

## 3. Run Tests

```bash
python test_scraper.py
```

Expected output: `Ran 11 tests in X.XXXs - OK`

## 4. Try the Examples

```bash
# Run usage examples
python example.py
```

## 5. Start the API Server

```bash
# Start the REST API server
python cli.py api

# Or directly
python api.py
```

The API will be available at `http://localhost:5000`

Test it:
```bash
curl http://localhost:5000/health
```

## 6. Use the CLI

### Scrape jobs (requires network access)
```bash
python cli.py scrape "Python developer" --location Bangalore --max-pages 1
```

### List database records
```bash
python cli.py list candidates
python cli.py list searches
python cli.py list call-logs
```

### Manage webhooks
```bash
python cli.py webhook config
```

## 7. Configuration (Optional)

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` to customize:
- Database URL
- API host/port
- Webhook URLs
- Security settings

## Common Commands

| Command | Description |
|---------|-------------|
| `python test_scraper.py` | Run unit tests |
| `python run_demo.py` | Run comprehensive demo |
| `python example.py` | Run usage examples |
| `python cli.py api` | Start API server |
| `python cli.py scrape "keyword"` | Scrape jobs |
| `python cli.py list [type]` | List records |
| `python cli.py webhook config` | Show webhook config |

## API Endpoints

Once the API is running, try these:

```bash
# Health check
curl http://localhost:5000/health

# API information
curl http://localhost:5000/

# List candidates
curl http://localhost:5000/api/candidates

# Create a candidate
curl -X POST http://localhost:5000/api/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "experience": 5.0,
    "skills": "Python, Django, Flask",
    "location": "Bangalore"
  }'
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [SECURITY.md](SECURITY.md) for security best practices
- Customize `.env` for your environment
- Explore the Python API in `example.py`

## Troubleshooting

### Dependencies not installing?
```bash
# Use pip with user flag
pip install --user -r requirements.txt
```

### Database errors?
```bash
# Delete the database and let it recreate
rm naukri_scraper.db
python run_demo.py
```

### Import errors?
Make sure you're in the project directory:
```bash
cd /path/to/NaukriScapper
python -c "import naukri_scraper; print('OK')"
```

## Support

For issues or questions:
- Check [README.md](README.md) for detailed documentation
- Review [SECURITY.md](SECURITY.md) for security guidelines
- Contact: dwaith.dev@gmail.com

Happy scraping! 🚀
