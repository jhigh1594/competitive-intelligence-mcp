"""
Plan generation module for daily planning.

This module handles:
1. Daily plan creation
2. Time blocking optimization
3. Contextual recommendations
"""

import os
import json
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
import openai


def create_daily_plan(
    calendar_events: List[Dict[str, Any]],
    prioritized_tasks: List[Dict[str, Any]],
    impact_assessment: Dict[str, Any],
    time_available_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a focused daily plan based on calendar, tasks, and impact assessment.
    
    Args:
        calendar_events: Calendar events for context
        prioritized_tasks: Prioritized list of tasks
        impact_assessment: Impact assessment of tasks
        time_available_hours: Available hours for the day
    
    Returns:
        Dictionary containing daily plan
    """
    # Calculate available time blocks
    available_time = calculate_available_time_blocks(
        calendar_events, time_available_hours
    )
    
    # Select top tasks for the day
    top_tasks = select_top_tasks(prioritized_tasks, available_time)
    
    # Create time blocks for selected tasks
    time_blocks = create_time_blocks(top_tasks, available_time)
    
    # Generate contextual insights
    insights = generate_plan_insights(
        top_tasks, calendar_events, available_time
    )
    
    # Generate recommendations
    recommendations = generate_plan_recommendations(
        top_tasks, available_time, impact_assessment
    )
    
    return {
        "plan_date": datetime.now().strftime("%Y-%m-%d"),
        "top_priorities": top_tasks,
        "time_blocks": time_blocks,
        "context_insights": insights,
        "recommendations": recommendations,
        "time_utilization": calculate_time_utilization(time_blocks, available_time)
    }


def calculate_available_time_blocks(
    calendar_events: List[Dict[str, Any]],
    time_available_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate available time blocks from calendar events.
    
    Args:
        calendar_events: Calendar events
        time_available_hours: Available hours for the day
    
    Returns:
        Dictionary with available time information
    """
    # Default to 8 work hours if not specified
    if not time_available_hours:
        time_available_hours = 8.0
    
    # Convert to minutes
    total_available_minutes = time_available_hours * 60
    
    # Calculate time already committed
    committed_minutes = sum(
        event.get("duration_minutes", 0) 
        for event in calendar_events 
        if event.get("type") in ["meeting", "work"]
    )
    
    # Calculate available time
    available_minutes = total_available_minutes - committed_minutes
    
    return {
        "total_available_minutes": total_available_minutes,
        "committed_minutes": committed_minutes,
        "available_minutes": available_minutes,
        "utilization_percent": (committed_minutes / total_available_minutes) * 100 if total_available_minutes > 0 else 0
    }


def select_top_tasks(
    prioritized_tasks: List[Dict[str, Any]],
    available_time: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Select top tasks that fit in available time.
    
    Args:
        prioritized_tasks: List of prioritized tasks
        available_time: Available time information
    
    Returns:
        List of selected tasks
    """
    available_minutes = available_time.get("available_minutes", 0)
    
    if not prioritized_tasks or available_minutes <= 30:
        return []  # Not enough time for meaningful tasks
    
    # Select tasks that fit in available time
    selected_tasks = []
    used_time = 0
    
    for task in prioritized_tasks:
        task_duration = task.get("duration_minutes", 60)
        
        # Check if task fits in remaining time
        if used_time + task_duration <= available_minutes:
            selected_tasks.append(task)
            used_time += task_duration
        
        # Stop if we've used 80% of available time
        if used_time >= available_minutes * 0.8:
            break
    
    return selected_tasks


def create_time_blocks(
    tasks: List[Dict[str, Any]],
    available_time: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Create time blocks for selected tasks.
    
    Args:
        tasks: List of selected tasks
        available_time: Available time information
    
    Returns:
        List of time blocks
    """
    if not tasks:
        return []
    
    # Sort tasks by priority score
    sorted_tasks = sorted(
        tasks, key=lambda x: x.get("priority_score", 0), reverse=True
    )
    
    # Create time blocks
    time_blocks = []
    current_time = 9 * 60  # Start at 9:00 AM in minutes
    
    for task in sorted_tasks:
        task_duration = task.get("duration_minutes", 60)
        
        # Find next available time slot
        time_block = {
            "task_id": task.get("id", ""),
            "title": task.get("title", ""),
            "start_time": minutes_to_time(current_time),
            "end_time": minutes_to_time(current_time + task_duration),
            "duration_minutes": task_duration,
            "task_type": task.get("task_type", "work"),
            "priority": task.get("importance", "medium")
        }
        
        time_blocks.append(time_block)
        current_time += task_duration
        
        # Add 15-minute break between tasks
        current_time += 15
    
    return time_blocks


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def generate_plan_insights(
    tasks: List[Dict[str, Any]],
    calendar_events: List[Dict[str, Any]],
    available_time: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate insights about the daily plan.
    
    Args:
        tasks: Selected tasks for the day
        calendar_events: Calendar events
        available_time: Available time information
    
    Returns:
        Dictionary with plan insights
    """
    # Calculate task distribution
    task_types = {}
    total_task_time = 0
    
    for task in tasks:
        task_type = task.get("task_type", "work")
        task_types[task_type] = task_types.get(task_type, 0) + task.get("duration_minutes", 60)
        total_task_time += task.get("duration_minutes", 60)
    
    # Calculate meeting time from calendar
    meeting_time = sum(
        event.get("duration_minutes", 0) 
        for event in calendar_events 
        if event.get("type") == "meeting"
    )
    
    # Generate insights
    insights = {
        "task_distribution": task_types,
        "total_task_time": total_task_time,
        "meeting_time": meeting_time,
        "focus_areas": identify_focus_areas(tasks),
        "time_pressure": assess_time_pressure(total_task_time, available_time)
    }
    
    return insights


def identify_focus_areas(tasks: List[Dict[str, Any]]) -> List[str]:
    """Identify focus areas from tasks."""
    focus_areas = []
    
    # Extract keywords from task titles and descriptions
    all_text = " ".join([
        task.get("title", "") + " " + task.get("description", "")
        for task in tasks
    ]).lower()
    
    # Common focus area keywords
    area_keywords = {
        "strategic": ["strategic", "planning", "roadmap", "vision"],
        "operational": ["operations", "process", "workflow", "efficiency"],
        "customer": ["customer", "client", "user", "support"],
        "development": ["development", "coding", "programming", "feature"],
        "learning": ["learning", "training", "research", "study"],
        "communication": ["communication", "meeting", "presentation", "report"]
    }
    
    # Find which areas are most mentioned
    for area, keywords in area_keywords.items():
        count = sum(1 for keyword in keywords if keyword in all_text)
        if count >= 2:  # At least 2 mentions
            focus_areas.append(area)
    
    return focus_areas


def assess_time_pressure(
    total_task_time: int,
    available_time: Dict[str, Any]
) -> str:
    """Assess time pressure level."""
    available_minutes = available_time.get("available_minutes", 480)  # Default 8 hours
    
    if total_task_time >= available_minutes * 0.9:
        return "high"
    elif total_task_time >= available_minutes * 0.7:
        return "medium"
    else:
        return "low"


def generate_plan_recommendations(
    tasks: List[Dict[str, Any]],
    available_time: Dict[str, Any],
    impact_assessment: Dict[str, Any]
) -> List[str]:
    """
    Generate recommendations for the daily plan.
    
    Args:
        tasks: Selected tasks for the day
        available_time: Available time information
        impact_assessment: Impact assessment of tasks
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Time utilization recommendations
    utilization = available_time.get("utilization_percent", 0)
    if utilization > 90:
        recommendations.append("High calendar utilization - consider deferring non-essential tasks")
    elif utilization < 50:
        recommendations.append("Low calendar utilization - consider adding more focused work blocks")
    
    # Task balance recommendations
    high_impact_tasks = sum(
        1 for task in tasks 
        if task.get("impact_score", 0) >= 7
    )
    
    if high_impact_tasks == 0:
        recommendations.append("No high-impact tasks scheduled - consider adding strategic work")
    
    # Focus area recommendations
    focus_areas = impact_assessment.get("focus_areas", [])
    if "strategic" not in focus_areas and len(tasks) > 0:
        recommendations.append("Consider adding strategic planning time to your schedule")
    
    # Meeting recommendations
    meeting_time = sum(
        event.get("duration_minutes", 0) 
        for event in impact_assessment.get("calendar_events", [])
        if event.get("type") == "meeting"
    )
    
    if meeting_time > 240:  # More than 4 hours
        recommendations.append("High meeting load - consider consolidating or declining some meetings")
    
    return recommendations


def calculate_time_utilization(
    time_blocks: List[Dict[str, Any]],
    available_time: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate time utilization metrics.
    
    Args:
        time_blocks: Time blocks with tasks
        available_time: Available time information
    
    Returns:
        Dictionary with utilization metrics
    """
    if not time_blocks:
        return {
            "scheduled_minutes": 0,
            "available_minutes": available_time.get("available_minutes", 0),
            "utilization_percent": 0
        }
    
    scheduled_minutes = sum(
        block.get("duration_minutes", 0) for block in time_blocks
    )
    
    available_minutes = available_time.get("available_minutes", 480)  # Default 8 hours
    
    return {
        "scheduled_minutes": scheduled_minutes,
        "available_minutes": available_minutes,
        "utilization_percent": (scheduled_minutes / available_minutes) * 100 if available_minutes > 0 else 0
    }


def save_daily_plan(plan: Dict[str, Any], file_path: str) -> bool:
    """Save daily plan to file."""
    try:
        with open(file_path, "w") as f:
            json.dump(plan, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving daily plan: {e}")
        return False


def format_plan_as_markdown(plan: Dict[str, Any]) -> str:
    """Format daily plan as markdown."""
    plan_date = plan.get("plan_date", "Unknown")
    top_priorities = plan.get("top_priorities", [])
    time_blocks = plan.get("time_blocks", [])
    insights = plan.get("context_insights", {})
    recommendations = plan.get("recommendations", [])
    
    markdown = f"""# Daily Plan for {plan_date}

## Top Priorities

"""
    
    for i, task in enumerate(top_priorities, 1):
        title = task.get("title", "Untitled Task")
        duration = task.get("duration_minutes", 0)
        priority = task.get("importance", "medium")
        
        markdown += f"{i}. **{title}** ({duration} min, Priority: {priority})\n"
    
    markdown += f"""
## Time Blocks

"""
    
    for block in time_blocks:
        start_time = block.get("start_time", "Unknown")
        end_time = block.get("end_time", "Unknown")
        title = block.get("title", "Untitled Block")
        
        markdown += f"- **{start_time} - {end_time}:** {title}\n"
    
    markdown += f"""
## Context Insights

"""
    
    # Task distribution
    task_distribution = insights.get("task_distribution", {})
    if task_distribution:
        markdown += "**Task Distribution:**\n"
        for task_type, minutes in task_distribution.items():
            markdown += f"- {task_type.title()}: {minutes} minutes\n"
    
    # Focus areas
    focus_areas = insights.get("focus_areas", [])
    if focus_areas:
        markdown += "\n**Focus Areas:**\n"
        for area in focus_areas:
            markdown += f"- {area.title()}\n"
    
    # Time pressure
    time_pressure = insights.get("time_pressure", "")
    if time_pressure:
        markdown += f"\n**Time Pressure:** {time_pressure.title()}\n"
    
    markdown += f"""
## Recommendations

"""
    
    for rec in recommendations:
        markdown += f"- {rec}\n"
    
    markdown += "\n---\n*Generated by Competitive Intelligence & Daily Planning MCP Tool*"
    
    return markdown


def save_markdown_plan(plan: Dict[str, Any], file_path: str) -> bool:
    """Save markdown plan to file."""
    try:
        markdown_content = format_plan_as_markdown(plan)
        with open(file_path, "w") as f:
            f.write(markdown_content)
        return True
    except Exception as e:
        print(f"Error saving markdown plan: {e}")
        return False
