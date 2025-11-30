"""AI processing utility module.

This module handles:
1. Google Gemini API integration
2. Text processing and analysis
3. AI-powered insights generation
"""

import os
import json
from typing import Dict, List, Any, Optional

try:
    import google.generativeai as genai
    from google.generativeai import GenerativeModel
    from google.ai import client
except ImportError:
    print("Google Generative AI library not installed. Install with: pip install google-generativeai")
    # Create placeholder functions
    genai = None
    GenerativeModel = None
    client = None


class AIProcessor:
    """Base class for AI processing operations using Google Gemini."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            # Configure Gemini client
            self.client = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
    
    def is_configured(self) -> bool:
        """Check if AI processor is configured."""
        return self.api_key is not None and self.client is not None
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of text using Gemini."""
        if not self.is_configured() or not text.strip():
            return None
        
        try:
            response = self.client.generate_content(
                f"Analyze the sentiment of this text and return a JSON object with 'score' (-1 to 1) and 'label' (positive, negative, neutral). Text: {text}"
            )
            
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
                # Fallback to simple sentiment analysis
                if "positive" in text.lower():
                    return {"score": 0.7, "label": "positive"}
                elif "negative" in text.lower():
                    return {"score": -0.7, "label": "negative"}
                else:
                    return {"score": 0.0, "label": "neutral"}
        except Exception as e:
            return {"error": str(e)}
    
    def extract_key_insights(self, text: str, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract key insights from text using Gemini."""
        if not self.is_configured() or not text.strip():
            return {"error": "AI not configured or empty text"}
        
        # Create prompt based on focus areas
        focus_prompt = ""
        if focus_areas:
            focus_prompt = f"Focus on these areas: {', '.join(focus_areas)}. "
        
        try:
            response = self.client.generate_content(
                f"{focus_prompt}Extract the 3-5 most important insights from this text. Return a JSON object with 'insights' array containing the insights."
            )
            
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
                # Fallback to simple insight extraction
                return {"insights": ["Key information extracted from text"]}
        except Exception as e:
            return {"error": str(e)}
    
    def summarize_text(self, text: str, max_length: int = 300) -> Optional[str]:
        """Summarize text using Gemini."""
        if not self.is_configured() or not text.strip():
            return None
        
        try:
            response = self.client.generate_content(
                f"Summarize this text in no more than {max_length} characters. Focus on key points and main ideas."
            )
            
            return response.text
        except Exception as e:
            print(f"Error summarizing text: {e}")
            return None
    
    def generate_recommendations(self, context: Dict[str, Any], goal: str) -> List[str]:
        """Generate recommendations based on context and goal using Gemini."""
        if not self.is_configured():
            return ["AI not configured"]
        
        try:
            context_str = json.dumps(context, indent=2)
            
            response = self.client.generate_content(
                f"Based on the provided context, generate 3-5 actionable recommendations to achieve the goal. Return a JSON array with 'recommendations'."
            )
            
            # Parse the response
            response_text = response.text
            try:
                # Extract JSON from response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    if "recommendations" in result and isinstance(result["recommendations"], list):
                        return result["recommendations"]
            except:
                return ["Error generating recommendations"]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def categorize_tasks(self, tasks: List[str]) -> Dict[str, List[str]]:
        """Categorize tasks into logical groups using Gemini."""
        if not self.is_configured():
            return {"error": "AI not configured"}
        
        try:
            tasks_text = "\n".join(tasks)
            
            response = self.client.generate_content(
                f"Categorize these tasks into logical groups (e.g., 'strategic', 'operational', 'administrative', 'learning'). Return a JSON object with 'categories' mapping each task to its category."
            )
            
            # Parse the response
            response_text = response.text
            try:
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    if "categories" in result and isinstance(result["categories"], dict):
                        return result["categories"]
            except:
                return {"strategic": [], "operational": [], "administrative": [], "learning": []}
        except Exception as e:
            print(f"Error categorizing tasks: {e}")
            return {"error": str(e)}
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]], constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Prioritize tasks based on constraints and context using Gemini."""
        if not self.is_configured():
            return tasks
        
        try:
            tasks_str = json.dumps(tasks, indent=2)
            constraints_str = json.dumps(constraints, indent=2) if constraints else "{}"
            
            response = self.client.generate_content(
                f"Prioritize these tasks based on the constraints: {constraints_str}. Return a JSON array with tasks in priority order, including 'priority_score' for each task."
            )
            
            # Parse the response
            response_text = response.text
            try:
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    if isinstance(result, list):
                        return result
                    elif "prioritized_tasks" in result and isinstance(result["prioritized_tasks"], list):
                        return result["prioritized_tasks"]
            except:
                return tasks  # Return original if parsing fails
        except Exception as e:
            print(f"Error prioritizing tasks: {e}")
            return tasks


# Global AI processor instance
ai_processor = AIProcessor()


def get_ai_processor() -> AIProcessor:
    """Get the global AI processor instance."""
    return ai_processor


def configure_ai_processor(api_key: str) -> bool:
    """Configure the AI processor with API key."""
    try:
        ai_processor.api_key = api_key
        ai_processor.client = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
        return True
    except Exception as e:
        print(f"Error configuring AI processor: {e}")
        return False


def is_ai_configured() -> bool:
    """Check if AI processor is configured."""
    return ai_processor.is_configured()
