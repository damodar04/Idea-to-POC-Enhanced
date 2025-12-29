"""Resource Estimation Agent - Analyzes company and idea to estimate required resources using DeepSeek"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ResourceEstimationAgent:
    """Agent that estimates resources needed to implement an idea for a specific company."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables from .env file
        try:
            # Try multiple possible locations for .env
            possible_paths = [
                Path(__file__).parent.parent / '.env',  # services/../.env
                Path.cwd() / '.env',                    # Current working dir
            ]
            
            env_loaded = False
            for env_path in possible_paths:
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path, override=True)
                    env_loaded = True
                    break
            
            if not env_loaded:
                load_dotenv()  # Try default load
                
        except Exception as e:
            self.logger.error(f"Error loading .env: {e}", exc_info=True)
        
        # Now get the API key
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not self.deepseek_api_key:
            self.logger.error("DEEPSEEK_API_KEY not found in environment variables")
            self.logger.error(f"Available env vars: {list(os.environ.keys())[:10]}...")
            self.client = None
        else:
            self.logger.info(f"DeepSeek API key found (length: {len(self.deepseek_api_key)})")
            try:
                self.client = OpenAI(
                    api_key=self.deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                self.logger.info("DeepSeek client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize DeepSeek client: {e}", exc_info=True)
                self.client = None
        

    
    def estimate_resources(
        self,
        company_name: str,
        idea_title: str,
        idea_description: str,
        company_research: Dict,
        idea_research: Dict
    ) -> Dict[str, Any]:
        """
        Estimate comprehensive resources needed to implement the idea.
        
        Args:
            company_name: Name of the target company
            idea_title: Title of the idea
            idea_description: Description of the idea
            company_research: Company research data
            idea_research: Idea/market research data
            
        Returns:
            Dictionary containing resource estimates including:
            - team_resources: Number and types of team members needed
            - timeline: Estimated implementation timeline with phases
            - technical_infrastructure: Required technical resources
            - budget_estimate: Estimated budget breakdown
            - risks: Potential risks and mitigation strategies
        """
        
        if not self.client:
            self.logger.error("DeepSeek client not initialized - missing API key")
            return {
                "success": False,
                "error": "DeepSeek API key not configured"
            }
        
        try:
            self.logger.info(f"Starting resource estimation for: {idea_title} at {company_name}")
            
            # Build context from research data
            context = self._build_context(
                company_name,
                idea_title,
                idea_description,
                company_research,
                idea_research
            )
            
            # Create prompt for DeepSeek
            prompt = self._create_estimation_prompt(context)
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert project manager and resource planner with deep knowledge of software development, business operations, and technology implementation. You provide detailed, realistic resource estimates for implementing business ideas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            estimation_text = response.choices[0].message.content
            
            # Structure the response
            result = self._parse_estimation_response(estimation_text)
            result["success"] = True
            result["raw_response"] = estimation_text
            
            self.logger.info(f"Resource estimation completed for: {idea_title}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in resource estimation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_context(
        self,
        company_name: str,
        idea_title: str,
        idea_description: str,
        company_research: Dict,
        idea_research: Dict
    ) -> Dict[str, Any]:
        """Build context from all available research data."""
        
        context = {
            "company_name": company_name,
            "idea_title": idea_title,
            "idea_description": idea_description,
            "company_info": {},
            "market_info": {}
        }
        
        # Extract relevant company information
        if company_research and company_research.get("success"):
            context["company_info"] = {
                "business_overview": company_research.get("what_company_does", ""),
                "size_indicator": company_research.get("financials", {}).get("annual_revenue", ""),
                "current_initiatives": company_research.get("current_initiatives_and_goals", []),
                "challenges": company_research.get("challenges", []),
                "opportunities": company_research.get("opportunities", [])
            }
        
        # Extract relevant market information
        if idea_research and idea_research.get("success"):
            context["market_info"] = {
                "existing_implementations": idea_research.get("who_is_implementing", []),
                "pros": idea_research.get("pros_and_cons", {}).get("pros", []),
                "cons": idea_research.get("pros_and_cons", {}).get("cons", []),
                "insights": idea_research.get("useful_insights", []),
                "metrics": idea_research.get("implementation_metrics", {})
            }
        
        return context
    
    def _create_estimation_prompt(self, context: Dict[str, Any]) -> str:
        """Create a detailed prompt for resource estimation."""
        
        prompt = f"""
Based on the following information, provide a comprehensive and REALISTIC resource estimation for implementing this idea.

**COMPANY INFORMATION:**
Company: {context['company_name']}
Business Overview: {context['company_info'].get('business_overview', 'N/A')}
Company Size/Revenue: {context['company_info'].get('size_indicator', 'N/A')}

Current Initiatives: {', '.join(context['company_info'].get('current_initiatives', [])[:3]) if context['company_info'].get('current_initiatives') else 'N/A'}

**IDEA TO IMPLEMENT:**
Title: {context['idea_title']}
Description: {context['idea_description']}

**MARKET CONTEXT:**
Existing Implementations: {len(context['market_info'].get('existing_implementations', []))} companies already implementing similar ideas
Key Benefits: {', '.join(context['market_info'].get('pros', [])[:3]) if context['market_info'].get('pros') else 'N/A'}
Key Challenges: {', '.join(context['market_info'].get('cons', [])[:3]) if context['market_info'].get('cons') else 'N/A'}

---

IMPORTANT: Provide REALISTIC, DETAILED, and WELL-EXPLAINED estimates. Use specific examples and be concrete.

You MUST respond with a valid JSON object containing the following fields:
1. "team_resources": List of objects with "role", "number_of_people", "required_skills", "allocation", "description".
2. "timeline": List of objects with "phase", "duration", "key_deliverables", "dependencies".
3. "technical_infrastructure": List of strings describing specific tools, cloud services, databases, etc.
4. "risks": List of objects with "risk", "impact_level" (High/Medium/Low), "mitigation_strategy".
5. "success_metrics": List of objects with "metric", "target_value", "measurement_frequency".

Example JSON structure:
{{
  "team_resources": [
    {{
      "role": "Senior Full-Stack Developer",
      "number_of_people": "2 developers",
      "required_skills": "React, Node.js, PostgreSQL, AWS",
      "allocation": "Full-time for 8 months",
      "description": "Lead development of the core platform..."
    }}
  ],
  "timeline": [
    {{
      "phase": "Discovery & Planning",
      "duration": "4 weeks",
      "key_deliverables": "Requirements doc, architecture",
      "dependencies": "None"
    }}
  ],
  "technical_infrastructure": [
    "VS Code, Git, Docker",
    "AWS EC2 t3.large instances",
    "PostgreSQL 14+"
  ],
  "risks": [
    {{
      "risk": "Lack of AI expertise",
      "impact_level": "High",
      "mitigation_strategy": "Hire experienced ML engineer"
    }}
  ],
  "success_metrics": [
    {{
      "metric": "User Adoption Rate",
      "target_value": "500 active users",
      "measurement_frequency": "Weekly"
    }}
  ]
}}

Ensure the response is ONLY valid JSON. Do not include markdown formatting like ```json.
"""
        return prompt
    
    def _parse_estimation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the DeepSeek JSON response into structured data."""
        
        # Initialize result structure
        result = {
            "team_resources": [],
            "timeline": [],
            "technical_infrastructure": [],
            "risks": [],
            "success_metrics": []
        }
        
        try:
            # Clean response text (remove markdown code blocks if present)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            clean_text = clean_text.strip()
            
            # Parse JSON
            data = json.loads(clean_text)
            
            # Update result with parsed data, ensuring keys exist
            for key in result.keys():
                if key in data:
                    result[key] = data[key]
                    self.logger.info(f"Parsed {len(result[key])} items for {key}")
                else:
                    self.logger.warning(f"Key '{key}' missing in JSON response")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {str(e)}")
            self.logger.error(f"Failed JSON text: {response_text}")
            # Fallback: Return empty structure (or could implement basic regex fallback)
        except Exception as e:
            self.logger.error(f"Error parsing estimation response: {str(e)}")
        
        return result


# Lazy initialization - create instance only when first accessed
_resource_estimation_agent_instance = None

def get_resource_estimation_agent():
    """Get or create the resource estimation agent instance (lazy initialization)"""
    global _resource_estimation_agent_instance
    if _resource_estimation_agent_instance is None:
        logger.info("Initializing resource estimation agent...")
        _resource_estimation_agent_instance = ResourceEstimationAgent()
    return _resource_estimation_agent_instance

# For backward compatibility, create a proxy
class ResourceEstimationAgentProxy:
    """Proxy to ensure lazy initialization"""
    def __getattr__(self, name):
        return getattr(get_resource_estimation_agent(), name)

resource_estimation_agent = ResourceEstimationAgentProxy()
