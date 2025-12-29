"""Enhanced AI Score Service with detailed criterion reasoning, confidence scores, and bias warnings"""

import os
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)


class CriterionScore(BaseModel):
    """Individual criterion score with reasoning"""
    criterion_name: str = Field(description="Name of the evaluation criterion")
    score: int = Field(description="Score for this criterion (0-25)")
    max_score: int = Field(default=25, description="Maximum possible score")
    reasoning: str = Field(description="Detailed reasoning for this score")
    evidence: List[str] = Field(description="Evidence from the idea supporting this score")
    confidence: float = Field(description="Confidence level for this score (0.0-1.0)")


class BiasWarning(BaseModel):
    """Bias or data quality warning"""
    warning_type: str = Field(description="Type of bias/warning: insufficient_data, domain_bias, recency_bias, etc.")
    severity: str = Field(description="Severity level: low, medium, high")
    description: str = Field(description="Detailed description of the potential bias")
    mitigation: str = Field(description="Suggested mitigation or additional data needed")


class EnhancedIdeaScore(BaseModel):
    """Comprehensive idea score with detailed analysis"""
    total_score: int = Field(description="Total score from 0-100")
    criterion_scores: List[CriterionScore] = Field(description="Breakdown of scores by criterion")
    overall_confidence: float = Field(description="Overall confidence in the evaluation (0.0-1.0)")
    bias_warnings: List[BiasWarning] = Field(description="List of potential biases or data quality issues")
    feedback: str = Field(description="Overall detailed feedback about the idea")
    strengths: List[str] = Field(description="Key strengths of the idea")
    improvements: List[str] = Field(description="Areas for improvement")
    data_quality_notes: str = Field(description="Notes about the quality and completeness of input data")


class EnhancedAIScoreService:
    """Enhanced AI scoring service with transparency features"""
    
    def __init__(self):
        self.api_key = os.getenv("GPT_4O_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.ready = False
        
        # Try Azure OpenAI first, fallback to DeepSeek
        if self.api_key and self.azure_endpoint and not self.api_key.startswith("your_"):
            try:
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
                logger.info("Azure OpenAI GPT-4o initialized for Enhanced AI Score Service")
                self.ready = True
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self._init_deepseek()
        elif self.deepseek_api_key and not self.deepseek_api_key.startswith("your_"):
            self._init_deepseek()
        else:
            logger.warning("No AI API configuration found for Enhanced AI Score Service")
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
            logger.info("DeepSeek initialized for Enhanced AI Score Service")
            self.ready = True
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek: {e}")
            self.ready = False
    
    def _setup_prompt(self):
        """Setup the enhanced scoring prompt template"""
        self.scoring_prompt = ChatPromptTemplate.from_template("""
You are an expert idea evaluator providing transparent, explainable scoring. 
Evaluate the business idea and provide detailed per-criterion analysis with confidence levels.

**Idea Details:**
- Title: {title}
- Department: {department}
- Content: {content}

**Evaluation Criteria (each scored 0-25):**

1. **Innovation (0-25 points)**
   - Novelty of the concept
   - Differentiation from existing solutions
   - Creative problem-solving approach

2. **Feasibility (0-25 points)**
   - Technical viability
   - Resource requirements
   - Implementation complexity

3. **Business Impact (0-25 points)**
   - Potential ROI
   - Market opportunity
   - Strategic alignment

4. **Clarity (0-25 points)**
   - Clear problem statement
   - Well-defined solution
   - Measurable outcomes

**IMPORTANT INSTRUCTIONS:**
For EACH criterion, you MUST provide:
1. A score (0-25)
2. Detailed reasoning explaining the score
3. Specific evidence from the idea content
4. Confidence level (0.0-1.0) based on available information

Also identify:
- Potential biases or data quality issues
- Areas where more information is needed
- Overall confidence in evaluation

Respond ONLY with valid JSON matching this structure:
{{
    "total_score": <0-100>,
    "criterion_scores": [
        {{
            "criterion_name": "Innovation",
            "score": <0-25>,
            "max_score": 25,
            "reasoning": "<detailed explanation>",
            "evidence": ["<quote or reference from idea>", ...],
            "confidence": <0.0-1.0>
        }},
        {{
            "criterion_name": "Feasibility",
            "score": <0-25>,
            "max_score": 25,
            "reasoning": "<detailed explanation>",
            "evidence": ["<quote or reference from idea>", ...],
            "confidence": <0.0-1.0>
        }},
        {{
            "criterion_name": "Business Impact",
            "score": <0-25>,
            "max_score": 25,
            "reasoning": "<detailed explanation>",
            "evidence": ["<quote or reference from idea>", ...],
            "confidence": <0.0-1.0>
        }},
        {{
            "criterion_name": "Clarity",
            "score": <0-25>,
            "max_score": 25,
            "reasoning": "<detailed explanation>",
            "evidence": ["<quote or reference from idea>", ...],
            "confidence": <0.0-1.0>
        }}
    ],
    "overall_confidence": <0.0-1.0>,
    "bias_warnings": [
        {{
            "warning_type": "<insufficient_data|domain_bias|recency_bias|etc>",
            "severity": "<low|medium|high>",
            "description": "<detailed description>",
            "mitigation": "<suggested action>"
        }}
    ],
    "feedback": "<comprehensive feedback>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "improvements": ["<improvement1>", "<improvement2>", ...],
    "data_quality_notes": "<notes about input data quality>"
}}
""")
        
        self.parser = JsonOutputParser(pydantic_object=EnhancedIdeaScore)
    
    def score_idea_enhanced(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score an idea with detailed per-criterion analysis"""
        try:
            if not self.ready:
                logger.error("Enhanced AI Score Service not ready")
                return {"success": False, "error": "AI service not available"}
            
            logger.info(f"Enhanced scoring for idea: {idea_data.get('title', 'Untitled')}")
            
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
                    "total_score": result.get("total_score", 0),
                    "criterion_scores": result.get("criterion_scores", []),
                    "overall_confidence": result.get("overall_confidence", 0.5),
                    "bias_warnings": result.get("bias_warnings", []),
                    "feedback": result.get("feedback", ""),
                    "strengths": result.get("strengths", []),
                    "improvements": result.get("improvements", []),
                    "data_quality_notes": result.get("data_quality_notes", "")
                }
            else:
                return {
                    "success": True,
                    "total_score": getattr(result, "total_score", 0),
                    "criterion_scores": getattr(result, "criterion_scores", []),
                    "overall_confidence": getattr(result, "overall_confidence", 0.5),
                    "bias_warnings": getattr(result, "bias_warnings", []),
                    "feedback": getattr(result, "feedback", ""),
                    "strengths": getattr(result, "strengths", []),
                    "improvements": getattr(result, "improvements", []),
                    "data_quality_notes": getattr(result, "data_quality_notes", "")
                }
        except Exception as e:
            logger.error(f"Enhanced scoring failed: {e}")
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
    
    def get_score_explanation(self, enhanced_score: Dict[str, Any]) -> Dict[str, Any]:
        """Format the enhanced score for UI display with 'Why this score?' section"""
        if not enhanced_score.get("success"):
            return {"success": False, "error": enhanced_score.get("error", "Unknown error")}
        
        explanation = {
            "success": True,
            "total_score": enhanced_score.get("total_score", 0),
            "overall_confidence": enhanced_score.get("overall_confidence", 0.5),
            "confidence_label": self._get_confidence_label(enhanced_score.get("overall_confidence", 0.5)),
            "criteria_breakdown": [],
            "bias_alerts": [],
            "summary": enhanced_score.get("feedback", ""),
            "strengths": enhanced_score.get("strengths", []),
            "improvements": enhanced_score.get("improvements", []),
            "data_quality": enhanced_score.get("data_quality_notes", "")
        }
        
        # Format criterion scores
        for criterion in enhanced_score.get("criterion_scores", []):
            if isinstance(criterion, dict):
                explanation["criteria_breakdown"].append({
                    "name": criterion.get("criterion_name", "Unknown"),
                    "score": criterion.get("score", 0),
                    "max_score": criterion.get("max_score", 25),
                    "percentage": round((criterion.get("score", 0) / criterion.get("max_score", 25)) * 100, 1),
                    "reasoning": criterion.get("reasoning", ""),
                    "evidence": criterion.get("evidence", []),
                    "confidence": criterion.get("confidence", 0.5),
                    "confidence_label": self._get_confidence_label(criterion.get("confidence", 0.5))
                })
        
        # Format bias warnings
        for warning in enhanced_score.get("bias_warnings", []):
            if isinstance(warning, dict):
                explanation["bias_alerts"].append({
                    "type": warning.get("warning_type", "unknown"),
                    "severity": warning.get("severity", "low"),
                    "description": warning.get("description", ""),
                    "mitigation": warning.get("mitigation", ""),
                    "icon": self._get_severity_icon(warning.get("severity", "low"))
                })
        
        return explanation
    
    def _get_confidence_label(self, confidence: float) -> str:
        """Convert confidence score to human-readable label"""
        if confidence >= 0.8:
            return "High Confidence"
        elif confidence >= 0.6:
            return "Moderate Confidence"
        elif confidence >= 0.4:
            return "Low Confidence"
        else:
            return "Very Low Confidence"
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        return icons.get(severity.lower(), "⚪")


# Global instance
enhanced_ai_score_service = EnhancedAIScoreService()
