"""AI Question Generator - Generates personalized development questions based on research insights"""

import logging
import os
from typing import Dict, List, Optional
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class QuestionGenerator:
    """Generates personalized development questions based on research insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm = None
        
        try:
            # Use existing Azure OpenAI configuration from environment
            gpt_4o_api_key = os.getenv("GPT_4O_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            
            if not gpt_4o_api_key or not azure_endpoint:
                # Try to load from .env if not found (just in case)
                from dotenv import load_dotenv
                load_dotenv()
                gpt_4o_api_key = os.getenv("GPT_4O_API_KEY")
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            
            # Try Azure OpenAI first
            if gpt_4o_api_key and azure_endpoint and not gpt_4o_api_key.startswith("your_"):
                # Clean endpoint if it contains the full path
                if "openai/deployments" in azure_endpoint:
                    from urllib.parse import urlparse
                    parsed = urlparse(azure_endpoint)
                    azure_endpoint = f"{parsed.scheme}://{parsed.netloc}/"
                    logger.info(f"cleaned Azure endpoint to: {azure_endpoint}")

                self.llm = AzureChatOpenAI(
                    api_key=gpt_4o_api_key,
                    azure_endpoint=azure_endpoint,
                    api_version="2024-02-01",
                    azure_deployment="gpt-4o",
                    temperature=0.7
                )
                logger.info("Azure OpenAI GPT-4o initialized for question generation")
            # Fallback to DeepSeek
            elif deepseek_api_key and not deepseek_api_key.startswith("your_"):
                self.llm = ChatOpenAI(
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com",
                    model="deepseek-chat",
                    temperature=0.7
                )
                logger.info("DeepSeek initialized for question generation")
            else:
                logger.error("No AI API configuration found for question generation")

        except Exception as e:
            logger.error(f"LLM initialization failed: {str(e)}")
    
    def generate_questions(self, company_research: Dict, idea_research: Dict, 
                          company_name: str, idea_title: str, idea_description: str) -> List[Dict]:
        """
        Generate personalized development questions based on research insights
        
        Args:
            company_research: Company research data
            idea_research: Idea research data
            company_name: Target company name
            idea_title: Idea title
            idea_description: Idea description
            
        Returns:
            List of personalized development questions
        """
        try:
            self.logger.info("Generating AI-powered development questions")
            
            if not self.llm:
                self.logger.error("LLM not available - cannot generate questions without AI")
                return []
            
            # Check if we have sufficient research data
            if not self._has_sufficient_research_data(company_research, idea_research):
                self.logger.error("Insufficient research data for question generation")
                return []
            
            # Prepare research context for AI
            research_context = self._prepare_research_context(
                company_research, idea_research, 
                company_name, idea_title, idea_description
            )
            
            # Generate questions using AI
            questions = self._generate_with_ai(research_context)
            
            if questions:
                self.logger.info(f"AI generated {len(questions)} personalized questions")
                return questions
            else:
                self.logger.error("AI question generation failed - no questions generated")
                return []
                
        except Exception as e:
            self.logger.error(f"Error generating questions: {str(e)}")
            return []
    
    def _prepare_research_context(self, company_research: Dict, idea_research: Dict, 
                                company_name: str, idea_title: str, idea_description: str) -> Dict:
        """Prepare research context for AI question generation"""
        
        context = {
            "company_name": company_name,
            "idea_title": idea_title,
            "idea_description": idea_description,
            "company_overview": "",
            "company_financials": "",
            "company_opportunities": "",
            "company_challenges": "",
            "market_insights": "",
            "existing_solutions": "",
            "competitors": "",
            "market_trends": ""
        }
        
        # Company research context (NEW STRUCTURE)
        if company_research:
            context["company_overview"] = company_research.get('what_company_does', '')
            
            # Financial data
            financials = company_research.get('financials', {})
            financial_text = []
            if financials.get('annual_revenue'):
                financial_text.append(f"Annual Revenue: {financials['annual_revenue']}")
            if financials.get('revenue_growth'):
                financial_text.append(f"Revenue Growth: {financials['revenue_growth']}")
            if financials.get('market_cap'):
                financial_text.append(f"Market Cap: {financials['market_cap']}")
            if financials.get('recent_performance'):
                financial_text.append(f"Recent Performance: {financials['recent_performance']}")
            context["company_financials"] = "\n".join(financial_text)
            
            # Initiatives and goals (opportunities)
            initiatives = company_research.get('current_initiatives_and_goals', [])
            context["company_opportunities"] = "\n".join([f"- {init}" for init in initiatives[:20]])  # Increased limit
            
            # Challenges (extracted from research)
            challenges = company_research.get('challenges', [])
            context["company_challenges"] = "\n".join([f"- {challenge}" for challenge in challenges[:20]])  # Increased limit
        
        # Idea research context (NEW STRUCTURE)
        if idea_research and idea_research.get('success'):
            # Market insights from useful insights
            insights = idea_research.get('useful_insights', [])
            if insights:
                context["market_insights"] = "\n".join([
                    f"- {insight.get('insight', '')}: {insight.get('details', '')}" 
                    for insight in insights[:15]  # Increased limit
                ])
            
            # Who is implementing (existing solutions)
            implementers = idea_research.get('who_is_implementing', [])
            if implementers:
                context["existing_solutions"] = "\n".join([
                    f"- {impl.get('name', '')}: {impl.get('description', '')}" 
                    for impl in implementers[:15]  # Increased limit
                ])
            
            # Pros and cons
            pros_cons = idea_research.get('pros_and_cons', {})
            if pros_cons:
                pros = pros_cons.get('pros', [])
                cons = pros_cons.get('cons', [])
                context["competitors"] = f"Pros:\n" + "\n".join([f"- {pro}" for pro in pros[:10]]) + \
                                       f"\n\nCons:\n" + "\n".join([f"- {con}" for con in cons[:10]])  # Increased limits
            
            # Market trends from insights
            if insights:
                trend_insights = [insight for insight in insights if insight.get('type') == 'Market Trend']
                if trend_insights:
                    context["market_trends"] = "\n".join([
                        f"- {trend.get('insight', '')}: {trend.get('details', '')}" 
                        for trend in trend_insights[:10]  # Increased limit
                    ])
        
        # ROI analysis removed - no longer included in question generation
        
        return context
    
    def _generate_with_ai(self, research_context: Dict) -> List[Dict]:
        """Generate POC-focused questions using AI to validate feasibility and value"""
        try:
            prompt = PromptTemplate(
                input_variables=[
                    "company_name", "idea_title", "idea_description",
                    "company_overview", "company_financials", "company_opportunities", "company_challenges",
                    "market_insights", "existing_solutions", "competitors", "market_trends"
                ],
                template="""You are an AI system generating development questions STRICTLY for a Proof of Concept (POC).

POC CONTEXT:
- POC Title: {idea_title}
- POC Description: {idea_description}

MARKET CONTEXT (for reference only - DO NOT ask questions about this):
- Similar solutions exist: {existing_solutions}

TASK:
Generate ONLY the ESSENTIAL questions (between 3-5 questions) needed to validate this POC. Generate FEWER questions if the POC is simple or straightforward. Only ask what is truly necessary.

QUESTION CATEGORIES (pick only the most relevant ones):
1. **Problem & Use Case** - What specific problem does this POC solve and for whom?
2. **Data & Inputs** - What data/inputs are needed to demonstrate the POC?
3. **Success Criteria** - What outcome proves the POC works?
4. **Technical Approach** - What is the core technical approach or method?
5. **Scope Boundaries** - What is explicitly in-scope vs out-of-scope?

CRITICAL RULES:
- Generate 3-5 questions MAXIMUM (fewer is better if sufficient)
- Focus ONLY on the POC itself - what needs to be built and demonstrated
- DO NOT mention company names in questions
- DO NOT ask about business strategy, ROI, competitors, or market positioning
- DO NOT ask about scaling, production deployment, or long-term plans
- Questions must be answerable by the person building the POC
- Keep questions short, clear, and actionable

GOOD EXAMPLES:
- "What specific problem does this POC solve?"
- "What data or inputs will be used to test the POC?"
- "What output or result will demonstrate that the POC works?"
- "What is the core technical approach (e.g., API, ML model, automation script)?"

BAD EXAMPLES (DO NOT USE):
- "How does this align with [Company] strategy?" ❌
- "What is the ROI?" ❌
- "How will this compete with existing solutions?" ❌
- "How will this scale?" ❌

Return questions in this JSON format (3-5 questions only):
[
  {{
    "category": "Problem & Use Case",
    "question": "Clear, direct POC question",
    "priority": "Must Answer",
    "key": "problem_1",
    "follow_ups": []
  }}
]

Generate ONLY essential POC questions now (3-5 maximum):"""
            )
            
            result = self.llm.invoke(prompt.format(**research_context)).content
            
            # Parse the JSON response using robust parser
            from utils.json_parser import extract_json_from_text
            questions = extract_json_from_text(result, default=[])
            
            # Validate the structure and limit to 5 questions max
            if isinstance(questions, list) and len(questions) > 0:
                validated_questions = []
                for q in questions[:5]:  # Limit to max 5 questions
                    required_fields = ['category', 'question', 'priority', 'key', 'follow_ups']
                    if not all(k in q for k in required_fields):
                        # Add missing fields with defaults
                        q.setdefault('category', 'General')
                        q.setdefault('priority', 'Must Answer')
                        q.setdefault('key', f'question_{len(validated_questions)+1}')
                        q.setdefault('follow_ups', [])
                    if q['priority'] not in ['Must Answer', 'Should Answer', 'Nice to Have']:
                        q['priority'] = 'Must Answer'
                    validated_questions.append(q)
                return validated_questions
            
            self.logger.error(f"AI question generation failed - no questions generated or invalid format. Raw response: {result}")
            return []
            
        except Exception as e:
            self.logger.error(f"AI question generation failed: {str(e)}")
            return []
    
    def _has_sufficient_research_data(self, company_research: Dict, idea_research: Dict) -> bool:
        """Check if we have sufficient research data for question generation"""
        # We now trust the AI to generate questions even with partial data
        # The previous hardcoded checks are removed to allow for maximum flexibility
        return True


# Lazy initialization - create instance only when first accessed
_question_generator_instance = None

def get_question_generator():
    """Get or create the question generator instance (lazy initialization)"""
    global _question_generator_instance
    if _question_generator_instance is None:
        logger.info("Initializing question generator...")
        _question_generator_instance = QuestionGenerator()
    return _question_generator_instance

# For backward compatibility
class QuestionGeneratorProxy:
    """Proxy to ensure lazy initialization"""
    def __getattr__(self, name):
        return getattr(get_question_generator(), name)

question_generator = QuestionGeneratorProxy()
