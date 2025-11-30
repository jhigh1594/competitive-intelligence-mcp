"""Tests for competitive intelligence module."""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from competitive_intelligence.data_sources import get_competitor_news, monitor_competitor_websites
from competitive_intelligence.analysis import analyze_market_trends, summarize_competitor_activity
from competitive_intelligence.report_generation import generate_intelligence_report


class TestCompetitiveIntelligence:
    """Test class for competitive intelligence functionality."""
    
    def test_get_competitor_news(self):
        """Test news data retrieval."""
        # Mock data for testing
        competitors = ["TestCompetitor1", "TestCompetitor2"]
        
        # This would normally call the API, but we'll mock for testing
        # In a real implementation, you would need to set NEWS_API_KEY
        result = get_competitor_news(competitors, "2023-01-01", 10)
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "TestCompetitor1" in result
        assert "TestCompetitor2" in result
    
    def test_monitor_competitor_websites(self):
        """Test website monitoring."""
        competitors = ["TestCompetitor1", "TestCompetitor2"]
        
        # This would normally scrape websites, but we'll mock for testing
        result = monitor_competitor_websites(competitors)
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "TestCompetitor1" in result
        assert "TestCompetitor2" in result
    
    def test_analyze_market_trends(self):
        """Test market trend analysis."""
        # Mock news data
        news_data = {
            "TestCompetitor1": {
                "status": "success",
                "articles": [
                    {
                        "title": "Test Article 1",
                        "description": "Test competitor launched new product",
                        "publishedAt": "2023-01-01T12:00:00Z"
                    }
                ]
            }
        }
        
        result = analyze_market_trends(news_data, ["pricing", "product_launches"])
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "trend_analysis" in result
        assert "overall_sentiment" in result
    
    def test_summarize_competitor_activity(self):
        """Test competitor activity summarization."""
        # Mock data
        news_data = {
            "TestCompetitor1": {
                "status": "success",
                "articles": [
                    {
                        "title": "Test Article 1",
                        "description": "Test competitor launched new product",
                        "publishedAt": "2023-01-01T12:00:00Z"
                    }
                ]
            }
        }
        
        website_data = {
            "TestCompetitor1": {
                "status": "success",
                "announcements": [
                    {
                        "title": "Test Announcement 1",
                        "date": "2023-01-01"
                    }
                ]
            }
        }
        
        result = summarize_competitor_activity(news_data, website_data)
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "TestCompetitor1" in result
        assert "key_insights" in result["TestCompetitor1"]
    
    def test_generate_intelligence_report(self):
        """Test intelligence report generation."""
        # Mock data
        competitors = ["TestCompetitor1", "TestCompetitor2"]
        news_data = {
            "TestCompetitor1": {
                "status": "success",
                "articles": [
                    {
                        "title": "Test Article 1",
                        "description": "Test competitor launched new product",
                        "publishedAt": "2023-01-01T12:00:00Z"
                    }
                ]
            }
        }
        website_data = {
            "TestCompetitor1": {
                "status": "success",
                "announcements": [
                    {
                        "title": "Test Announcement 1",
                        "date": "2023-01-01"
                    }
                ]
            }
        }
        trend_analysis = {
            "trend_analysis": {
                "pricing": {
                    "trend_direction": "positive",
                    "article_count": 5
                }
            },
            "overall_sentiment": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.3
            }
        }
        competitor_summary = {
            "TestCompetitor1": {
                "risk_level": "medium",
                "key_insights": ["Product launch detected"]
            }
        }
        
        result = generate_intelligence_report(
            competitors=competitors,
            news_data=news_data,
            website_data=website_data,
            trend_analysis=trend_analysis,
            competitor_summary=competitor_summary,
            focus_areas=["pricing", "product_launches"]
        )
        
        # Check basic structure
        assert isinstance(result, dict)
        assert "metadata" in result
        assert "executive_summary" in result
        assert "competitor_profiles" in result
        assert "recommendations" in result


if __name__ == "__main__":
    pytest.main([__file__])
