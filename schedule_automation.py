#!/usr/bin/env python3
"""
Automation script for scheduling morning competitive intelligence and daily planning.

This script sets up cron jobs to run the MCP server at specified times.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, time
from pathlib import Path


def setup_cron_jobs():
    """Set up cron jobs for automated execution."""
    # Get configuration from environment
    competitors = os.getenv("DEFAULT_COMPETITORS", "").split(",")
    focus_areas = os.getenv("DEFAULT_FOCUS_AREAS", "").split(",")
    calendar_source = os.getenv("DEFAULT_CALENDAR_SOURCE", "google")
    
    # Create cron job for 6 AM competitive intelligence gathering
    intel_cron = f"0 6 * * * /usr/bin/python3 {Path(__file__).parent.absolute()}/run_server.py --get-competitive-intelligence"
    
    # Create cron job for 7 AM daily planning
    plan_cron = f"0 7 * * * /usr/bin/python3 {Path(__file__).parent.absolute()}/run_server.py --create-daily-plan"
    
    # Save cron jobs to file
    cron_file = Path(__file__).parent / "crontab.txt"
    with open(cron_file, "w") as f:
        f.write(f"# Competitive Intelligence & Daily Planning Automation\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"# Competitive Intelligence at 6 AM daily\n")
        f.write(f"{intel_cron}\n\n")
        f.write(f"# Daily Planning at 7 AM daily\n")
        f.write(f"{plan_cron}\n")
    
    print(f"Cron jobs written to {cron_file}")
    print("To install, run: crontab crontab.txt")
    
    return 0


def run_competitive_intelligence():
    """Run competitive intelligence gathering."""
    competitors = os.getenv("DEFAULT_COMPETITORS", "").split(",")
    focus_areas = os.getenv("DEFAULT_FOCUS_AREAS", "").split(",")
    
    # Import and run the function
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        from server import get_competitive_intelligence
        
        result = get_competitive_intelligence(
            competitors=competitors,
            focus_areas=focus_areas
        )
        
        # Save report
        report_file = Path(__file__).parent / "reports" / f"intelligence_{datetime.now().strftime('%Y%m%d')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Competitive intelligence report saved to {report_file}")
        return 0
    except Exception as e:
        print(f"Error running competitive intelligence: {e}")
        return 1


def run_daily_planning():
    """Run daily planning."""
    calendar_source = os.getenv("DEFAULT_CALENDAR_SOURCE", "google")
    task_sources = ["email", "jira"]
    focus_areas = os.getenv("DEFAULT_FOCUS_AREAS", "").split(",")
    
    # Import and run the function
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        from server import create_daily_plan
        
        result = create_daily_plan(
            calendar_source=calendar_source,
            task_sources=task_sources,
            focus_areas=focus_areas
        )
        
        # Save plan
        plan_file = Path(__file__).parent / "reports" / f"daily_plan_{datetime.now().strftime('%Y%m%d')}.json"
        plan_file.parent.mkdir(exist_ok=True)
        
        with open(plan_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Daily plan saved to {plan_file}")
        return 0
    except Exception as e:
        print(f"Error running daily planning: {e}")
        return 1


def main():
    """Main function for automation script."""
    if len(sys.argv) < 2:
        print("Usage: python schedule_automation.py [command]")
        print("Commands:")
        print("  setup-cron    Set up cron jobs")
        print("  get-intelligence    Run competitive intelligence")
        print("  create-plan      Create daily plan")
        return 1
    
    command = sys.argv[1]
    
    if command == "setup-cron":
        return setup_cron_jobs()
    elif command == "get-intelligence":
        return run_competitive_intelligence()
    elif command == "create-plan":
        return run_daily_planning()
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
