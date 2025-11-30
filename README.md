# Competitive Intelligence & Daily Planning MCP Tool

A FastMCP server that provides AI-powered competitive intelligence and daily planning capabilities.

## Features

### Competitive Intelligence
- Automated monitoring of competitor activities
- News aggregation from multiple sources
- AI-powered analysis and summarization
- Structured report generation
- Focus on key areas (pricing, product launches, partnerships)

### Daily Planning
- Calendar integration with OAuth authentication
- Task prioritization based on multiple factors
- Time-blocking and schedule optimization
- Identification of 2-3 most impactful daily activities
- Contextual recommendations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/competitive-intelligence-mcp.git
cd competitive-intelligence-mcp
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

## Configuration

Edit the `.env` file with your settings:

```bash
# API Keys
NEWS_API_KEY=your_news_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Google Calendar OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Jira API
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_DOMAIN=your_domain.atlassian.net

# Asana API
ASANA_API_TOKEN=your_asana_api_token_here

# Configuration
DEFAULT_COMPETITORS=competitor1,competitor2,competitor3
DEFAULT_FOCUS_AREAS=pricing,product_launches,partnerships
DEFAULT_CALENDAR_SOURCE=google
```

## Usage

### Running the Server

Start the FastMCP server:

```bash
python src/server.py
```

### Using with Cursor

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

## Available Tools

### Competitive Intelligence Tools

#### `get_competitive_intelligence`
Gather competitive intelligence for specified competitors.

**Parameters:**
- `competitors` (required): List of competitor names to monitor
- `date_range` (optional): Date range for analysis (default: last 24 hours)
- `focus_areas` (optional): Specific areas to focus on

**Example:**
```python
get_competitive_intelligence(
    competitors=["CompetitorA", "CompetitorB"],
    focus_areas=["pricing", "product_launches"]
)
```

### Daily Planning Tools

#### `create_daily_plan`
Create a focused daily plan based on calendar, tasks, and priorities.

**Parameters:**
- `calendar_source` (optional): Calendar service to use (google, outlook)
- `task_sources` (optional): Task management systems to integrate (jira, asana, email)
- `focus_areas` (optional): Areas to prioritize (strategic, operational, learning)
- `time_available_hours` (optional): Available hours for the day

**Example:**
```python
create_daily_plan(
    calendar_source="google",
    task_sources=["jira", "email"],
    focus_areas=["strategic", "operational"],
    time_available_hours=8
)
```

#### `schedule_morning_intelligence`
Schedule automated morning intelligence gathering and daily planning.

**Parameters:**
- `time` (optional): Time to run automation (HH:MM format)
- `competitors` (optional): List of competitors to monitor
- `calendar_source` (optional): Calendar service for daily planning

**Example:**
```python
schedule_morning_intelligence(
    time="06:00",
    competitors=["CompetitorA", "CompetitorB"],
    calendar_source="google"
)
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## API Setup

### News API
1. Sign up at [NewsAPI.org](https://newsapi.org/)
2. Get your API key
3. Add to `.env` file as `NEWS_API_KEY`

### OpenAI API
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Get your API key
3. Add to `.env` file as `OPENAI_API_KEY`

### Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add to `.env` file as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### Jira API
1. Get API token from your Jira instance
2. Add to `.env` file as `JIRA_API_TOKEN`
3. Set your domain in `.env` as `JIRA_DOMAIN`

### Asana API
1. Get API token from Asana
2. Add to `.env` file as `ASANA_API_TOKEN`

## Deployment

### FastMCP Cloud

Deploy to FastMCP Cloud for easy access:

```bash
# Configure FastMCP Cloud credentials
export FASTMCP_CLOUD_TOKEN=your_token_here

# Deploy
fastmcp deploy src/server.py
```

### Self-Hosted

Run with HTTP transport:

```bash
python src/server.py --transport http --host 0.0.0.0 --port 8000
```

## License

MIT License - see LICENSE file for details.
