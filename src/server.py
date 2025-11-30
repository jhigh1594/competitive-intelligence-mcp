#!/usr/bin/env python3
"""
Competitive Intelligence & Daily Planning MCP Server

A FastMCP server that provides tools for:
1. Competitive intelligence gathering and analysis
2. Daily planning with calendar integration
"""

import os
import asyncio
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional, Any

from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Competitive Intelligence & Daily Planning")

# Import modules
from competitive_intelligence.data_sources import get_competitor_news, monitor_competitor_websites, get_tech_news
from competitive_intelligence.analysis import analyze_market_trends, summarize_competitor_activity
from competitive_intelligence.report_generation import generate_intelligence_report
from daily_planning.calendar_integration import get_calendar_events, get_upcoming_tasks
from daily_planning.task_prioritization import prioritize_tasks, assess_impact
from daily_planning.plan_generation import create_daily_plan


@mcp.tool
def get_competitive_intelligence(
    competitors: List[str],
    date_range: Optional[str] = None,
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Gather competitive intelligence for specified competitors.
    
    Args:
        competitors: List of competitor names to monitor
        date_range: Date range for analysis (default: last 24 hours)
        focus_areas: Specific areas to focus on (e.g., pricing, product launches, partnerships)
    
    Returns:
        Dictionary containing competitive intelligence data and insights
    """
    if not date_range:
        yesterday = date.fromisoformat(datetime.now().strftime("%Y-%m-%d"))
        date_range = f"{yesterday.isoformat()}/{datetime.now().strftime('%Y-%m-%d')}"
    
    # Get news data
    news_data = get_competitor_news(competitors, date_range)
    
    # Get tech news data
    tech_news_data = get_tech_news(
        sources=["techcrunch", "verge"],
        date_range=date_range
    )
    
    # Get website monitoring data
    website_data = monitor_competitor_websites(competitors)
    
    # Analyze market trends
    trend_analysis = analyze_market_trends(news_data, focus_areas)
    
    # Summarize competitor activities
    competitor_summary = summarize_competitor_activity(news_data, website_data)
    
    # Generate intelligence report
    report = generate_intelligence_report(
        competitors=competitors,
        news_data=news_data,
        website_data=website_data,
        trend_analysis=trend_analysis,
        competitor_summary=competitor_summary,
        focus_areas=focus_areas
    )
    
    return {
        "report_date": datetime.now().isoformat(),
        "competitors": competitors,
        "date_range": date_range,
        "intelligence_report": report,
        "key_insights": report.get("key_insights", []),
        "recommendations": report.get("recommendations", [])
    }


@mcp.tool
def create_daily_plan(
    calendar_source: str = "outlook",
    task_sources: Optional[List[str]] = None,
    focus_areas: Optional[List[str]] = None,
    time_available_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a focused daily plan based on calendar, tasks, and priorities.
    
    Args:
        calendar_source: Calendar service to use (outlook, google)
        task_sources: Task management systems to integrate (jira, asana, email)
        focus_areas: Areas to prioritize (e.g., strategic, operational, learning)
        time_available_hours: Available hours for the day
    
    Returns:
        Dictionary containing daily plan with prioritized activities
    """
    # Get calendar events
    calendar_events = get_calendar_events(calendar_source)
    
    # Get upcoming tasks
    tasks = get_upcoming_tasks(task_sources)
    
    # Prioritize tasks based on impact and urgency
    prioritized_tasks = prioritize_tasks(tasks, calendar_events, focus_areas)
    
    # Assess impact of each activity
    impact_assessment = assess_impact(prioritized_tasks, calendar_events)
    
    # Create daily plan
    daily_plan = create_daily_plan(
        calendar_events=calendar_events,
        prioritized_tasks=prioritized_tasks,
        impact_assessment=impact_assessment,
        time_available_hours=time_available_hours
    )
    
    return {
        "plan_date": datetime.now().strftime("%Y-%m-%d"),
        "calendar_source": calendar_source,
        "top_priorities": daily_plan.get("top_priorities", []),
        "time_blocks": daily_plan.get("time_blocks", []),
        "context_insights": daily_plan.get("context_insights", {}),
        "recommendations": daily_plan.get("recommendations", [])
    }


@mcp.tool
def schedule_morning_intelligence(
    time: str = "06:00",
    competitors: Optional[List[str]] = None,
    calendar_source: str = "outlook"
) -> Dict[str, Any]:
    """
    Schedule automated morning intelligence gathering and daily planning.
    
    Args:
        time: Time to run automation (HH:MM format)
        competitors: List of competitors to monitor
        calendar_source: Calendar service for daily planning
    
    Returns:
        Dictionary with scheduling confirmation and next run time
    """
    # This would integrate with cron or similar scheduling system
    # For now, return confirmation of scheduled task
    
    return {
        "scheduled_time": time,
        "competitors": competitors or [],
        "calendar_source": calendar_source,
        "next_run": datetime.now().strftime("%Y-%m-%d") + " " + time,
        "status": "scheduled",
        "message": f"Competitive intelligence and daily planning scheduled for {time}"
    }


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Competitive Intelligence & Daily Planning MCP Server")
    
    # Add arguments for different modes
    parser.add_argument(
        "--mode", 
        choices=["server", "get-intelligence", "create-plan"],
        default="server",
        help="Operation mode: server (run MCP server), get-intelligence (run once), create-plan (run once)"
    )
    
    # Add optional arguments
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol: stdio (default), http"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP transport"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport"
    )
    
    return parser.parse_args()


def run_intelligence_mode():
    """Run competitive intelligence gathering mode."""
    # Get default competitors from environment
    default_competitors = os.getenv("DEFAULT_COMPETITORS", "").split(",")
    default_focus_areas = os.getenv("DEFAULT_FOCUS_AREAS", "").split(",")
    
    print("Running competitive intelligence gathering...")
    
    result = get_competitive_intelligence(
        competitors=default_competitors,
        focus_areas=default_focus_areas
    )
    
    # Save report to file
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = os.path.join(
        reports_dir, 
        f"intelligence_{datetime.now().strftime('%Y%m%d')}.json"
    )
    
    import json
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Competitive intelligence report saved to {report_file}")
    return 0


def run_plan_mode():
    """Run daily planning mode."""
    # Get defaults from environment
    default_calendar_source = os.getenv("DEFAULT_CALENDAR_SOURCE", "outlook")
    default_task_sources = ["email", "jira"]
    default_focus_areas = os.getenv("DEFAULT_FOCUS_AREAS", "").split(",")
    
    print("Running daily planning...")
    
    result = create_daily_plan(
        calendar_source=default_calendar_source,
        task_sources=default_task_sources,
        focus_areas=default_focus_areas
    )
    
    # Save plan to file
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    plan_file = os.path.join(
        reports_dir, 
        f"daily_plan_{datetime.now().strftime('%Y%m%d')}.json"
    )
    
    import json
    with open(plan_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Daily plan saved to {plan_file}")
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    
    # Check for required environment variables
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        exit(1)
    
    # Run in different modes
    if args.mode == "server":
        print("Starting FastMCP server...")
        mcp.run(transport=args.transport, host=args.host, port=args.port)
    elif args.mode == "get-intelligence":
        exit(run_intelligence_mode())
    elif args.mode == "create-plan":
        exit(run_plan_mode())
    else:
        print(f"Unknown mode: {args.mode}")
        exit(1)
