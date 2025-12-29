import os
from typing import Dict, Any
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)

class AIScoreService:
    def __init__(self):
        self.api_key = os.getenv("GPT_4O_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Define IdeaScore model
        class IdeaScore(BaseModel):
            score: int = Field(description="Score from 0-100")
            feedback: str = Field(description="Detailed feedback about the idea")
            strengths: list[str] = Field(description="Key strengths of the idea")
            improvements: list[str] = Field(description="Areas for improvement")
        
        self.IdeaScore = IdeaScore
        
        # Try Azure OpenAI first, fallback to DeepSeek
        if self.api_key and self.azure_endpoint and not self.api_key.startswith("your_"):
            try:
                # Clean endpoint if needed
                if "openai/deployments" in self.azure_endpoint:
                    from urllib.parse import urlparse
                    parsed = urlparse(self.azure_endpoint)
                    self.azure_endpoint = f"{parsed.scheme}://{parsed.netloc}/"
                
                self.llm = AzureChatOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version="2024-02-01",
                    azure_deployment="gpt-4o",
                    temperature=0.3
                )
                logger.info("Azure OpenAI GPT-4o initialized for AI Score Service")
                self.ready = True
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self._init_deepseek()
        elif self.deepseek_api_key and not self.deepseek_api_key.startswith("your_"):
            self._init_deepseek()
        else:
            logger.warning("No AI API configuration found for AI Score Service")
            self.ready = False
            return
        
        if self.ready:
            self._setup_prompt()
    
    def _init_deepseek(self):
        """Initialize DeepSeek as fallback LLM"""
        try:
            self.llm = ChatOpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com",
                model="deepseek-chat",
                temperature=0.3
            )
            logger.info("DeepSeek initialized for AI Score Service")
            self.ready = True
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek: {e}")
            self.ready = False
    
    def _setup_prompt(self):
        """Setup the scoring prompt template"""
        self.scoring_prompt = ChatPromptTemplate.from_template("""
You are an expert idea evaluator for DexKo Group. Evaluate the business idea and provide a score with feedback.

**Idea Details:**
- Title: {title}
- Department: {department}
- Content: {content}

**Evaluation Criteria:**
1. Innovation (0-25 points)
2. Feasibility (0-25 points)
3. Business Impact (0-25 points)
4. Clarity (0-25 points)

Provide a JSON response with: score (0-100), feedback (detailed), strengths (2-3), improvements (2-3).
""")
        
        self.parser = JsonOutputParser(pydantic_object=self.IdeaScore)

    def score_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score an idea using Azure GPT-4o"""
        try:
            if not self.ready:
                logger.error("AI Score Service not ready")
                return {"success": False, "error": "AI service not available"}
            
            logger.info(f"Scoring idea: {idea_data.get('title', 'Untitled')}")
            
            content = self._prepare_idea_content(idea_data)
            
            chain = self.scoring_prompt | self.llm | self.parser
            result = chain.invoke({
                "title": idea_data.get("title", ""),
                "department": idea_data.get("metadata", {}).get("department", "General"),
                "content": content
            })
            
            # Handle both dictionary and object responses
            if isinstance(result, dict):
                return {
                    "success": True,
                    "score": result.get("score", 0),
                    "feedback": result.get("feedback", ""),
                    "strengths": result.get("strengths", []),
                    "improvements": result.get("improvements", [])
                }
            else:
                return {
                    "success": True,
                    "score": getattr(result, "score", 0),
                    "feedback": getattr(result, "feedback", ""),
                    "strengths": getattr(result, "strengths", []),
                    "improvements": getattr(result, "improvements", [])
                }
        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return {"success": False, "error": str(e)}

    def _prepare_idea_content(self, idea_data: Dict[str, Any]) -> str:
        """Prepare idea content for scoring"""
        parts = []
        
        if idea_data.get("original_idea"):
            parts.append(f"Original Idea: {idea_data['original_idea']}")
        if idea_data.get("rephrased_idea"):
            parts.append(f"Rephrased: {idea_data['rephrased_idea']}")
            
        # Include research data if available
        research_data = idea_data.get("research_data", {})
        if research_data:
            if research_data.get("company_research"):
                parts.append(f"Company Context: {str(research_data['company_research'])[:2000]}")
            if research_data.get("idea_research"):
                parts.append(f"Market Research: {str(research_data['idea_research'])[:2000]}")
            if research_data.get("roi_analysis"):
                parts.append(f"ROI Analysis: {str(research_data['roi_analysis'])[:2000]}")

        if idea_data.get("drafts"):
            for section, draft in idea_data['drafts'].items():
                if draft:
                    draft_str = str(draft)
                    parts.append(f"{section}: {draft_str[:2000]}")
        
        return "\n".join(parts) if parts else "No content provided"

# Global instance
ai_score_service = AIScoreService()
