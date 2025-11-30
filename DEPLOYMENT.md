# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- FastMCP installed (`pip install fastmcp`)
- Required API keys in `.env` file

### Running the Server

#### Option 1: Direct Execution
```bash
python src/server.py
```

#### Option 2: With Custom Arguments
```bash
python src/server.py --transport http --host 0.0.0.0 --port 8000
```

### Testing the Tools

#### Test Competitive Intelligence
```bash
python example_usage.py intelligence
```

#### Test Daily Planning
```bash
python example_usage.py planning
```

### Data Sources

### News Sources
- **NewsAPI**: General news from multiple sources
- **Tech News**: Tech industry news from TechCrunch, The Verge, etc.
- **RSS Feeds**: Custom RSS feeds for specific sources

### Calendar Sources
- **Microsoft Outlook**: Enterprise calendar integration
- **Google Calendar**: Alternative calendar integration (if needed)

## Production Deployment

### FastMCP Cloud (Recommended)

1. Configure FastMCP Cloud credentials
```bash
export FASTMCP_CLOUD_TOKEN=your_token_here
```

2. Deploy to FastMCP Cloud
```bash
fastmcp deploy src/server.py
```

3. Access via FastMCP Cloud
- Your MCP server will be available at a secure URL
- Access through FastMCP Cloud dashboard

### Self-Hosted Deployment

#### Option 1: Basic HTTP Server
```bash
python src/server.py --transport http --host 0.0.0.0 --port 8000
```

#### Option 2: Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

CMD ["python", "src/server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t competitive-intelligence-mcp .
docker run -p 8000:8000 competitive-intelligence-mcp
```

## Cursor Integration

Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "competitive-intelligence": {
      "command": "python",
      "args": ["src/server.py"]
    }
  }
}
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `NEWS_API_KEY`: News API key for competitive intelligence
- `GEMINI_API_KEY`: Google Gemini API key for AI analysis

### Optional
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Google Calendar OAuth credentials
- `JIRA_API_TOKEN` & `JIRA_DOMAIN`: Jira API credentials
- `ASANA_API_TOKEN`: Asana API token
- `DEFAULT_COMPETITORS`: Default competitors to monitor
- `DEFAULT_FOCUS_AREAS`: Default focus areas for analysis
- `DEFAULT_CALENDAR_SOURCE`: Default calendar source (outlook)
- `TECH_NEWS_SOURCES`: Tech news sources (techcrunch,verge)

## Automation Setup

### Cron Jobs
```bash
# Set up cron jobs for daily automation
python schedule_automation.py setup-cron

# Install cron jobs
crontab crontab.txt
```

### Example Cron Configuration
```
# Competitive Intelligence at 6 AM daily
0 6 * * * /usr/bin/python3 /path/to/competitive-intelligence-mcp/run_server.py --get-intelligence

# Daily Planning at 7 AM daily
0 7 * * * /usr/bin/python3 /path/to/competitive-intelligence-mcp/run_server.py --create-plan
```

## Monitoring

### Log Files
- Reports saved to `reports/` directory
- Check logs for errors and performance

### Health Checks
```bash
# Test server health
curl -X POST http://localhost:8000/health -H "Content-Type: application/json" -d '{"test": "health"}'
```
