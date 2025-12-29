"""Idea Research Agent - Researches market implementation of ideas using AI"""

import logging
import json
from typing import Dict, List, Optional
from services.research_agent import research_agent

logger = logging.getLogger(__name__)

class IdeaResearchAgent:
    """Agent that researches idea implementation in the market using Azure GPT-4o"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.research_agent = research_agent
    
    def research_idea_market(self, idea_title: str, idea_description: str) -> Optional[Dict]:
        """
        Research market implementation of an idea using AI
        
        Args:
            idea_title: Title of the idea
            idea_description: Description of the idea
            
        Returns:
            Dict containing market research data
        """
        idea_data = {
            "success": False,
            "idea_title": idea_title,
            "research_timestamp": "",
            "who_is_implementing": [],
            "pros_and_cons": {"pros": [], "cons": []},
            "useful_insights": [],
            "implementation_metrics": {},
            "workability_assessment": {},
            "poc_approaches": [],
            "improvement_suggestions": {},
            "sources": []
        }

        try:
            self.logger.info(f"Starting AI-powered idea market research for: {idea_title}")
            
            # Comprehensive research query
            research_query = f"""
            Research market implementation of this idea: {idea_title}
            Description: {idea_description}
            
            Find comprehensive information about:
            
            1. Companies/organizations implementing this idea
            2. Pros and cons of implementations
            3. Market insights and trends
            4. Implementation metrics and timelines
            5. Technology maturity and adoption
            6. Success stories and case studies
            
            Include ALL available data, numbers, case studies, and verified sources.
            """
            
            # Perform research
            self.logger.info(f"Researching idea implementation: {idea_title}")
            research_results = self.research_agent.research_idea(research_query, f"Idea Research: {idea_title}")
            
            if not research_results or not research_results.get('success'):
                self.logger.warning(f"Failed to research idea: {idea_title}")
                return research_results
            
            # Extract using AI - NO keyword fallbacks
            workability = self._assess_workability_ai(research_results, idea_title, idea_description)
            
            idea_data.update({
                "success": True,
                "research_timestamp": research_results.get('timestamp'),
                "who_is_implementing": self._extract_implementers_ai(research_results, idea_title),
                "pros_and_cons": self._extract_pros_cons_ai(research_results, idea_title),
                "useful_insights": self._extract_insights_ai(research_results, idea_title),
                "implementation_metrics": self._extract_metrics_ai(research_results, idea_title),
                "workability_assessment": workability,
                "poc_approaches": self._extract_poc_approaches_ai(research_results, idea_title, idea_description),
                "improvement_suggestions": self._generate_improvement_suggestions_ai(research_results, idea_title, idea_description, workability),
                "sources": self._extract_sources(research_results)
            })
            
            self.logger.info(f"Idea research completed for: {idea_title}")
            return idea_data
            
        except Exception as e:
            self.logger.error(f"Error in idea research: {str(e)}")
            idea_data["success"] = False
            idea_data["answer"] = f"Error in idea research: {str(e)}"
            return idea_data
    
    def _extract_implementers_ai(self, research_results: Dict, idea_title: str) -> List[Dict]:
        """Extract companies/organizations implementing the idea using Azure GPT-4o"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            # Get the full research content - Prefer full_content for maximum context
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            if not content_to_analyze:
                return []
            
            prompt = PromptTemplate(
                input_variables=["idea", "content"],
                template="""Extract ALL companies and organizations implementing this idea from the research.

Idea: {idea}

Research Content:
{content}

Extract EVERYTHING including:
- Company/organization names
- Detailed descriptions of their implementation approach
- Implementation timeline and scale
- Technology stack and methodology
- Results and impact achieved
- URLs and sources

Return as JSON array:
[
  {{
    "name": "Company Name",
    "description": "Detailed description of implementation",
    "url": "source URL if available"
  }}
]

Include ALL implementers found. NO LIMIT."""
            )
            
            result = llm.invoke(prompt.format(idea=idea_title, content=content_to_analyze[:32000])).content
            
            # Parse JSON using robust parser
            from utils.json_parser import extract_json_from_text
            implementers = extract_json_from_text(result, default=[])
            
            if not implementers:
                implementers = [{
                    "name": "None Found",
                    "description": "No direct existing implementations found in the current market research.",
                    "url": "N/A"
                }]
                
            self.logger.info(f"AI extracted {len(implementers)} implementers")
            return implementers
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for implementers: {e}")
            return []
    
    def _extract_pros_cons_ai(self, research_results: Dict, idea_title: str) -> Dict:
        """Extract pros and cons using Azure GPT-4o"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            # Get the full research content - Prefer full_content for maximum context
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            if not content_to_analyze:
                return {"pros": [], "cons": []}
            
            prompt = PromptTemplate(
                input_variables=["idea", "content"],
                template="""Extract ALL pros and cons of implementing this idea from the research.

Idea: {idea}

Research Content:
{content}

Extract EVERYTHING including:
PROS:
- Benefits and advantages
- Success stories
- Positive outcomes
- Cost savings
- Efficiency gains
- User satisfaction
- Any other benefits

CONS:
- Challenges and disadvantages
- Implementation difficulties
- Risks and limitations
- Cost concerns
- Technical challenges
- User resistance
- Any other drawbacks

Return as JSON:
{{
  "pros": ["detailed pro 1", "detailed pro 2", ...],
  "cons": ["detailed con 1", "detailed con 2", ...]
}}

Include ALL pros and cons found. NO LIMIT."""
            )
            
            result = llm.invoke(prompt.format(idea=idea_title, content=content_to_analyze[:32000])).content
            
            # Parse JSON using robust parser
            from utils.json_parser import extract_json_from_text
            pros_cons = extract_json_from_text(result, default={"pros": [], "cons": []})
            self.logger.info(f"AI extracted {len(pros_cons.get('pros', []))} pros and {len(pros_cons.get('cons', []))} cons")
            return pros_cons
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for pros/cons: {e}")
            return {"pros": [], "cons": []}
    
    def _extract_insights_ai(self, research_results: Dict, idea_title: str) -> List[Dict]:
        """Extract market insights using Azure GPT-4o"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            # Get the full research content - Prefer full_content for maximum context
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            if not content_to_analyze:
                return []
            
            prompt = PromptTemplate(
                input_variables=["idea", "content"],
                template="""Extract ALL useful market insights about this idea from the research.

Idea: {idea}

Research Content:
{content}

Extract EVERYTHING including:
- Market trends and growth patterns
- Technology maturity and readiness
- User adoption patterns and rates
- Implementation challenges and solutions
- Best practices and lessons learned
- Market size and projections
- Competitive landscape
- Industry forecasts
- Expert opinions
- Statistical data
- Any other valuable insights

Return as JSON array with categorized insights:
[
  {{
    "type": "Market Trend|Technology Maturity|User Adoption|Challenge|Best Practice|Market Size|Other",
    "insight": "detailed insight text",
    "details": "additional context if available",
    "source": "source URL if available"
  }}
]

Include ALL insights found. NO LIMIT."""
            )
            
            result = llm.invoke(prompt.format(idea=idea_title, content=content_to_analyze[:32000])).content
            
            # Parse JSON using robust parser
            from utils.json_parser import extract_json_from_text
            insights = extract_json_from_text(result, default=[])
            self.logger.info(f"AI extracted {len(insights)} insights")
            return insights
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for insights: {e}")
            return []
    
    def _extract_metrics_ai(self, research_results: Dict, idea_title: str) -> Dict:
        """Extract implementation metrics using Azure GPT-4o"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            # Get the full research content - Prefer full_content for maximum context
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            if not content_to_analyze:
                return {
                    "implementation_timelines": [],
                    "scale_metrics": [],
                    "adoption_rates": [],
                    "technology_maturity": []
                }
            
            prompt = PromptTemplate(
                input_variables=["idea", "content"],
                template="""Extract ALL implementation metrics for this idea from the research.

Idea: {idea}

Research Content:
{content}

Extract EVERYTHING including:
- Implementation timelines (how long deployments take, phases, milestones)
- Scale metrics (number of users, customers, revenue, market share)
- Adoption rates (percentages, growth)
- Technology maturity (maturity level, readiness, proven vs experimental)

Return as JSON:
{{
  "implementation_timelines": ["timeline 1", "timeline 2", ...],
  "scale_metrics": ["metric 1", "metric 2", ...],
  "adoption_rates": ["rate 1", "rate 2", ...],
  "technology_maturity": ["maturity info 1", "maturity info 2", ...]
}}

Include ALL metrics found. NO LIMIT."""
            )
            
            result = llm.invoke(prompt.format(idea=idea_title, content=content_to_analyze[:32000])).content
            
            # Parse JSON using robust parser
            from utils.json_parser import extract_json_from_text
            metrics = extract_json_from_text(result, default={
                "implementation_timelines": [],
                "scale_metrics": [],
                "adoption_rates": [],
                "technology_maturity": []
            })
            self.logger.info(f"AI extracted metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for metrics: {e}")
            return {
                "implementation_timelines": [],
                "scale_metrics": [],
                "adoption_rates": [],
                "technology_maturity": []
            }
    
    def _assess_workability_ai(self, research_results: Dict, idea_title: str, idea_description: str) -> Dict:
        """Assess whether the POC is workable or not using AI analysis"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            if not content_to_analyze:
                return {
                    "is_workable": True,
                    "confidence": "Low",
                    "verdict": "Unable to assess - insufficient research data",
                    "reasoning": "No market research data available to assess workability",
                    "similar_implementations": [],
                    "key_challenges": [],
                    "success_factors": []
                }
            
            prompt = PromptTemplate(
                input_variables=["idea", "description", "content"],
                template="""Analyze if this POC idea is WORKABLE (feasible to implement as a proof of concept).

POC Idea: {idea}
Description: {description}

Market Research:
{content}

Assess workability based on:
1. Do similar implementations exist? (If yes, it's likely workable)
2. Is the technology mature enough?
3. Are there major technical blockers?
4. What are the key challenges to overcome?
5. What factors would make this POC successful?

Return a JSON assessment:
{{
  "is_workable": true or false,
  "confidence": "High" or "Medium" or "Low",
  "verdict": "WORKABLE" or "NOT WORKABLE" or "NEEDS VALIDATION",
  "reasoning": "One paragraph explaining why this is or isn't workable as a POC",
  "similar_implementations": ["List of similar existing implementations found"],
  "key_challenges": ["Challenge 1", "Challenge 2", ...],
  "success_factors": ["What would make this POC successful"]
}}

Be practical - most POCs are workable with the right scope. Mark as NOT WORKABLE only if there are fundamental technical impossibilities."""
            )
            
            result = llm.invoke(prompt.format(
                idea=idea_title, 
                description=idea_description, 
                content=content_to_analyze[:20000]
            )).content
            
            from utils.json_parser import extract_json_from_text
            assessment = extract_json_from_text(result, default={
                "is_workable": True,
                "confidence": "Medium",
                "verdict": "WORKABLE",
                "reasoning": "Based on available research, this POC appears feasible",
                "similar_implementations": [],
                "key_challenges": [],
                "success_factors": []
            })
            
            self.logger.info(f"Workability assessment: {assessment.get('verdict')}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"AI workability assessment failed: {e}")
            return {
                "is_workable": True,
                "confidence": "Low",
                "verdict": "Unable to assess",
                "reasoning": f"Assessment failed: {str(e)}",
                "similar_implementations": [],
                "key_challenges": [],
                "success_factors": []
            }
    
    def _generate_improvement_suggestions_ai(self, research_results: Dict, idea_title: str, idea_description: str, workability: Dict) -> Dict:
        """Generate suggestions on how to improve the POC idea"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            # Get challenges and similar implementations from workability
            challenges = workability.get('key_challenges', [])
            similar_impls = workability.get('similar_implementations', [])
            is_workable = workability.get('is_workable', True)
            
            prompt = PromptTemplate(
                input_variables=["idea", "description", "content", "challenges", "similar_impls", "is_workable"],
                template="""Based on the POC idea and market research, provide specific suggestions to improve this idea.

POC Idea: {idea}
Description: {description}

Current Challenges Identified:
{challenges}

Similar Implementations Found:
{similar_impls}

Market Research:
{content}

Current Workability: {"WORKABLE" if {is_workable} else "NOT WORKABLE"}

Provide actionable improvement suggestions:

1. If WORKABLE: How can this POC be made even better, more innovative, or more impactful?
2. If NOT WORKABLE: What changes would make this feasible?
3. What can be learned from similar implementations?
4. How to differentiate from existing solutions?
5. What features or approaches should be prioritized?

Return as JSON:
{{
  "overall_recommendation": "A brief summary of how to improve this idea (2-3 sentences)",
  "do_this_instead": ["If the current approach has issues, suggest alternative approaches"],
  "add_these_features": ["Specific features that would make the POC more compelling"],
  "learn_from_others": ["What to learn from existing similar solutions"],
  "quick_wins": ["Easy improvements that can be made immediately"],
  "avoid_these_mistakes": ["Common pitfalls to avoid based on market research"],
  "differentiation_tips": ["How to make this POC stand out from similar solutions"]
}}

Be specific and actionable. Focus on practical improvements."""
            )
            
            result = llm.invoke(prompt.format(
                idea=idea_title, 
                description=idea_description, 
                content=content_to_analyze[:15000] if content_to_analyze else "No additional context",
                challenges="\n".join([f"- {c}" for c in challenges]) if challenges else "None identified",
                similar_impls="\n".join([f"- {s}" for s in similar_impls]) if similar_impls else "None found",
                is_workable=str(is_workable)
            )).content
            
            from utils.json_parser import extract_json_from_text
            suggestions = extract_json_from_text(result, default={
                "overall_recommendation": "Focus on building a minimal viable POC first",
                "do_this_instead": [],
                "add_these_features": [],
                "learn_from_others": [],
                "quick_wins": [],
                "avoid_these_mistakes": [],
                "differentiation_tips": []
            })
            
            self.logger.info(f"Generated improvement suggestions for: {idea_title}")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"AI improvement suggestions failed: {e}")
            return {
                "overall_recommendation": "Unable to generate improvement suggestions",
                "do_this_instead": [],
                "add_these_features": [],
                "learn_from_others": [],
                "quick_wins": [],
                "avoid_these_mistakes": [],
                "differentiation_tips": []
            }
    
    def _extract_poc_approaches_ai(self, research_results: Dict, idea_title: str, idea_description: str) -> List[Dict]:
        """Extract different ways to implement this POC with tools and architecture"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            llm = self.research_agent.llm
            content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '')
            
            prompt = PromptTemplate(
                input_variables=["idea", "description", "content"],
                template="""Based on the POC idea and market research, suggest different implementation approaches.

POC Idea: {idea}
Description: {description}

Market Research (for context):
{content}

Provide 2-3 different ways to implement this POC, each with:
1. A clear approach name
2. Tools and technologies to use
3. Simple architecture description
4. Pros and cons of this approach
5. Estimated complexity (Low/Medium/High)

Return as JSON array:
[
  {{
    "approach_name": "Approach 1 Name",
    "description": "Brief description of this approach",
    "tools_and_technologies": ["Tool 1", "Tool 2", "Framework X", "Cloud Service Y"],
    "architecture": "Simple description of the architecture (e.g., 'Frontend -> API -> Database' or 'Event-driven with message queue')",
    "pros": ["Pro 1", "Pro 2"],
    "cons": ["Con 1", "Con 2"],
    "complexity": "Low" or "Medium" or "High",
    "best_for": "When to use this approach"
  }}
]

Focus on practical, modern technologies. Include both simple and more sophisticated approaches."""
            )
            
            result = llm.invoke(prompt.format(
                idea=idea_title, 
                description=idea_description, 
                content=content_to_analyze[:15000] if content_to_analyze else "No additional context available"
            )).content
            
            from utils.json_parser import extract_json_from_text
            approaches = extract_json_from_text(result, default=[])
            
            self.logger.info(f"AI extracted {len(approaches)} POC implementation approaches")
            return approaches
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for POC approaches: {e}")
            return []

    def _extract_sources(self, research_results: Dict) -> List[Dict]:
        """Extract research sources"""
        sources = []
        seen_urls = set()
        
        # Extract from existing solutions
        existing_solutions = research_results.get('existing_solutions', [])
        for solution in existing_solutions:
            url = solution.get('url')
            title = solution.get('title', 'Implementation Example')
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Implementation",
                    "title": title[:150],
                    "url": url,
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        # Extract from trends
        trends = research_results.get('trends', [])
        for trend in trends:
            url = trend.get('url') or trend.get('source')
            title = trend.get('trend', 'Market Analysis')
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Market Insight",
                    "title": title[:150],
                    "url": url,
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        # Extract from competitors
        competitors = research_results.get('competitors', [])
        for comp in competitors:
            url = comp.get('url')
            name = comp.get('name', 'Competitor')
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Competitor",
                    "title": name[:150],
                    "url": url,
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        return sources


# Create singleton instance
_idea_research_agent_instance = None

def get_idea_research_agent():
    """Get or create the idea research agent instance"""
    global _idea_research_agent_instance
    if _idea_research_agent_instance is None:
        logger.info("Initializing idea research agent...")
        _idea_research_agent_instance = IdeaResearchAgent()
    return _idea_research_agent_instance

# For backward compatibility
class IdeaResearchAgentProxy:
    """Proxy to ensure lazy initialization"""
    def __getattr__(self, name):
        return getattr(get_idea_research_agent(), name)

idea_research_agent = IdeaResearchAgentProxy()
