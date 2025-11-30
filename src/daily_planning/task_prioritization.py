"""
Task prioritization module for daily planning.

This module handles:
1. Task prioritization algorithms
2. Impact assessment
3. Context-aware prioritization
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple


def prioritize_tasks(
    tasks: List[Dict[str, Any]],
    calendar_events: List[Dict[str, Any]],
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Prioritize tasks based on multiple factors.
    
    Args:
        tasks: List of tasks from various sources
        calendar_events: Calendar events for context
        focus_areas: Specific areas to prioritize
    
    Returns:
        List of prioritized tasks with scores
    """
    if not tasks:
        return []
    
    # Calculate priority scores for each task
    scored_tasks = []
    for task in tasks:
        score = calculate_task_priority(task, calendar_events, focus_areas)
        task["priority_score"] = score
        scored_tasks.append(task)
    
    # Sort by priority score (higher is more important)
    prioritized_tasks = sorted(scored_tasks, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    return prioritized_tasks


def calculate_task_priority(
    task: Dict[str, Any],
    calendar_events: List[Dict[str, Any]],
    focus_areas: Optional[List[str]] = None
) -> float:
    """
    Calculate priority score for a single task.
    
    Args:
        task: Task to score
        calendar_events: Calendar events for context
        focus_areas: Specific areas to prioritize
    
    Returns:
        Priority score (0-100)
    """
    score = 0.0
    
    # Factor 1: Urgency (0-30 points)
    urgency_score = calculate_urgency_score(task)
    score += urgency_score
    
    # Factor 2: Importance (0-25 points)
    importance_score = calculate_importance_score(task)
    score += importance_score
    
    # Factor 3: Focus area alignment (0-20 points)
    if focus_areas:
        alignment_score = calculate_focus_alignment_score(task, focus_areas)
        score += alignment_score
    
    # Factor 4: Calendar context (0-15 points)
    context_score = calculate_calendar_context_score(task, calendar_events)
    score += context_score
    
    # Factor 5: Effort vs impact (0-10 points)
    effort_impact_score = calculate_effort_impact_score(task)
    score += effort_impact_score
    
    return min(score, 100.0)  # Cap at 100


def calculate_urgency_score(task: Dict[str, Any]) -> float:
    """Calculate urgency score based on deadline and time sensitivity."""
    due_date = task.get("due_date")
    if not due_date:
        return 0.0  # No due date = no urgency
    
    try:
        due = datetime.fromisoformat(due_date)
        now = datetime.now()
        
        # Calculate days until due
        days_until_due = (due - now).days
        
        if days_until_due < 0:
            return 30.0  # Overdue = maximum urgency
        elif days_until_due <= 1:
            return 25.0  # Due today or tomorrow = high urgency
        elif days_until_due <= 3:
            return 20.0  # Due this week = medium-high urgency
        elif days_until_due <= 7:
            return 15.0  # Due next week = medium urgency
        elif days_until_due <= 14:
            return 10.0  # Due in two weeks = low-medium urgency
        else:
            return 5.0   # Due later = low urgency
    except:
        return 0.0  # Invalid date format = no urgency


def calculate_importance_score(task: Dict[str, Any]) -> float:
    """Calculate importance score based on task properties."""
    # Check for explicit importance rating
    importance = task.get("importance", "").lower()
    
    if importance in ["critical", "urgent", "high"]:
        return 25.0
    elif importance in ["medium", "normal", "regular"]:
        return 15.0
    elif importance in ["low", "minor"]:
        return 5.0
    else:
        # Infer importance from title/description
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        
        # High importance indicators
        high_importance_keywords = [
            "strategic", "critical", "important", "key", "essential",
            "must", "required", "deadline", "review", "approval"
        ]
        
        # Medium importance indicators
        medium_importance_keywords = [
            "should", "plan", "consider", "review", "update", "improve"
        ]
        
        # Check for high importance keywords
        for keyword in high_importance_keywords:
            if keyword in title or keyword in description:
                return 25.0
        
        # Check for medium importance keywords
        for keyword in medium_importance_keywords:
            if keyword in title or keyword in description:
                return 15.0
        
        # Default to medium importance
        return 15.0


def calculate_focus_alignment_score(
    task: Dict[str, Any],
    focus_areas: Optional[List[str]] = None
) -> float:
    """Calculate alignment score with focus areas."""
    if not focus_areas:
        return 10.0  # Default alignment score
    
    title = task.get("title", "").lower()
    description = task.get("description", "").lower()
    tags = [tag.lower() for tag in task.get("tags", [])]
    
    # Count matches with focus areas
    matches = 0
    for area in focus_areas:
        area_lower = area.lower()
        if area_lower in title or area_lower in description or area_lower in tags:
            matches += 1
    
    # Calculate score based on matches
    if matches >= 2:
        return 20.0  # Strong alignment
    elif matches >= 1:
        return 15.0  # Some alignment
    else:
        return 5.0   # No alignment


def calculate_calendar_context_score(
    task: Dict[str, Any],
    calendar_events: List[Dict[str, Any]]
) -> float:
    """Calculate context score based on calendar events."""
    if not calendar_events:
        return 7.5  # Default score if no calendar context
    
    # Get task duration estimate
    task_duration = task.get("duration_minutes", 60)
    
    # Look for meeting-free blocks
    available_blocks = [
        event for event in calendar_events
        if event.get("type") == "available"
    ]
    
    # Calculate total available time
    total_available = sum(block.get("duration_minutes", 0) for block in available_blocks)
    
    # Score based on whether task fits in available blocks
    if task_duration <= max(block.get("duration_minutes", 0) for block in available_blocks):
        return 15.0  # Fits well in calendar
    elif task_duration <= total_available * 0.8:
        return 10.0  # Fits with some rearrangement
    elif task_duration <= total_available:
        return 5.0   # Fits but requires significant rearrangement
    else:
        return 0.0   # Doesn't fit in available time


def calculate_effort_impact_score(task: Dict[str, Any]) -> float:
    """Calculate effort vs impact score."""
    effort = task.get("effort_hours", 1)
    impact = task.get("impact_score", 5)
    
    # High impact, low effort = best
    if impact >= 8 and effort <= 2:
        return 10.0
    elif impact >= 6 and effort <= 4:
        return 7.5
    elif impact >= 4 and effort <= 6:
        return 5.0
    elif impact >= 2 and effort <= 8:
        return 2.5
    else:
        return 0.0  # Low impact or high effort


def assess_impact(
    tasks: List[Dict[str, Any]],
    calendar_events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Assess impact of tasks on overall goals and calendar.
    
    Args:
        tasks: List of prioritized tasks
        calendar_events: Calendar events for context
    
    Returns:
        Dictionary with impact assessment
    """
    if not tasks:
        return {
            "total_tasks": 0,
            "high_impact_tasks": 0,
            "calendar_conflicts": 0,
            "time_utilization": 0,
            "recommendations": ["No tasks to assess"]
        }
    
    # Count high-impact tasks
    high_impact_tasks = [
        task for task in tasks 
        if task.get("impact_score", 0) >= 7
    ]
    
    # Check for calendar conflicts
    total_task_time = sum(task.get("duration_minutes", 60) for task in tasks[:3])  # Top 3 tasks
    available_time = sum(
        event.get("duration_minutes", 0) 
        for event in calendar_events 
        if event.get("type") == "available"
    )
    
    calendar_conflicts = max(0, total_task_time - available_time)
    
    # Calculate time utilization
    time_utilization = min(100, (total_task_time / max(available_time, 1)) * 100) if available_time > 0 else 0
    
    # Generate recommendations
    recommendations = []
    
    if calendar_conflicts > 60:
        recommendations.append("Consider rescheduling some tasks to avoid calendar conflicts")
    
    if len(high_impact_tasks) > 0:
        recommendations.append(f"Focus on {len(high_impact_tasks)} high-impact tasks first")
    
    if time_utilization > 90:
        recommendations.append("High time utilization - ensure buffer time between tasks")
    
    return {
        "total_tasks": len(tasks),
        "high_impact_tasks": len(high_impact_tasks),
        "calendar_conflicts": calendar_conflicts,
        "time_utilization": time_utilization,
        "recommendations": recommendations
    }


def get_upcoming_tasks(
    task_sources: Optional[List[str]] = None,
    days_ahead: int = 7
) -> List[Dict[str, Any]]:
    """
    Get upcoming tasks from various sources.
    
    Args:
        task_sources: List of task sources to check
        days_ahead: Number of days ahead to look for tasks
    
    Returns:
        List of upcoming tasks
    """
    all_tasks = []
    
    if not task_sources:
        task_sources = ["email", "jira", "asana"]
    
    for source in task_sources:
        if source.lower() == "email":
            tasks = get_email_tasks(days_ahead)
        elif source.lower() == "jira":
            tasks = get_jira_tasks(days_ahead)
        elif source.lower() == "asana":
            tasks = get_asana_tasks(days_ahead)
        else:
            tasks = []
        
        # Add source information
        for task in tasks:
            task["source"] = source
        
        all_tasks.extend(tasks)
    
    return all_tasks


def get_email_tasks(days_ahead: int) -> List[Dict[str, Any]]:
    """Get tasks from email."""
    # This would integrate with email APIs (Gmail, Outlook)
    # For now, return placeholder data
    return [
        {
            "id": "email_1",
            "title": "Review quarterly report",
            "description": "Review and provide feedback on Q4 performance metrics",
            "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "importance": "high",
            "effort_hours": 2,
            "impact_score": 8,
            "source": "email"
        },
        {
            "id": "email_2",
            "title": "Prepare presentation for client meeting",
            "description": "Create slides and practice presentation for upcoming client review",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "importance": "medium",
            "effort_hours": 4,
            "impact_score": 6,
            "source": "email"
        }
    ]


def get_jira_tasks(days_ahead: int) -> List[Dict[str, Any]]:
    """Get tasks from Jira."""
    # This would integrate with Jira API
    # For now, return placeholder data
    return [
        {
            "id": "jira_1",
            "title": "Fix critical bug in authentication module",
            "description": "Users reporting login failures with new authentication flow",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "importance": "critical",
            "effort_hours": 6,
            "impact_score": 9,
            "source": "jira"
        },
        {
            "id": "jira_2",
            "title": "Implement new feature for dashboard",
            "description": "Add competitive intelligence widget to main dashboard",
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "importance": "medium",
            "effort_hours": 8,
            "impact_score": 7,
            "source": "jira"
        }
    ]


def get_asana_tasks(days_ahead: int) -> List[Dict[str, Any]]:
    """Get tasks from Asana."""
    # This would integrate with Asana API
    # For now, return placeholder data
    return [
        {
            "id": "asana_1",
            "title": "Update project documentation",
            "description": "Ensure all project documentation is up to date with latest changes",
            "due_date": (datetime.now() + timedelta(days=4)).isoformat(),
            "importance": "medium",
            "effort_hours": 3,
            "impact_score": 5,
            "source": "asana"
        }
    ]


def extract_tasks_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract tasks from natural language text using AI.
    
    Args:
        text: Natural language text containing task information
    
    Returns:
        List of extracted tasks
    """
    from utils.ai_processing import get_ai_processor
    
    ai_processor = get_ai_processor()
    return ai_processor.extract_tasks_from_text(text)
