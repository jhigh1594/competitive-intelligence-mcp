"""
Data sources for competitive intelligence gathering.

This module handles:
1. News API integration
2. Competitor website monitoring
3. Industry report aggregation
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup


def get_competitor_news(
    competitors: List[str],
    date_range: str,
    max_articles: int = 50
) -> Dict[str, Any]:
    """
    Fetch news articles related to competitors.
    
    Args:
        competitors: List of competitor names
        date_range: Date range for news search
        max_articles: Maximum number of articles to fetch per competitor
    
    Returns:
        Dictionary containing news data for each competitor
    """
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        return {"error": "News API key not configured"}
    
    base_url = "https://newsapi.org/v2/everything"
    
    results = {}
    
    for competitor in competitors:
        params = {
            "q": competitor,
            "from": date_range,
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "apiKey": news_api_key
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results[competitor] = {
                "articles": data.get("articles", []),
                "total_results": data.get("totalResults", 0),
                "status": "success"
            }
        except requests.exceptions.RequestException as e:
            results[competitor] = {
                "error": str(e),
                "status": "error"
            }
    
    return results


def get_tech_news(
    sources: List[str] = None,
    date_range: str = None,
    max_articles: int = 50
) -> Dict[str, Any]:
    """
    Fetch tech news from sources like TechCrunch and The Verge.
    
    Args:
        sources: List of news sources to check (techcrunch, verge, etc.)
        date_range: Date range for news search
        max_articles: Maximum number of articles to fetch
    
    Returns:
        Dictionary containing tech news data
    """
    if not sources:
        sources = ["techcrunch", "verge"]
    
    results = {}
    
    for source in sources:
        if source.lower() == "techcrunch":
            results[source] = get_techcrunch_articles(date_range, max_articles)
        elif source.lower() == "verge":
            results[source] = get_verge_articles(date_range, max_articles)
        else:
            results[source] = {"error": f"Unsupported source: {source}"}
    
    return results


def get_techcrunch_articles(date_range: str, max_articles: int) -> Dict[str, Any]:
    """Fetch articles from TechCrunch."""
    try:
        # TechCrunch RSS feed
        rss_url = "https://techcrunch.com/feed/"
        
        response = requests.get(rss_url, headers={"User-Agent": "Competitive-Intelligence-MCP/1.0"})
        response.raise_for_status()
        
        # Parse RSS feed
        soup = BeautifulSoup(response.content, "xml")
        
        articles = []
        for item in soup.find_all("item")[:max_articles]:
            title = item.find("title").get_text() if item.find("title") else "No title"
            description = item.find("description").get_text() if item.find("description") else "No description"
            pub_date = item.find("pubdate").get_text() if item.find("pubdate") else ""
            link = item.find("link").get("href") if item.find("link") else ""
            
            articles.append({
                "title": title,
                "description": description,
                "publishedAt": pub_date,
                "url": link,
                "source": "techcrunch"
            })
        
        return {
            "articles": articles,
            "total_results": len(articles),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


def get_verge_articles(date_range: str, max_articles: int) -> Dict[str, Any]:
    """Fetch articles from The Verge."""
    try:
        # The Verge RSS feed
        rss_url = "https://www.theverge.com/rss/index.xml"
        
        response = requests.get(rss_url, headers={"User-Agent": "Competitive-Intelligence-MCP/1.0"})
        response.raise_for_status()
        
        # Parse RSS feed
        soup = BeautifulSoup(response.content, "xml")
        
        articles = []
        for item in soup.find_all("item")[:max_articles]:
            title = item.find("title").get_text() if item.find("title") else "No title"
            description = item.find("description").get_text() if item.find("description") else "No description"
            pub_date = item.find("pubdate").get_text() if item.find("pubdate") else ""
            link = item.find("link").get("href") if item.find("link") else ""
            
            articles.append({
                "title": title,
                "description": description,
                "publishedAt": pub_date,
                "url": link,
                "source": "verge"
            })
        
        return {
            "articles": articles,
            "total_results": len(articles),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


def monitor_competitor_websites(
    competitors: List[str],
    competitor_urls: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Monitor competitor websites for changes and updates.
    
    Args:
        competitors: List of competitor names
        competitor_urls: Optional mapping of competitor names to URLs
    
    Returns:
        Dictionary containing website monitoring data
    """
    # Default competitor URLs (would be configurable in production)
    default_urls = {
        "competitor1": "https://example-competitor1.com",
        "competitor2": "https://example-competitor2.com",
        "competitor3": "https://example-competitor3.com"
    }
    
    urls = competitor_urls if competitor_urls else default_urls
    
    results = {}
    
    for competitor in competitors:
        url = urls.get(competitor.lower())
        if not url:
            results[competitor] = {
                "error": "No URL configured for competitor",
                "status": "error"
            }
            continue
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract basic information
            title = soup.find("title")
            title_text = title.get_text() if title else "No title found"
            
            # Look for recent announcements or news sections
            announcements = []
            news_sections = soup.find_all(["div", "section"], 
                                    class_=["news", "announcements", "updates", "blog"])
            
            for section in news_sections[:5]:  # Limit to 5 most recent
                heading = section.find(["h1", "h2", "h3"])
                if heading:
                    announcements.append({
                        "title": heading.get_text().strip(),
                        "date": extract_date_from_section(section),
                        "url": extract_link_from_section(section)
                    })
            
            results[competitor] = {
                "url": url,
                "title": title_text,
                "announcements": announcements,
                "last_checked": datetime.now().isoformat(),
                "status": "success"
            }
            
        except requests.exceptions.RequestException as e:
            results[competitor] = {
                "error": str(e),
                "status": "error"
            }
    
    return results


def get_industry_reports(
    industry: str,
    date_range: str,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fetch industry reports and analysis.
    
    Args:
        industry: Industry sector to analyze
        date_range: Date range for reports
        sources: Optional list of report sources
    
    Returns:
        Dictionary containing industry report data
    """
    # This would integrate with industry report APIs or databases
    # For now, return a placeholder structure
    
    return {
        "industry": industry,
        "date_range": date_range,
        "sources": sources or ["default_source"],
        "reports": [
            {
                "title": "Industry Trends Q4 2024",
                "summary": "Key trends in the industry include digital transformation, AI adoption, and sustainability focus.",
                "date": datetime.now().isoformat(),
                "source": "Industry Analyst Group"
            }
        ],
        "status": "success"
    }


def extract_date_from_section(section) -> Optional[str]:
    """Extract date from a website section."""
    # Look for common date patterns
    date_patterns = [
        r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
        r"(\d{4})-(\d{1,2})-(\d{1,2})",  # YYYY-MM-DD
        r"(\w+) \d{1,2}, \d{4}"  # Month DD, YYYY
    ]
    
    section_text = section.get_text()
    
    for pattern in date_patterns:
        import re
        match = re.search(pattern, section_text)
        if match:
            return match.group(0)
    
    return None


def extract_link_from_section(section) -> Optional[str]:
    """Extract the first link from a website section."""
    link = section.find("a")
    if link and link.get("href"):
        return link["href"]
    return None
