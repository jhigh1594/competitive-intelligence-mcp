"""Tests for daily planning module."""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daily_planning.calendar_integration import get_calendar_events, calculate_available_time
from daily_planning.task_prioritization import prioritize_tasks, assess_impact
from daily_planning.plan_generation import create_daily_plan


class TestDailyPlanning:
    """Test class for daily planning functionality."""
    
    def test_get_calendar_events(self):
        """Test calendar event retrieval."""
        # Mock calendar events
        events = get_calendar_events("google")
        
        # Check basic structure
        assert isinstance(events, list)
        assert len(events) >= 0
    
    def test_calculate_available_time(self):
        """Test available time calculation."""
        # Mock calendar events
        events = [
            {
                "title": "Meeting 1",
                "start": "2023-01-01T09:00:00Z",
                "end": "2023-01-01T10:00:00Z",
                "type": "meeting"
            },
            {
                "title": "Meeting 2",
                "start": "2023-01-01T11:00:00Z",
                "end": "2023-01-01T12:00:00Z",
                "type": "meeting"
            },
            {
                "title": "Lunch",
                "start": "2023-01-01T12:00:00Z",
                "end": "2023-01-01T13:00:00Z",
                "type": "personal"
            }
        ]
        
        result = calculate_available_time(events)
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "total_available_minutes" in result
        assert "time_blocks" in result
    
    def test_prioritize_tasks(self):
        """Test task prioritization."""
        # Mock tasks
        tasks = [
            {
                "id": "task1",
                "title": "High priority task",
                "description": "Important task with high impact",
                "due_date": "2023-01-02",
                "importance": "high",
                "effort_hours": 4
            },
            {
                "id": "task2",
                "title": "Medium priority task",
                "description": "Medium importance task",
                "due_date": "2023-01-03",
                "importance": "medium",
                "effort_hours": 2
            },
            {
                "id": "task3",
                "title": "Low priority task",
                "description": "Low importance task",
                "due_date": "2023-01-04",
                "importance": "low",
                "effort_hours": 1
            }
        ]
        
        # Mock calendar events
        calendar_events = [
            {
                "title": "Meeting 1",
                "start": "2023-01-01T09:00:00Z",
                "end": "2023-01-01T10:00:00Z",
                "type": "meeting"
            }
        ]
        
        result = prioritize_tasks(tasks, calendar_events)
        
        # Check basic structure
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check if tasks are sorted by priority
        assert result[0]["id"] == "task1"  # High priority first
        assert result[1]["id"] == "task2"  # Medium priority second
        assert result[2]["id"] == "task3"  # Low priority third
    
    def test_assess_impact(self):
        """Test impact assessment."""
        # Mock prioritized tasks
        tasks = [
            {
                "id": "task1",
                "title": "High priority task",
                "impact_score": 8
            },
            {
                "id": "task2",
                "title": "Medium priority task",
                "impact_score": 5
            },
            {
                "id": "task3",
                "title": "Low priority task",
                "impact_score": 3
            }
        ]
        
        # Mock calendar events
        calendar_events = [
            {
                "title": "Meeting 1",
                "start": "2023-01-01T09:00:00Z",
                "end": "2023-01-01T10:00:00Z",
                "type": "meeting"
            }
        ]
        
        result = assess_impact(tasks, calendar_events)
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "total_tasks" in result
        assert "high_impact_tasks" in result
        assert "recommendations" in result
    
    def test_create_daily_plan(self):
        """Test daily plan creation."""
        # Mock data
        calendar_events = [
            {
                "title": "Meeting 1",
                "start": "2023-01-01T09:00:00Z",
                "end": "2023-01-01T10:00:00Z",
                "type": "meeting"
            }
        ]
        
        prioritized_tasks = [
            {
                "id": "task1",
                "title": "High priority task",
                "duration_minutes": 120,
                "priority_score": 80
            },
            {
                "id": "task2",
                "title": "Medium priority task",
                "duration_minutes": 60,
                "priority_score": 60
            }
        ]
        
        impact_assessment = {
            "total_tasks": 2,
            "high_impact_tasks": 1
        }
        
        available_time = {
            "total_available_minutes": 360,
            "available_minutes": 240
        }
        
        result = create_daily_plan(
            calendar_events=calendar_events,
            prioritized_tasks=prioritized_tasks,
            impact_assessment=impact_assessment,
            time_available_hours=8
        )
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "plan_date" in result
        assert "top_priorities" in result
        assert "time_blocks" in result
        assert "context_insights" in result
        assert "recommendations" in result


if __name__ == "__main__":
    pytest.main([__file__])
