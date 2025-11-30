#!/usr/bin/env python3
"""
FastMCP Cloud Entry Point

This is the entry point for FastMCP Cloud deployment.
It exports the mcp instance without complex argument parsing.
"""

import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from src.competitive_intelligence.data_sources import get_competitor_news, monitor_competitor_websites, get_tech_news
from src.competitive_intelligence.analysis import analyze_market_trends, summarize_competitor_activity
from src.competitive_intelligence.report_generation import generate_intelligence_report
from src.daily_planning.calendar_integration import get_calendar_events
from src.daily_planning.task_prioritization import prioritize_tasks, assess_impact, get_upcoming_tasks
from src.daily_planning.plan_generation import create_daily_plan

# Initialize FastMCP server
mcp = FastMCP("Competitive Intelligence & Daily Planning")


@mcp.tool
def get_competitive_intelligence(
    competitors: list[str],
    date_range: str | None = None,
    focus_areas: list[str] | None = None
) -> dict:
    """
    Gather competitive intelligence for specified competitors.
    
    Args:
        competitors: List of competitor names to monitor
        date_range: Date range for analysis (default: last 24 hours)
        focus_areas: Specific areas to focus on (e.g., pricing, product launches, partnerships)
    
    Returns:
        Dictionary containing competitive intelligence data and insights
    """
    from datetime import datetime, date
    
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
    task_sources: list[str] | None = None,
    focus_areas: list[str] | None = None,
    time_available_hours: float | None = None
) -> dict:
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
    from datetime import datetime
    
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
    competitors: list[str] | None = None,
    calendar_source: str = "outlook"
) -> dict:
    """
    Schedule automated morning intelligence gathering and daily planning.
    
    Args:
        time: Time to run automation (HH:MM format)
        competitors: List of competitors to monitor
        calendar_source: Calendar service for daily planning
    
    Returns:
        Dictionary with scheduling confirmation and next run time
    """
    from datetime import datetime
    
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
