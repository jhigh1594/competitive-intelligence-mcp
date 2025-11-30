"""
Calendar integration module for daily planning.

This module handles:
1. Microsoft Outlook API integration
2. Event extraction and analysis
3. Time availability calculation
"""

import os
import json
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional

try:
    from exchangelib import EWSDateTime, EWSTimeZone, CalendarItem, Calendar, Credentials, Configuration, Account, DELEGATE
    from exchangelib.autodiscover import Autodiscover
except ImportError:
    print("Microsoft Exchange Web Services library not installed. Install with: pip install exchangelib")
    # Create placeholder functions
    EWSDateTime = None
    EWSTimeZone = None
    CalendarItem = None
    Calendar = None
    Credentials = None
    Configuration = None
    Account = None
    DELEGATE = None
    Autodiscover = None


def get_calendar_events(
    calendar_source: str = "outlook",
    date_range: Optional[str] = None,
    max_events: int = 20
) -> List[Dict[str, Any]]:
    """
    Get calendar events from specified calendar source.
    
    Args:
        calendar_source: Calendar service to use (outlook, google)
        date_range: Date range for events (default: today)
        max_events: Maximum number of events to retrieve
    
    Returns:
        List of calendar events with details
    """
    if not date_range:
        today = datetime.now().date()
        date_range = f"{today.isoformat()}/{today.isoformat()}"
    
    if calendar_source.lower() == "outlook":
        return get_outlook_calendar_events(date_range, max_events)
    elif calendar_source.lower() == "google":
        return get_google_calendar_events(date_range, max_events)
    else:
        return [{"error": f"Unsupported calendar source: {calendar_source}"}]


def get_outlook_calendar_events(date_range: str, max_events: int) -> List[Dict[str, Any]]:
    """Get events from Microsoft Outlook Calendar."""
    if not EWSDateTime:
        return [{"error": "Exchange Web Services library not installed"}]
    
    # Check for credentials
    credentials = get_outlook_credentials()
    if not credentials:
        return [{"error": "Outlook Calendar not authenticated. Run authentication flow."}]
    
    try:
        # Set up Exchange Web Services connection
        config = Configuration(server=os.getenv("OUTLOOK_EWS_URL", "https://outlook.office365.com/EWS/Exchange.asmx"))
        credentials = Credentials(username=credentials["username"], password=credentials["password"])
        
        # Autodiscover settings
        autodiscover = Autodiscover(config)
        autodiscover.start()
        
        # Get calendar service
        calendar_service = autodiscover.discoverServices().find(
            service_type="Calendar"
        ).service
        
        # Create calendar object
        calendar = Calendar(
            primary_smtp_address=credentials["email"],
            credentials=credentials,
            autodiscover=autodiscover,
            access_type=DELEGATE
        )
        
        # Get current date
        now = datetime.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Create search filter for today's events
        search_filter = f"Start >= '{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND End <= '{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}'"
        
        # Get events
        events = calendar.FindItems(
            CalendarView=[Calendar(id="Calendar")],
            Restriction=[search_filter],
            MaxItemsReturned=max_events,
            Traversal="Shallow"
        )
        
        # Process events
        processed_events = []
        for event in events[:max_events]:
            processed_event = process_outlook_event(event)
            if processed_event:
                processed_events.append(processed_event)
        
        return processed_events
    
    except Exception as e:
        return [{"error": f"Error accessing Outlook Calendar: {str(e)}"}]


def get_google_calendar_events(date_range: str, max_events: int) -> List[Dict[str, Any]]:
    """Get events from Google Calendar (kept for compatibility)."""
    # This would use the Google Calendar API
    # For now, return placeholder data
    return [{"error": "Google Calendar integration not implemented in this version"}]


def get_outlook_credentials() -> Optional[Dict[str, str]]:
    """Get Outlook credentials from environment or file."""
    # Check for environment variables
    email = os.getenv("OUTLOOK_EMAIL")
    password = os.getenv("OUTLOOK_PASSWORD")
    
    if email and password:
        return {
            "email": email,
            "password": password,
            "username": email
        }
    
    # Check for credentials file
    creds_file = os.path.expanduser("~/.credentials/outlook_credentials.json")
    if os.path.exists(creds_file):
        try:
            with open(creds_file, "r") as f:
                return json.load(f)
        except:
            pass
    
    return None


def process_outlook_event(event) -> Optional[Dict[str, Any]]:
    """Process an Outlook Calendar event into standardized format."""
    if not event:
        return None
    
    # Extract basic event information
    subject = event.Subject
    start = event.Start
    end = event.End
    
    # Calculate duration in minutes
    duration_minutes = 0
    if start and end:
        try:
            start_time = datetime.combine(start.date, start.time)
            end_time = datetime.combine(end.date, end.time)
            duration_minutes = (end_time - start_time).total_seconds() / 60
        except:
            pass  # If time parsing fails, skip duration calculation
    
    # Determine event type
    event_type = categorize_event(subject, str(event.Body) if event.Body else "")
    
    # Extract attendees
    attendee_count = len(event.RequiredAttendees or []) + 1  # Include organizer
    
    # Check if all-day event
    is_all_day = event.IsAllDayEvent if hasattr(event, 'IsAllDayEvent') else False
    
    return {
        'title': subject,
        'start': start.isoformat() if start else '',
        'end': end.isoformat() if end else '',
        'duration_minutes': duration_minutes,
        'event_type': event_type,
        'attendee_count': attendee_count,
        'is_all_day': is_all_day,
        'description': str(event.Body) if event.Body else '',
        'location': str(event.Location) if event.Location else '',
        'source': 'outlook_calendar'
    }


def categorize_event(title: str, description: str) -> str:
    """Categorize calendar event based on title and description."""
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # Meeting keywords
    meeting_keywords = [
        'meeting', 'call', 'discussion', 'review', 'sync', 'standup',
        '1:1', 'check-in', 'catch-up', 'interview'
    ]
    
    # Work keywords
    work_keywords = [
        'work', 'project', 'task', 'development', 'coding', 'writing',
        'focus', 'deep work', 'analysis', 'research'
    ]
    
    # Personal keywords
    personal_keywords = [
        'lunch', 'break', 'coffee', 'gym', 'exercise', 'personal',
        'appointment', 'errand', 'commute'
    ]
    
    # Check for meeting keywords
    for keyword in meeting_keywords:
        if keyword in title_lower or keyword in desc_lower:
            return 'meeting'
    
    # Check for work keywords
    for keyword in work_keywords:
        if keyword in title_lower or keyword in desc_lower:
            return 'work'
    
    # Check for personal keywords
    for keyword in personal_keywords:
        if keyword in title_lower or keyword in desc_lower:
            return 'personal'
    
    # Default to 'other'
    return 'other'


def calculate_available_time(
    events: List[Dict[str, Any]],
    work_hours_start: int = 9,
    work_hours_end: int = 17
) -> Dict[str, Any]:
    """
    Calculate available time blocks from calendar events.
    
    Args:
        events: List of calendar events
        work_hours_start: Start of work hours (24-hour format)
        work_hours_end: End of work hours (24-hour format)
    
    Returns:
        Dictionary with available time blocks
    """
    if not events:
        return {
            "total_available_minutes": (work_hours_end - work_hours_start) * 60,
            "time_blocks": [{
                "start": f"{work_hours_start:02d}:00",
                "end": f"{work_hours_end:02d}:00",
                "duration_minutes": (work_hours_end - work_hours_start) * 60,
                "type": "available"
            }]
        }
    
    # Sort events by start time
    sorted_events = sorted(events, key=lambda x: x.get('start', ''))
    
    # Convert to datetime objects for easier calculation
    event_times = []
    for event in sorted_events:
        start_str = event.get('start', '')
        if start_str:
            try:
                start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                event_times.append((start_time, event))
            except:
                pass  # Skip events with invalid time format
    
    # Sort by start time
    event_times.sort(key=lambda x: x[0])
    
    # Calculate available time blocks
    available_blocks = []
    current_time = datetime.now().replace(
        hour=work_hours_start, minute=0, second=0, microsecond=0
    )
    work_end_time = datetime.now().replace(
        hour=work_hours_end, minute=0, second=0, microsecond=0
    )
    
    for start_time, event in event_times:
        # Add available block before this event
        if start_time > current_time:
            duration = (start_time - current_time).total_seconds() / 60
            if duration > 15:  # Only include blocks longer than 15 minutes
                available_blocks.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": start_time.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "type": "available"
                })
        
        # Update current time to end of this event
        end_str = event.get('end', '')
        if end_str:
            try:
                end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                current_time = max(current_time, end_time)
            except:
                pass  # Skip if invalid time format
    
    # Add final available block after last event
    if current_time < work_end_time:
        duration = (work_end_time - current_time).total_seconds() / 60
        if duration > 15:  # Only include blocks longer than 15 minutes
            available_blocks.append({
                "start": current_time.strftime("%H:%M"),
                "end": work_end_time.strftime("%H:%M"),
                "duration_minutes": duration,
                "type": "available"
            })
    
    total_available = sum(block["duration_minutes"] for block in available_blocks)
    
    return {
        "total_available_minutes": total_available,
        "time_blocks": available_blocks,
        "work_hours": {
            "start": f"{work_hours_start:02d}:00",
            "end": f"{work_hours_end:02d}:00"
        }
    }


def authenticate_outlook_calendar() -> Dict[str, Any]:
    """
    Authenticate with Microsoft Outlook Calendar.
    
    Returns:
        Dictionary with authentication status and instructions
    """
    if not EWSDateTime:
        return {
            "status": "error",
            "message": "Exchange Web Services library not installed"
        }
    
    # For now, return placeholder for authentication
    return {
        "status": "auth_required",
        "message": "Please configure Outlook credentials in .env file with OUTLOOK_EMAIL and OUTLOOK_PASSWORD",
        "instructions": [
            "1. Set OUTLOOK_EMAIL to your Outlook email address",
            "2. Set OUTLOOK_PASSWORD to your Outlook password or app password",
            "3. For production use, consider using OAuth2 with Microsoft Graph API"
        ]
    }
