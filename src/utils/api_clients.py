"""
API clients utility module.

This module handles:
1. HTTP client configuration
2. API authentication
3. Common API operations
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List


class APIClient:
    """Base class for API clients."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up headers
        self.session.headers.update({
            "User-Agent": "Competitive-Intelligence-MCP/1.0",
            "Content-Type": "application/json"
        })
        
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "error"
            }


class NewsAPIClient(APIClient):
    """Client for news APIs."""
    
    def __init__(self):
        api_key = os.getenv("NEWS_API_KEY")
        super().__init__("https://newsapi.org/v2", api_key)
    
    def get_everything(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        sort_by: str = "publishedAt",
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Get all articles matching the query."""
        params = {
            "q": query,
            "sortBy": sort_by,
            "pageSize": page_size
        }
        
        if from_date:
            params["from"] = from_date
        
        if to_date:
            params["to"] = to_date
        
        return self.get("everything", params)
    
    def get_sources(self) -> Dict[str, Any]:
        """Get all news sources."""
        return self.get("sources")


class GoogleCalendarClient(APIClient):
    """Client for Google Calendar API."""
    
    def __init__(self):
        # Google Calendar uses OAuth, not API key
        super().__init__("https://www.googleapis.com/calendar/v3")
    
    def get_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Get events from Google Calendar."""
        params = {
            "calendarId": calendar_id,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        if time_min:
            params["timeMin"] = time_min
        
        if time_max:
            params["timeMax"] = time_max
        
        return self.get("events", params)


class JiraClient(APIClient):
    """Client for Jira API."""
    
    def __init__(self):
        api_token = os.getenv("JIRA_API_TOKEN")
        domain = os.getenv("JIRA_DOMAIN", "atlassian.net")
        super().__init__(f"https://{domain}.rest/api/3", api_token)
        
        # Set up Jira-specific headers
        self.session.headers.update({
            "Accept": "application/json"
        })
    
    def get_issues(
        self,
        project_key: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Get issues from Jira."""
        params = {
            "maxResults": max_results,
            "fields": "summary,description,status,duedate,priority,customfield_10010"  # Include custom fields
        }
        
        jql_parts = []
        
        if project_key:
            jql_parts.append(f'project = "{project_key}"')
        
        if status:
            jql_parts.append(f'status = "{status}"')
        
        if assignee:
            jql_parts.append(f'assignee = "{assignee}"')
        
        if jql_parts:
            params["jql"] = " AND ".join(jql_parts)
        
        return self.get("search", params)
    
    def get_projects(self) -> Dict[str, Any]:
        """Get all projects from Jira."""
        return self.get("project")


class AsanaClient(APIClient):
    """Client for Asana API."""
    
    def __init__(self):
        api_token = os.getenv("ASANA_API_TOKEN")
        super().__init__("https://app.asana.com/api/1.0", api_token)
        
        # Set up Asana-specific headers
        self.session.headers.update({
            "Accept": "application/json"
        })
    
    def get_tasks(
        self,
        project_id: Optional[str] = None,
        assignee: Optional[str] = None,
        completed_since: Optional[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Get tasks from Asana."""
        params = {
            "opt_fields": "name,notes,due_on,completed,projects,assignee"
        }
        
        if project_id:
            params["project"] = project_id
        
        if assignee:
            params["assignee"] = assignee
        
        if completed_since:
            params["completed_since"] = completed_since
        
        return self.get("tasks", params)
    
    def get_projects(self) -> Dict[str, Any]:
        """Get all projects from Asana."""
        return self.get("projects")


def create_api_client(service: str) -> APIClient:
    """
    Factory function to create appropriate API client.
    
    Args:
        service: Service name (news, google_calendar, jira, asana)
    
    Returns:
        Configured API client
    """
    if service.lower() == "news":
        return NewsAPIClient()
    elif service.lower() == "google_calendar":
        return GoogleCalendarClient()
    elif service.lower() == "jira":
        return JiraClient()
    elif service.lower() == "asana":
        return AsanaClient()
    else:
        raise ValueError(f"Unsupported service: {service}")


def make_authenticated_request(
    client: APIClient,
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Make an authenticated request with error handling.
    
    Args:
        client: API client instance
        method: HTTP method (get, post)
        endpoint: API endpoint
        data: Request data for POST requests
        params: Query parameters for GET requests
    
    Returns:
        Response dictionary
    """
    try:
        if method.lower() == "get":
            return client.get(endpoint, params)
        elif method.lower() == "post":
            return client.post(endpoint, data)
        else:
            return {
                "error": f"Unsupported method: {method}",
                "status": "error"
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
