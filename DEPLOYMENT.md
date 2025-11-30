# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- FastMCP installed (`pip install fastmcp`)
- Required API keys in `.env` file

### Running Server

#### Option 1: Direct Execution
```bash
python src/server.py
```

#### Option 2: With Custom Arguments
```bash
python src/server.py --transport http --host 0.0.0.0 --port 8000
```

### Testing Tools

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

FastMCP Cloud is a managed platform for hosting MCP servers. It's the fastest way to deploy your server and make it available to LLM clients like Claude and Cursor.

#### Prerequisites
- A GitHub account
- A GitHub repository containing your FastMCP server
- Required environment variables configured in your repository

#### Step 1: Prepare Your Repository
1. Ensure your repository has a `pyproject.toml` or `requirements.txt` file with dependencies
2. Create a `.env.example` file documenting required environment variables
3. Make sure your server file exports a FastMCP instance (see `fastmcp_server.py`)

#### Step 2: Deploy to FastMCP Cloud
1. Visit [fastmcp.cloud](https://fastmcp.cloud) and sign in with your GitHub account
2. Create a new project and select your repository
3. Configure your project:
   - **Name**: Competitive Intelligence & Daily Planning
   - **Entrypoint**: `fastmcp_server.py:mcp` (points to the mcp instance in fastmcp_server.py)
   - **Authentication**: Enable if you want to restrict access to your organization members

#### Step 3: Configure Environment Variables
In the FastMCP Cloud dashboard, add the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `NEWS_API_KEY`: Your News API key (required)
- Optional: Google Calendar, Jira, and Asana credentials if using those integrations

#### Step 4: Connect to Your Server
Once deployed, your server will be available at a URL like:
```
https://your-project-name.fastmcp.app/mcp
```

You can connect to it using the FastMCP Cloud dashboard connection options or by adding it to your Cursor MCP configuration.

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

### For FastMCP Cloud Deployment
Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "competitive-intelligence": {
      "command": "npx",
      "args": ["-y", "@fastmcp/cli", "connect", "https://your-project-name.fastmcp.app/mcp"]
    }
  }
}
```

### For Local Development
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
- `GEMINI_API_KEY`: Google Gemini API key for AI analysis
- `NEWS_API_KEY`: News API key for competitive intelligence

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
