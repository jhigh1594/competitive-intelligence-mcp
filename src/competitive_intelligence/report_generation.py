"""
Report generation module for competitive intelligence.

This module handles:
1. Structured report templates
2. Key insights extraction
3. Multiple output formats
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def generate_intelligence_report(
    competitors: List[str],
    news_data: Dict[str, Any],
    website_data: Dict[str, Any],
    trend_analysis: Dict[str, Any],
    competitor_summary: Dict[str, Any],
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive competitive intelligence report.
    
    Args:
        competitors: List of monitored competitors
        news_data: News data from competitors
        website_data: Website monitoring data
        trend_analysis: Market trend analysis
        competitor_summary: Summarized competitor activities
        focus_areas: Specific areas of focus
    
    Returns:
        Dictionary containing structured intelligence report
    """
    report_date = datetime.now().strftime("%B %d, %Y")
    
    # Generate executive summary
    executive_summary = generate_executive_summary(
        competitors, trend_analysis, competitor_summary
    )
    
    # Generate competitor profiles
    competitor_profiles = generate_competitor_profiles(competitor_summary)
    
    # Generate market insights
    market_insights = generate_market_insights(trend_analysis, focus_areas)
    
    # Generate recommendations
    recommendations = generate_recommendations(
        competitor_summary, trend_analysis, focus_areas
    )
    
    # Compile full report
    report = {
        "metadata": {
            "report_date": report_date,
            "competitors_count": len(competitors),
            "focus_areas": focus_areas or ["general"],
            "data_sources": ["news_api", "website_monitoring", "industry_reports", "tech_news"]
        },
        "executive_summary": executive_summary,
        "competitor_profiles": competitor_profiles,
        "market_insights": market_insights,
        "recommendations": recommendations,
        "appendix": {
            "data_collection_methods": "Automated news monitoring, website scraping, industry report aggregation, and tech news feeds",
            "analysis_period": "Last 24 hours",
            "confidence_level": "Medium - based on publicly available data"
        }
    }
    
    return report


def generate_executive_summary(
    competitors: List[str],
    trend_analysis: Dict[str, Any],
    competitor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate executive summary of key findings."""
    from utils.ai_processing import get_ai_processor
    
    ai_processor = get_ai_processor()
    
    # Create context for AI
    context = {
        "competitors": competitors,
        "trend_analysis": trend_analysis,
        "competitor_summary": competitor_summary
    }
    
    # Generate prompt
    prompt = f"""
    Analyze the following competitive intelligence data and generate an executive summary:
    
    Competitors: {', '.join(competitors)}
    Market Trends: {trend_analysis}
    Competitor Summary: {json.dumps(competitor_summary, indent=2)}
    
    Focus on:
    1. Key strategic implications
    2. Critical risks or opportunities
    3. Recommended actions
    
    Return a JSON object with:
    - key_findings: Array of main findings
    - critical_insights: Array of critical insights
    - summary: Brief overall summary
    """
    
    try:
        response = ai_processor.client.generate_content(prompt)
        
        # Parse the response
        response_text = response.text
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            # Fallback to simple summary
            return {
                "key_findings": [
                    f"Monitoring {len(competitors)} competitors",
                    f"Market sentiment is {trend_analysis.get('overall_sentiment', {}).get('overall_sentiment', 'neutral')}"
                ],
                "critical_insights": [
                    "Competitors showing increased activity",
                    "Market requires close monitoring"
                ],
                "summary": f"Competitive landscape shows {len(competitors)} active competitors"
            }
    except Exception as e:
        return {
            "key_findings": [f"Error generating summary: {str(e)}"],
            "critical_insights": [],
            "summary": "Error in analysis"
        }


def generate_competitor_profiles(competitor_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate detailed profiles for each competitor."""
    profiles = []
    
    for competitor, data in competitor_summary.items():
        # Extract key activities
        activities = data.get("recent_activities", [])
        
        # Count activity types
        news_count = sum(1 for activity in activities if activity.get("type") == "news")
        announcement_count = sum(1 for activity in activities if activity.get("type") == "website_announcement")
        
        # Count impact levels
        high_impact = sum(1 for activity in activities if activity.get("impact") == "high")
        medium_impact = sum(1 for activity in activities if activity.get("impact") == "medium")
        
        # Get most recent activity
        most_recent = activities[0] if activities else None
        most_recent_date = most_recent.get("date", "") if most_recent else ""
        
        profile = {
            "name": competitor,
            "risk_level": data.get("risk_level", "low"),
            "activity_summary": {
                "total_activities": len(activities),
                "news_articles": news_count,
                "website_announcements": announcement_count,
                "high_impact_activities": high_impact,
                "medium_impact_activities": medium_impact
            },
            "most_recent_activity": {
                "date": most_recent_date,
                "type": most_recent.get("type", "") if most_recent else "",
                "title": most_recent.get("title", "") if most_recent else ""
            },
            "key_insights": data.get("key_insights", []),
            "recommended_actions": get_competitor_actions(data.get("risk_level", "low"))
        }
        
        profiles.append(profile)
    
    return profiles


def generate_market_insights(
    trend_analysis: Dict[str, Any],
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Generate insights about market trends."""
    insights = []
    
    # Overall market sentiment
    overall_sentiment = trend_analysis.get("overall_sentiment", {})
    sentiment_score = overall_sentiment.get("sentiment_score", 0)
    sentiment_label = overall_sentiment.get("overall_sentiment", "neutral")
    
    insights.append(f"Market sentiment is {sentiment_label} with score of {sentiment_score:.2f}")
    
    # Analyze trend areas
    trend_data = trend_analysis.get("trend_analysis", {})
    for area, data in trend_data.items():
        if isinstance(data, dict):
            direction = data.get("trend_direction", "stable")
            article_count = data.get("article_count", 0)
            
            if direction == "positive":
                insights.append(f"Positive trend in {area} with {article_count} articles")
            elif direction == "negative":
                insights.append(f"Negative trend in {area} with {article_count} articles")
            else:
                insights.append(f"Stable trend in {area} with {article_count} articles")
    
    # Focus area specific insights
    if focus_areas:
        for area in focus_areas:
            if area.lower() in ["pricing", "product_launches", "partnerships"]:
                insights.append(f"Special attention needed for {area} developments")
    
    return {
        "market_sentiment": {
            "score": sentiment_score,
            "label": sentiment_label
        },
        "trend_insights": insights,
        "focus_areas": focus_areas or ["general"],
        "data_points_analyzed": trend_analysis.get("total_articles_analyzed", 0)
    }


def generate_recommendations(
    competitor_summary: Dict[str, Any],
    trend_analysis: Dict[str, Any],
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    # Count high-risk competitors
    high_risk_count = 0
    for competitor, data in competitor_summary.items():
        if data.get("risk_level") == "high":
            high_risk_count += 1
    
    # Market sentiment recommendations
    market_sentiment = trend_analysis.get("overall_sentiment", {}).get("overall_sentiment", "neutral")
    
    if market_sentiment == "positive":
        recommendations.append({
            "priority": "high",
            "category": "market_opportunity",
            "title": "Leverage Positive Market Sentiment",
            "description": "Current market sentiment is positive - consider accelerating product launches or marketing campaigns",
            "actions": ["Increase marketing spend", "Launch new features", "Expand sales efforts"]
        })
    elif market_sentiment == "negative":
        recommendations.append({
            "priority": "high",
            "category": "risk_mitigation",
            "title": "Address Negative Market Sentiment",
            "description": "Market sentiment is negative - focus on customer retention and value communication",
            "actions": ["Enhance customer support", "Communicate value proposition", "Monitor competitor responses"]
        })
    
    # Competitor-specific recommendations
    if high_risk_count > 0:
        recommendations.append({
            "priority": "high",
            "category": "competitive_response",
            "title": "Monitor High-Risk Competitors",
            "description": f"{high_risk_count} competitors showing high-risk activities - immediate response required",
            "actions": ["Analyze competitor strategy", "Prepare countermeasures", "Review own positioning"]
        })
    
    # Focus area specific recommendations
    if focus_areas:
        for area in focus_areas:
            if area.lower() == "pricing":
                recommendations.append({
                    "priority": "medium",
                    "category": "pricing_strategy",
                    "title": "Review Pricing Strategy",
                    "description": "Competitor pricing changes detected - review own pricing strategy",
                    "actions": ["Analyze price elasticity", "Consider promotional pricing", "Review value proposition"]
                })
            elif area.lower() == "product_launches":
                recommendations.append({
                    "priority": "medium",
                    "category": "product_development",
                    "title": "Accelerate Product Development",
                    "description": "Increased competitor product launches detected - accelerate development pipeline",
                    "actions": ["Prioritize roadmap", "Allocate additional resources", "Consider strategic partnerships"]
                })
    
    return recommendations


def get_competitor_actions(risk_level: str) -> List[str]:
    """Get recommended actions based on competitor risk level."""
    if risk_level == "high":
        return [
            "Daily monitoring of all activities",
            "Prepare rapid response team",
            "Analyze strategic implications",
            "Review own competitive positioning"
        ]
    elif risk_level == "medium":
        return [
            "Weekly competitive reviews",
            "Monitor key announcements",
            "Assess impact on own strategy"
        ]
    else:
        return [
            "Monthly competitive reviews",
            "Monitor major announcements",
            "Maintain competitive intelligence database"
        ]


def format_report_as_markdown(report: Dict[str, Any]) -> str:
    """Format the intelligence report as markdown."""
    metadata = report.get("metadata", {})
    executive_summary = report.get("executive_summary", {})
    
    markdown = f"""# Competitive Intelligence Report
    
**Date:** {metadata.get('report_date', 'Unknown')}  
**Competitors Monitored:** {metadata.get('competitors_count', 0)}  
**Focus Areas:** {', '.join(metadata.get('focus_areas', []))}

## Executive Summary

{format_executive_summary(executive_summary)}

## Market Insights

{format_market_insights(report.get('market_insights', {}))}

## Competitor Profiles

{format_competitor_profiles(report.get('competitor_profiles', []))}

## Recommendations

{format_recommendations(report.get('recommendations', []))}

---

*Report generated by Competitive Intelligence MCP Tool*  
*Data sources: {', '.join(metadata.get('data_sources', []))}*
"""
    return markdown


def format_executive_summary(executive_summary: Dict[str, Any]) -> str:
    """Format executive summary as markdown."""
    key_findings = executive_summary.get("key_findings", [])
    critical_insights = executive_summary.get("critical_insights", [])
    summary = executive_summary.get("summary", "")
    
    formatted = "### Key Findings\n\n"
    for finding in key_findings:
        formatted += f"- {finding}\n"
    
    formatted += "\n### Critical Insights\n\n"
    for insight in critical_insights:
        formatted += f"- {insight}\n"
    
    formatted += f"\n### Overall Summary\n\n{summary}\n"
    
    return formatted


def format_market_insights(market_insights: Dict[str, Any]) -> str:
    """Format market insights as markdown."""
    sentiment = market_insights.get("market_sentiment", {})
    trend_insights = market_insights.get("trend_insights", [])
    
    formatted = f"**Market Sentiment:** {sentiment.get('label', 'Unknown')} (Score: {sentiment.get('score', 0):.2f})\n\n"
    
    formatted += "**Trend Analysis:**\n\n"
    for insight in trend_insights:
        formatted += f"- {insight}\n"
    
    return formatted


def format_competitor_profiles(profiles: List[Dict[str, Any]]) -> str:
    """Format competitor profiles as markdown."""
    formatted = ""
    
    for profile in profiles:
        name = profile.get("name", "Unknown")
        risk_level = profile.get("risk_level", "low").upper()
        activity_summary = profile.get("activity_summary", {})
        most_recent = profile.get("most_recent_activity", {})
        
        formatted += f"""### {name} (Risk Level: {risk_level})

**Activity Summary:**
- Total Activities: {activity_summary.get('total_activities', 0)}
- News Articles: {activity_summary.get('news_articles', 0)}
- Website Announcements: {activity_summary.get('website_announcements', 0)}
- High-Impact Activities: {activity_summary.get('high_impact_activities', 0)}

**Most Recent Activity:**
- Date: {most_recent.get('date', 'Unknown')}
- Type: {most_recent.get('type', 'Unknown')}
- Title: {most_recent.get('title', 'Unknown')}

**Key Insights:**
"""
        
        insights = profile.get("key_insights", [])
        for insight in insights:
            formatted += f"- {insight}\n"
        
        actions = profile.get("recommended_actions", [])
        formatted += "\n**Recommended Actions:**\n"
        for action in actions:
            formatted += f"- {action}\n"
        
        formatted += "\n---\n\n"
    
    return formatted


def format_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """Format recommendations as markdown."""
    formatted = ""
    
    # Group by priority
    high_priority = [r for r in recommendations if r.get("priority") == "high"]
    medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
    low_priority = [r for r in recommendations if r.get("priority") == "low"]
    
    if high_priority:
        formatted += "### High Priority\n\n"
        for rec in high_priority:
            formatted += f"**{rec.get('title', 'Unknown')}**\n"
            formatted += f"{rec.get('description', 'Unknown')}\n\n"
            formatted += "**Actions:**\n"
            for action in rec.get("actions", []):
                formatted += f"- {action}\n"
            formatted += "\n"
    
    if medium_priority:
        formatted += "### Medium Priority\n\n"
        for rec in medium_priority:
            formatted += f"**{rec.get('title', 'Unknown')}**\n"
            formatted += f"{rec.get('description', 'Unknown')}\n\n"
            formatted += "**Actions:**\n"
            for action in rec.get("actions", []):
                formatted += f"- {action}\n"
            formatted += "\n"
    
    if low_priority:
        formatted += "### Low Priority\n\n"
        for rec in low_priority:
            formatted += f"**{rec.get('title', 'Unknown')}**\n"
            formatted += f"{rec.get('description', 'Unknown')}\n\n"
            formatted += "**Actions:**\n"
            for action in rec.get("actions", []):
                formatted += f"- {action}\n"
            formatted += "\n"
    
    return formatted


def save_report_to_file(report: Dict[str, Any], file_path: str) -> bool:
    """Save report to file."""
    try:
        with open(file_path, "w") as f:
            json.dump(report, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False


def save_markdown_report(report: Dict[str, Any], file_path: str) -> bool:
    """Save markdown report to file."""
    try:
        markdown_content = format_report_as_markdown(report)
        with open(file_path, "w") as f:
            f.write(markdown_content)
        return True
    except Exception as e:
        print(f"Error saving markdown report: {e}")
        return False
