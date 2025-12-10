# AI Integration Guide

This guide explains how to integrate Naukri Scraper with various AI automation platforms for automated candidate calling and interview scheduling.

## Overview

The Naukri Scraper supports webhooks and API integrations with popular automation platforms:
- **n8n**: Open-source workflow automation
- **make.com**: Visual automation platform
- **Custom**: Any webhook-compatible service

## Integration Flow

```
Naukri Scraper → AI Platform → Voice Call → Response → Callback → Database Update
```

## n8n Integration

### Setup

1. **Install n8n** (if not already installed):
```bash
npm install -g n8n
n8n start
```

2. **Create a Workflow**:
   - Add a Webhook node as trigger
   - Configure it to listen for POST requests
   - Copy the webhook URL

3. **Configure Naukri Scraper**:
```bash
# In .env file
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/naukri
WEBHOOK_SECRET=your-secret-key
```

### Example n8n Workflow

#### Nodes Structure:
1. **Webhook (Trigger)**
   - Method: POST
   - Path: /naukri
   - Response Mode: onReceived

2. **Set Node** (Extract Data)
   ```json
   {
     "candidate_name": "={{ $json.candidate.name }}",
     "candidate_phone": "={{ $json.candidate.phone }}",
     "call_script": "={{ $json.script }}"
   }
   ```

3. **HTTP Request** (Make Call - Using Twilio/VoiceAI)
   - Method: POST
   - URL: Your voice service API
   - Body:
   ```json
   {
     "to": "={{ $node['Set'].json.candidate_phone }}",
     "message": "={{ $node['Set'].json.call_script }}"
   }
   ```

4. **IF Node** (Check Call Success)
   - Condition: `{{ $json.status }} == 'completed'`

5. **HTTP Request** (Send Result Back)
   - Method: POST
   - URL: http://your-scraper-api:5000/api/webhook/callback
   - Body:
   ```json
   {
     "candidate_id": "={{ $node['Webhook'].json.candidate.id }}",
     "call_status": "completed",
     "interested": true,
     "response": "={{ $json.response_text }}",
     "secret": "your-webhook-secret"
   }
   ```

### Triggering Calls from Naukri Scraper

```python
from ai_integration import AIIntegration

ai = AIIntegration()

# Trigger calls for specific candidates
ai.trigger_automated_calls(
    candidate_ids=[1, 2, 3],
    job_data={
        'job_role': 'Python Developer',
        'location': 'Bangalore',
        'company_name': 'Tech Corp'
    },
    ai_tool='n8n'
)
```

Or via CLI:
```bash
python cli.py trigger-calls \
  --job-search-id 1 \
  --ai-tool n8n \
  --job-role "Python Developer" \
  --company-name "Tech Corp"
```

Or via REST API:
```bash
curl -X POST http://localhost:5000/api/ai/trigger-calls \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_ids": [1, 2, 3],
    "job_data": {
      "job_role": "Python Developer",
      "location": "Bangalore"
    },
    "ai_tool": "n8n"
  }'
```

## make.com Integration

### Setup

1. **Create a Scenario**:
   - Go to make.com and create a new scenario
   - Add a Webhook module
   - Copy the webhook URL

2. **Configure Naukri Scraper**:
```bash
# In .env file
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-id
WEBHOOK_SECRET=your-secret-key
```

### Example Scenario

#### Modules:
1. **Webhook** (Instant Trigger)
   - Copy the webhook URL
   - Configure to accept JSON

2. **Voice AI Service** (e.g., Twilio, Bland.ai)
   - Phone Number: `candidate.phone`
   - Message: `script`
   - Wait for response: Yes

3. **Parse Response**
   - Extract: interest_level, response_text

4. **HTTP Request** (Callback)
   - URL: http://your-scraper-api:5000/api/webhook/callback
   - Method: POST
   - Body:
   ```json
   {
     "candidate_id": "{{candidate.id}}",
     "call_status": "{{call_status}}",
     "interested": "{{interested}}",
     "response": "{{response_text}}",
     "secret": "your-webhook-secret"
   }
   ```

### Triggering Calls

```python
ai.trigger_automated_calls(
    candidate_ids=[1, 2, 3],
    job_data={'job_role': 'Python Developer'},
    ai_tool='make'
)
```

## Custom Integration

For custom webhook services:

```python
from ai_integration import AIIntegration

ai = AIIntegration()

# Send to custom webhook
ai.trigger_automated_calls(
    candidate_ids=[1, 2, 3],
    job_data={'job_role': 'Python Developer'},
    ai_tool='custom',
    custom_webhook='https://your-custom-service.com/webhook'
)
```

### Custom Webhook Payload

The Naukri Scraper sends the following JSON payload:

```json
{
  "candidate": {
    "id": 1,
    "name": "John Doe",
    "phone": "+91-9876543210",
    "email": "john@example.com",
    "experience_years": 3.5,
    "current_company": "Tech Corp",
    "skills": "Python, Django, REST API"
  },
  "script": "Hello John Doe, this is regarding the Python Developer position...",
  "timestamp": "2024-01-01T10:00:00Z",
  "source": "naukri_scraper",
  "secret": "your-webhook-secret"
}
```

### Expected Callback Format

Your service should send results back to:
`POST http://your-api:5000/api/webhook/callback`

```json
{
  "candidate_id": 1,
  "call_status": "completed",
  "interested": true,
  "response": "Candidate is very interested in the position",
  "secret": "your-webhook-secret",
  "ai_tool": "custom"
}
```

## Voice AI Services

### Recommended Services

1. **Twilio**
   - Programmable Voice API
   - Text-to-Speech
   - Call recording

2. **Bland.ai**
   - AI-powered phone calls
   - Natural conversation
   - Intent detection

3. **Vapi.ai**
   - Voice AI for calling
   - Real-time transcription
   - Sentiment analysis

4. **Synthflow.ai**
   - No-code voice AI
   - Easy integration
   - Call analytics

### Example Twilio Integration in n8n

```javascript
// Twilio node configuration
{
  "from": "+1234567890", // Your Twilio number
  "to": "{{ $json.candidate.phone }}",
  "url": "http://your-server.com/twiml-response.xml"
}
```

## Call Script Customization

### Default Script Template

The default script is defined in `config.py`:

```python
DEFAULT_CALL_SCRIPT = """
Hello {candidate_name},

This is regarding the {job_role} position at our company.
We found your profile on Naukri and would like to discuss this opportunity with you.

Are you interested in exploring this opportunity?
"""
```

### Custom Script

You can provide custom scripts when triggering calls:

```python
custom_script = """
Hi {candidate_name},

I'm calling from {company_name} about an exciting {job_role} position 
in {location}. We noticed you have {experience_years} years of experience.

Would you be available for a quick chat this week?
"""

ai.trigger_automated_calls(
    candidate_ids=[1, 2, 3],
    job_data={
        'job_role': 'Senior Python Developer',
        'location': 'Bangalore',
        'company_name': 'Innovative Tech Solutions'
    },
    custom_script=custom_script,
    ai_tool='n8n'
)
```

## Response Processing

### Interest Detection

You can use AI to detect candidate interest from responses:

1. **Rule-based**:
   - Keywords: "interested", "yes", "sure", "tell me more"
   - Anti-keywords: "not interested", "no", "busy"

2. **AI-based** (using GPT/Claude):
   - Send transcript to LLM
   - Ask: "Is the candidate interested? Yes/No"
   - Get structured response

### Example in n8n

Add an OpenAI node after the call:

```javascript
// Prompt
`Analyze this call transcript and determine if the candidate is interested in the job. 
Transcript: {{ $json.transcript }}
Respond with only: YES, NO, or MAYBE`

// Then map to boolean
interested = response.trim().toUpperCase() === 'YES'
```

## Monitoring and Analytics

### Track Call Performance

Query the database for analytics:

```python
from data_manager import DataManager

dm = DataManager()

# Get call statistics
stats = dm.get_statistics(job_search_id=1)
print(f"Total candidates: {stats['total_candidates']}")
print(f"Contacted: {stats['contacted']}")
print(f"Interested: {stats['interested']}")

# Get all call logs
from models import CallLog
call_logs = dm.session.query(CallLog).all()
for log in call_logs:
    print(f"Candidate {log.candidate_id}: {log.call_status}")
```

### Export Call Results

```bash
python cli.py export --job-search-id 1 --output call_results.xlsx
```

## Security Best Practices

1. **Use HTTPS**: Always use HTTPS for webhooks
2. **Webhook Secrets**: Verify webhook authenticity using secrets
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Data Encryption**: Encrypt sensitive candidate data
5. **Access Control**: Restrict API access with authentication

## Troubleshooting

### Webhook Not Receiving Data

1. Check webhook URL is correct
2. Verify firewall/network settings
3. Test with curl:
```bash
curl -X POST https://your-webhook-url \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Calls Not Being Made

1. Check AI tool configuration
2. Verify webhook URL in .env
3. Check logs: `tail -f api.log`
4. Test webhook manually

### Callback Not Updating Database

1. Verify callback URL is accessible
2. Check webhook secret matches
3. Ensure candidate_id is correct
4. Check API logs for errors

## Advanced Usage

### Batch Processing

Process candidates in batches:

```python
from ai_integration import AIIntegration

ai = AIIntegration()

# Get candidates not yet contacted
candidate_ids = ai.get_candidates_for_calling(
    job_search_id=1,
    contacted_only=False
)

# Process in batches of 10
batch_size = 10
for i in range(0, len(candidate_ids), batch_size):
    batch = candidate_ids[i:i+batch_size]
    ai.trigger_automated_calls(
        candidate_ids=batch,
        job_data={'job_role': 'Python Developer'},
        ai_tool='n8n'
    )
    time.sleep(60)  # Wait between batches
```

### Retry Failed Calls

```python
from models import CallLog

# Get failed calls
failed_calls = dm.session.query(CallLog).filter(
    CallLog.call_status == 'failed'
).all()

# Retry
candidate_ids = [log.candidate_id for log in failed_calls]
ai.trigger_automated_calls(candidate_ids, job_data, ai_tool='n8n')
```

## Support

For integration issues:
1. Check the [README.md](README.md) for general setup
2. Review API documentation in [api.py](api.py)
3. Open an issue on GitHub with logs and configuration (remove secrets!)
