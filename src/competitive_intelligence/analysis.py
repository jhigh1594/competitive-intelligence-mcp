"""
Analysis module for competitive intelligence.

This module handles:
1. Market trend analysis
2. Competitor activity summarization
3. Sentiment analysis and impact assessment
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import openai


def analyze_market_trends(
    news_data: Dict[str, Any],
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze market trends from news data.
    
    Args:
        news_data: News data from competitors
        focus_areas: Specific areas to focus on
    
    Returns:
        Dictionary containing trend analysis
    """
    # Extract all articles from all sources
    all_articles = []
    for competitor, data in news_data.items():
        if data.get("status") == "success":
            articles = data.get("articles", [])
            for article in articles:
                article["competitor"] = competitor
                all_articles.append(article)
    
    # Analyze trends based on focus areas
    trends = {}
    
    if focus_areas:
        for area in focus_areas:
            trends[area] = analyze_trend_by_area(all_articles, area)
    else:
        # Default analysis areas
        default_areas = ["product_launches", "pricing_changes", "partnerships", "executive_changes"]
        for area in default_areas:
            trends[area] = analyze_trend_by_area(all_articles, area)
    
    # Overall market sentiment
    overall_sentiment = analyze_overall_sentiment(all_articles)
    
    return {
        "trend_analysis": trends,
        "overall_sentiment": overall_sentiment,
        "total_articles_analyzed": len(all_articles),
        "analysis_date": datetime.now().isoformat(),
        "focus_areas": focus_areas or default_areas
    }


def summarize_competitor_activity(
    news_data: Dict[str, Any],
    website_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Summarize competitor activities from news and website data.
    
    Args:
        news_data: News data from competitors
        website_data: Website monitoring data from competitors
    
    Returns:
        Dictionary containing competitor summaries
    """
    summaries = {}
    
    # Process each competitor
    all_competitors = set(list(news_data.keys()) + list(website_data.keys()))
    
    for competitor in all_competitors:
        competitor_summary = {
            "name": competitor,
            "recent_activities": [],
            "key_insights": [],
            "risk_level": "low"
        }
        
        # Analyze news data
        if competitor in news_data and news_data[competitor].get("status") == "success":
            articles = news_data[competitor].get("articles", [])
            for article in articles[:5]:  # Focus on 5 most recent
                activity = {
                    "type": "news",
                    "title": article.get("title", ""),
                    "date": article.get("publishedAt", ""),
                    "summary": summarize_article_content(article.get("description", "")),
                    "impact": assess_article_impact(article)
                }
                competitor_summary["recent_activities"].append(activity)
        
        # Analyze website data
        if competitor in website_data and website_data[competitor].get("status") == "success":
            announcements = website_data[competitor].get("announcements", [])
            for announcement in announcements[:3]:  # Focus on 3 most recent
                activity = {
                    "type": "website_announcement",
                    "title": announcement.get("title", ""),
                    "date": announcement.get("date", ""),
                    "summary": announcement.get("title", ""),
                    "impact": assess_announcement_impact(announcement)
                }
                competitor_summary["recent_activities"].append(activity)
        
        # Sort activities by date
        competitor_summary["recent_activities"].sort(
            key=lambda x: x.get("date", ""), 
            reverse=True
        )
        
        # Generate key insights
        competitor_summary["key_insights"] = generate_competitor_insights(
            competitor_summary["recent_activities"]
        )
        
        # Assess overall risk level
        competitor_summary["risk_level"] = assess_competitor_risk(
            competitor_summary["recent_activities"]
        )
        
        summaries[competitor] = competitor_summary
    
    return summaries


def analyze_trend_by_area(articles: List[Dict], area: str) -> Dict[str, Any]:
    """Analyze trends for a specific focus area."""
    area_articles = [
        article for article in articles 
        if area.lower() in article.get("title", "").lower() or 
        area.lower() in article.get("description", "").lower()
    ]
    
    if not area_articles:
        return {
            "area": area,
            "article_count": 0,
            "trend": "no_data",
            "insights": [f"No articles found related to {area}"]
        }
    
    # Analyze sentiment and frequency
    sentiment_scores = []
    for article in area_articles:
        sentiment = analyze_sentiment(article.get("description", ""))
        if sentiment:
            sentiment_scores.append(sentiment.get("score", 0))
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Determine trend direction
    if avg_sentiment > 0.2:
        trend_direction = "positive"
    elif avg_sentiment < -0.2:
        trend_direction = "negative"
    else:
        trend_direction = "neutral"
    
    return {
        "area": area,
        "article_count": len(area_articles),
        "avg_sentiment": avg_sentiment,
        "trend_direction": trend_direction,
        "insights": [
            f"Found {len(area_articles)} articles related to {area}",
            f"Overall sentiment is {trend_direction}"
        ]
    }


def analyze_overall_sentiment(articles: List[Dict]) -> Dict[str, Any]:
    """Analyze overall market sentiment from all articles."""
    if not articles:
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0,
            "article_count": 0
        }
    
    sentiment_scores = []
    for article in articles:
        sentiment = analyze_sentiment(article.get("description", ""))
        if sentiment:
            sentiment_scores.append(sentiment.get("score", 0))
    
    if not sentiment_scores:
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0,
            "article_count": len(articles)
        }
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    if avg_sentiment > 0.2:
        overall = "positive"
    elif avg_sentiment < -0.2:
        overall = "negative"
    else:
        overall = "neutral"
    
    return {
        "overall_sentiment": overall,
        "sentiment_score": avg_sentiment,
        "article_count": len(articles)
    }


def analyze_sentiment(text: str) -> Optional[Dict[str, Any]]:
    """Analyze sentiment of text using Gemini."""
    from utils.ai_processing import get_ai_processor
    
    ai_processor = get_ai_processor()
    return ai_processor.analyze_sentiment(text)


def summarize_article_content(content: str, max_length: int = 150) -> str:
    """Summarize article content."""
    if len(content) <= max_length:
        return content
    
    # Simple truncation for now - would use OpenAI in production
    return content[:max_length] + "..." if len(content) > max_length else content


def assess_article_impact(article: Dict) -> str:
    """Assess the impact level of an article."""
    title = article.get("title", "").lower()
    description = article.get("description", "").lower()
    
    # High impact keywords
    high_impact_keywords = [
        "launch", "release", "acquisition", "partnership", 
        "ceo", "executive", "funding", "investment"
    ]
    
    # Medium impact keywords
    medium_impact_keywords = [
        "update", "feature", "improvement", "expansion", 
        "growth", "customer", "client"
    ]
    
    # Check for high impact keywords first
    for keyword in high_impact_keywords:
        if keyword in title or keyword in description:
            return "high"
    
    # Check for medium impact keywords
    for keyword in medium_impact_keywords:
        if keyword in title or keyword in description:
            return "medium"
    
    return "low"


def assess_announcement_impact(announcement: Dict) -> str:
    """Assess the impact level of a website announcement."""
    title = announcement.get("title", "").lower()
    
    # High impact keywords
    high_impact_keywords = [
        "new product", "launch", "release", "acquisition", 
        "partnership", "ceo", "executive", "funding"
    ]
    
    # Medium impact keywords
    medium_impact_keywords = [
        "update", "feature", "improvement", "expansion", 
        "growth", "award", "certification"
    ]
    
    # Check for high impact keywords first
    for keyword in high_impact_keywords:
        if keyword in title:
            return "high"
    
    # Check for medium impact keywords
    for keyword in medium_impact_keywords:
        if keyword in title:
            return "medium"
    
    return "low"


def generate_competitor_insights(activities: List[Dict]) -> List[str]:
    """Generate key insights from competitor activities."""
    insights = []
    
    # Count activity types
    news_count = sum(1 for activity in activities if activity.get("type") == "news")
    announcement_count = sum(1 for activity in activities if activity.get("type") == "website_announcement")
    
    # Count impact levels
    high_impact_count = sum(1 for activity in activities if activity.get("impact") == "high")
    
    # Generate insights based on activity patterns
    if news_count > 3:
        insights.append("High news activity detected - possible campaign or significant developments")
    
    if announcement_count > 2:
        insights.append("Frequent website updates - active product development or communication")
    
    if high_impact_count > 1:
        insights.append("Multiple high-impact activities detected - strategic shifts likely")
    
    # Add insight if no activities found
    if not activities:
        insights.append("No recent activities detected - monitoring may need adjustment")
    
    return insights


def assess_competitor_risk(activities: List[Dict]) -> str:
    """Assess overall risk level based on competitor activities."""
    if not activities:
        return "low"
    
    # Count high-impact activities
    high_impact_count = sum(1 for activity in activities if activity.get("impact") == "high")
    
    # Check for negative sentiment activities
    negative_count = 0
    for activity in activities:
        if "negative" in activity.get("summary", "").lower():
            negative_count += 1
    
    # Determine risk level
    if high_impact_count >= 2 or negative_count >= 2:
        return "high"
    elif high_impact_count >= 1 or negative_count >= 1:
        return "medium"
    else:
        return "low"
