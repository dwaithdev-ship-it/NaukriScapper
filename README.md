# NaukriScraper

A Python utility to scrape job listings from Naukri.com (India's leading job portal). This tool allows you to search, filter, and export job listings with ease.

## Features

- 🔍 **Search Jobs**: Search by keyword and location
- 📊 **Multiple Export Formats**: Save results as CSV or JSON
- 🎯 **Advanced Filtering**: Filter by experience, company, and location
- ⚡ **Rate Limiting**: Built-in delays to respect server resources
- 🖥️ **CLI Interface**: Easy-to-use command-line interface
- 📦 **Modular Design**: Use as a library or standalone tool

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

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

## Usage

### Command Line Interface

The CLI provides a simple way to scrape jobs directly from the terminal.

#### Basic Usage

```bash
# Search for Python developer jobs
python cli.py --keyword "python developer"

# Search with location filter
python cli.py --keyword "data scientist" --location "bangalore"

# Scrape multiple pages
python cli.py --keyword "software engineer" --pages 3
```

#### Advanced Usage

```bash
# Filter by experience (2-5 years)
python cli.py --keyword "java developer" --min-exp 2 --max-exp 5

# Filter by specific companies
python cli.py --keyword "developer" --companies "Google" "Microsoft" "Amazon"

# Save to custom filename
python cli.py --keyword "analyst" --output my_jobs --format csv

# Verbose mode with detailed output
python cli.py --keyword "devops" --pages 2 --verbose

# Adjust rate limiting (delay between requests)
python cli.py --keyword "manager" --delay 3.0
```

#### CLI Options

```
Required Arguments:
  --keyword, -k      Job search keyword (e.g., "python developer")

Optional Arguments:
  --location, -l     Location filter (e.g., "bangalore", "mumbai")
  --pages, -p        Number of pages to scrape (default: 1)
  --min-exp          Minimum years of experience
  --max-exp          Maximum years of experience
  --companies        Filter by company names (space-separated)
  --output, -o       Output filename without extension (default: naukri_jobs)
  --format, -f       Output format: csv, json, or both (default: both)
  --delay, -d        Delay between requests in seconds (default: 2.0)
  --verbose, -v      Enable verbose output
```

### Python Library

You can also use NaukriScraper as a Python library in your own scripts.

```python
from naukri_scraper import NaukriScraper

# Create scraper instance
scraper = NaukriScraper(delay=2.0)

# Search for jobs
jobs = scraper.search_jobs(
    keyword="python developer",
    location="bangalore",
    max_pages=2
)

# Filter results
filtered_jobs = scraper.filter_jobs(
    min_experience=2,
    max_experience=5,
    locations=["Bangalore", "Mumbai"],
    companies=["Google", "Microsoft"]
)

# Save to files
scraper.save_to_csv("python_jobs.csv")
scraper.save_to_json("python_jobs.json")

# Get detailed job information
if jobs:
    job_url = jobs[0]['link']
    details = scraper.get_job_details(job_url)
    print(details)
```

## Output Format

### CSV Output

Jobs are saved with the following columns:
- `title`: Job title
- `company`: Company name
- `experience`: Required experience
- `salary`: Salary range (if disclosed)
- `location`: Job location
- `description`: Brief job description/skills
- `posted_date`: When the job was posted
- `link`: URL to the job posting

### JSON Output

```json
[
  {
    "title": "Python Developer",
    "company": "Tech Corp",
    "experience": "2-5 Yrs",
    "salary": "₹5-8 Lacs PA",
    "location": "Bangalore",
    "description": "Python, Django, REST API, AWS",
    "posted_date": "1 Day Ago",
    "link": "https://www.naukri.com/job-listings-..."
  }
]
```

## Examples

### Example 1: Search for Remote Jobs

```bash
python cli.py --keyword "remote python developer" --pages 5 --format json
```

### Example 2: Entry-Level Positions

```bash
python cli.py --keyword "software engineer" --max-exp 2 --location "pune"
```

### Example 3: Senior Positions at Top Companies

```bash
python cli.py --keyword "senior developer" --min-exp 7 \
  --companies "Google" "Amazon" "Microsoft" "Facebook" \
  --pages 3 --verbose
```

### Example 4: Data Science Jobs

```bash
python cli.py --keyword "data scientist" --location "hyderabad" \
  --output data_science_jobs --format both --pages 5
```

## Rate Limiting

The scraper includes built-in rate limiting to avoid overwhelming the server:
- Default delay: 2 seconds between requests
- Adjustable via `--delay` parameter or `delay` argument in code
- Recommended: 2-5 seconds for respectful scraping

## Error Handling

The scraper handles common errors gracefully:
- Network timeouts
- Invalid responses
- Missing data fields
- Rate limiting issues

## Limitations

- Naukri.com may update their website structure, which could break the scraper
- Some job details may not be available for all listings
- Rate limiting is important to avoid IP blocking
- Scraping should be done responsibly and in accordance with Naukri.com's terms of service

## Dependencies

- `requests`: HTTP library for making web requests
- `beautifulsoup4`: HTML parsing library
- `lxml`: XML/HTML parser
- `pandas`: Data manipulation and CSV export
- `selenium`: Web automation (for JavaScript-heavy pages)
- `webdriver-manager`: Automatic webdriver management

## Troubleshooting

### Issue: No jobs found
- Check your internet connection
- Verify the keyword spelling
- Try broader search terms
- Reduce the number of pages

### Issue: Parsing errors
- Naukri.com may have changed their HTML structure
- Update the parsing logic in `naukri_scraper.py`
- Check for updates to this repository

### Issue: Rate limiting/blocking
- Increase the delay between requests
- Use a VPN or different IP address
- Reduce the number of pages being scraped

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Legal Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their use of this tool complies with Naukri.com's Terms of Service and applicable laws. The authors are not responsible for any misuse of this tool.

Web scraping should be done ethically and responsibly:
- Respect robots.txt
- Use reasonable rate limiting
- Don't overload the server
- Follow the website's terms of service

## License

This project is open source and available under the MIT License.

## Author

Created by dwaithdev-ship-it

## Acknowledgments

- Naukri.com for providing the job listings platform
- BeautifulSoup and Requests libraries for making web scraping easier