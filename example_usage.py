#!/usr/bin/env python3
"""
Example usage of the Competitive Intelligence & Daily Planning MCP tool.

This script demonstrates how to use the MCP server with different tools.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import modules
from competitive_intelligence.data_sources import get_competitor_news, get_tech_news
from competitive_intelligence.analysis import analyze_market_trends, summarize_competitor_activity
from competitive_intelligence.report_generation import generate_intelligence_report
from daily_planning.calendar_integration import get_calendar_events, get_upcoming_tasks
from daily_planning.task_prioritization import prioritize_tasks, assess_impact
from daily_planning.plan_generation import create_daily_plan


async def example_competitive_intelligence():
    """Example of using competitive intelligence tool."""
    print("=== Competitive Intelligence Example ===")
    
    # Get competitive intelligence for sample competitors
    result = get_competitive_intelligence(
        competitors=["CompetitorA", "CompetitorB"],
        focus_areas=["pricing", "product_launches"]
    )
    
    print(f"Report generated for {len(result['competitors'])} competitors")
    print(f"Key insights: {len(result['key_insights'])}")
    print(f"Recommendations: {len(result['recommendations'])}")
    
    # Save report to file
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / "example_intelligence.json"
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Report saved to {report_file}")


async def example_tech_news():
    """Example of using tech news sources."""
    print("\n=== Tech News Example ===")
    
    # Get tech news from multiple sources
    result = get_tech_news(
        sources=["techcrunch", "verge"],
        date_range="2023-01-01/2023-01-02"
    )
    
    print(f"Tech news gathered from {len(result)} sources")
    
    # Save report to file
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / "example_tech_news.json"
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Tech news report saved to {report_file}")


async def example_daily_planning():
    """Example of using daily planning tool."""
    print("\n=== Daily Planning Example ===")
    
    # Create daily plan
    result = create_daily_plan(
        calendar_source="google",
        task_sources=["email", "jira"],
        focus_areas=["strategic", "operational"],
        time_available_hours=8
    )
    
    print(f"Plan created for {result['plan_date']}")
    print(f"Top priorities: {len(result['top_priorities'])}")
    print(f"Time blocks: {len(result['time_blocks'])}")
    
    # Save plan to file
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    plan_file = reports_dir / "example_daily_plan.json"
    with open(plan_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Plan saved to {plan_file}")


async def main():
    """Run example usage."""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py [intelligence|planning]")
        return 1
    
    mode = sys.argv[1]
    
    if mode == "intelligence":
        await example_competitive_intelligence()
    elif mode == "planning":
        await example_daily_planning()
    else:
        print(f"Unknown mode: {mode}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
