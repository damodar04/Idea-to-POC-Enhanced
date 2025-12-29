"""Research Agent Service - Performs market research using Tavily API with AI content understanding"""

import logging
from typing import Dict, List, Any
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from services.text_cleaner import clean_html_content, extract_clean_sentences, truncate_smart
import concurrent.futures
import threading

# Configure logging
logger = logging.getLogger(__name__)

class ResearchAgent:
    """Research agent that performs market research using Tavily API with content extraction"""
    
    def __init__(self):
        """Initialize research agent with Tavily API"""
        self.client = None
        self.llm = None
        self.tavily_api_key = None
        self.initialize()
        
    def initialize(self):
        """Initialize or re-initialize the agent"""
        logger.info("Initializing ResearchAgent...")
        
        # 1. Force reload environment variables
        try:
            # Try multiple possible locations for .env
            possible_paths = [
                Path(__file__).parent.parent / '.env',  # services/../.env
                Path.cwd() / '.env',                    # Current working dir
                Path("g:/DEXKO/I2POC_Copy/I2POC_Streamlit/.env") # Hardcoded fallback
            ]
            
            env_loaded = False
            for env_path in possible_paths:
                if env_path.exists():
                    logger.info(f"Loading .env from: {env_path}")
                    load_dotenv(dotenv_path=env_path, override=True)
                    env_loaded = True
                    break
            
            if not env_loaded:
                logger.warning(".env file not found in standard locations")
                # Try default load
                load_dotenv()
                
        except Exception as e:
            logger.error(f"Error loading .env: {e}")

        # 2. Initialize Tavily Client
        try:
            from tavily import TavilyClient
            
            self.tavily_api_key = os.getenv("TAVILY_API_KEY")
            
            if not self.tavily_api_key:
                logger.error("TAVILY_API_KEY not found in environment variables")
                self.client = None
            elif self.tavily_api_key.startswith("your_"):
                logger.error("TAVILY_API_KEY is a placeholder")
                self.client = None
            else:
                logger.info(f"TAVILY_API_KEY found (length: {len(self.tavily_api_key)})")
                self.client = TavilyClient(api_key=self.tavily_api_key)
                logger.info("Tavily client initialized successfully")

        except ImportError:
            logger.error("Tavily package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Tavily client: {str(e)}")
            self.client = None
        
        # 3. Initialize LLM (Azure GPT-4o preferred, DeepSeek fallback)
        try:
            from langchain_openai import AzureChatOpenAI, ChatOpenAI
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
                    logger.info(f"Cleaned Azure endpoint to: {azure_endpoint}")
                
                self.llm = AzureChatOpenAI(
                    api_key=gpt_4o_api_key,
                    azure_endpoint=azure_endpoint,
                    api_version="2024-02-01",
                    azure_deployment="gpt-4o",
                    temperature=0.7
                )
                logger.info("Azure GPT-4o initialized for AI-powered content analysis")
            # Fallback to DeepSeek
            elif deepseek_api_key and not deepseek_api_key.startswith("your_"):
                self.llm = ChatOpenAI(
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com",
                    model="deepseek-chat",
                    temperature=0.7
                )
                logger.info("DeepSeek initialized for AI-powered content analysis")
            else:
                logger.error("No AI API configuration found - GPT_4O_API_KEY/AZURE_OPENAI_ENDPOINT or DEEPSEEK_API_KEY required")
                self.llm = None
        except Exception as e:
            logger.error(f"LLM initialization failed: {str(e)}")
            self.llm = None
    
    def research_idea(self, idea: str, title: str) -> Dict[str, Any]:
        """
        Perform market research for an idea with content extraction
        
        Args:
            idea: The idea description
            title: The title of the idea
        
        Returns:
            Dictionary with research findings
        """
        logger.info(f"Research agent called for: {title}")
        
        # Auto-retry initialization if client is missing
        if not self.client:
            logger.warning("Tavily client not ready, attempting re-initialization...")
            self.initialize()
            
        if not self.client:
            logger.error("Tavily client initialization failed after retry")
            return {
                "success": False,
                "title": title,
                "answer": "Tavily API client could not be initialized. Check server logs for API key issues.",
                "market_overview": "",
                "existing_solutions": [],
                "competitors": [],
                "trends": [],
                "opportunities": [],
                "challenges": [],
                "sources": []
            }
        
        try:
            logger.info(f"Starting Tavily search for: {title}")
            
            response = None
            last_error = None
            
            # Retry logic for Tavily API
            for attempt in range(3):
                try:
                    # Search with FULL CONTENT extraction - quality over quantity
                    response = self.client.search(
                        query=f"{title} market analysis competitors solutions trends opportunities challenges",
                        max_results=5,  # Restricted to 5 websites as requested
                        search_depth="advanced",
                        include_answer=True,
                        include_raw_content=True  # CRITICAL: Extract full page content, not just snippets
                    )
                    if response and response.get('results'):
                        break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Tavily search attempt {attempt+1} failed: {str(e)}")
                    import time
                    time.sleep(2)  # Wait before retry
            
            if not response:
                raise Exception(f"Tavily search failed after 3 attempts. Last error: {str(last_error)}")
            
            logger.info(f"Tavily returned {len(response.get('results', []))} results with full content")
            
            # Parse with AI-powered content understanding using FULL page content
            research_findings = self._parse_tavily_with_ai(response, title, idea)
            
            logger.info(f"Research complete: {len(research_findings.get('existing_solutions', []))} solutions, {len(research_findings.get('competitors', []))} competitors")
            
            return research_findings
            
        except Exception as e:
            logger.error(f"Error during research execution: {str(e)}")
            return {
                "success": False,
                "title": title,
                "answer": f"Error during research: {str(e)}",
                "market_overview": "",
                "existing_solutions": [],
                "competitors": [],
                "trends": [],
                "opportunities": [],
                "challenges": [],
                "sources": []
            }
    
    def _parse_tavily_with_ai(self, response: Dict, title: str, idea: str) -> Dict[str, Any]:
        """Parse Tavily response with AI-powered understanding of content"""
        try:
            research_findings = {
                "success": True,
                "title": title,
                "answer": response.get("answer", ""),
                "market_overview": response.get("answer", ""),
                "existing_solutions": [],
                "competitors": [],
                "trends": [],
                "opportunities": [],
                "challenges": [],
                "sources": [],
                "full_content": ""
            }
            
            # Aggregate full content from results for robust extraction
            full_content_parts = []
            
            # Add answer if available
            answer = response.get("answer", "")
            if answer:
                full_content_parts.append(answer)
            
            # Add results content
            for result in response.get("results", []):
                r_title = result.get("title", "") or ""
                r_content = result.get("content", "") or result.get("snippet", "") or ""
                if r_title or r_content:
                    full_content_parts.append(f"Source: {r_title}\n{r_content}\n")
            
            # Filter out None and empty strings before joining
            full_content_parts = [part for part in full_content_parts if part]
            full_content = "\n\n".join(full_content_parts) if full_content_parts else ""
            research_findings["full_content"] = full_content
            
            # Ensure answer/market_overview has content
            if not research_findings["answer"] and full_content:
                research_findings["answer"] = truncate_smart(full_content, 5000)
                research_findings["market_overview"] = research_findings["answer"]
            
            # Extract opportunities and challenges from AI-generated answer
            if response.get("answer") or research_findings["answer"]:
                opportunities = self._extract_opportunities_smart(response.get("answer"), idea)
                challenges = self._extract_challenges_smart(response.get("answer"), idea)
                research_findings["opportunities"] = opportunities
                research_findings["challenges"] = challenges
                logger.info(f"Extracted {len(opportunities)} opportunities and {len(challenges)} challenges from AI answer")
            
            # Process search results - categorize with understanding
            if response.get("results"):
                categorized = self._categorize_results_with_understanding(
                    response.get("results", []),
                    title,
                    idea
                )
                research_findings["existing_solutions"] = categorized.get("solutions", [])
                research_findings["competitors"] = categorized.get("competitors", [])
                research_findings["trends"] = categorized.get("trends", [])
                research_findings["sources"] = categorized.get("all_sources", [])
                
                logger.info(f"Categorized results: {len(categorized.get('solutions', []))} solutions, {len(categorized.get('competitors', []))} competitors, {len(categorized.get('trends', []))} trends")
            
            return research_findings
            
        except Exception as e:
            logger.error(f"Error in AI parsing: {str(e)}")
            return {
                "success": False,
                "title": title,
                "answer": "",
                "market_overview": "",
                "existing_solutions": [],
                "competitors": [],
                "trends": [],
                "challenges": [],
                "sources": []
            }
    
    def _categorize_results_with_understanding(self, results: List[Dict], title: str, idea: str) -> Dict[str, Any]:
        """Categorize results by understanding FULL content using AI - PARALLEL PROCESSING"""
        solutions = []
        competitors = []
        trends = []
        all_sources = []
        
        # Thread-safe locks for lists
        solutions_lock = threading.Lock()
        competitors_lock = threading.Lock()
        trends_lock = threading.Lock()
        sources_lock = threading.Lock()
        
        def process_single_result(result):
            try:
                # Use raw_content if available (full page), otherwise fall back to content/snippet
                raw_content = result.get("raw_content", "")
                content = result.get("content", "")
                snippet = result.get("snippet", "")
                
                # Clean the content first
                raw_content = clean_html_content(raw_content)
                content = clean_html_content(content)
                snippet = clean_html_content(snippet)
                
                # Priority: raw_content > content > snippet
                full_text = raw_content or content or snippet
                
                # Use MAXIMUM content for AI analysis
                full_text_for_analysis = truncate_smart(full_text, 32000)
                
                source = {
                    "title": clean_html_content(result.get("title", "")),
                    "url": result.get("url", ""),
                    "snippet": snippet
                }
                with sources_lock:
                    all_sources.append(source)
                
                # AI ONLY - No keyword fallback
                category = self._classify_with_ai(result, title, idea, full_text_for_analysis)
                
                # Generate comprehensive AI summary
                description = self._summarize_with_ai(
                    clean_html_content(result.get("title", "")), 
                    full_text_for_analysis, 
                    category,
                    idea
                )
                
                # Clean title
                clean_title = clean_html_content(result.get("title", ""))
                
                if category == "solution":
                    with solutions_lock:
                        solutions.append({
                            "title": clean_title,
                            "description": description,
                            "url": result.get("url", ""),
                            "relevance": "Direct solution or tool"
                        })
                elif category == "competitor":
                    with competitors_lock:
                        competitors.append({
                            "title": clean_title,
                            "description": description,
                            "url": result.get("url", ""),
                            "relevance": "Market competitor"
                        })
                else:
                    with trends_lock:
                        trends.append({
                            "trend": clean_title,
                            "description": description,
                            "source": result.get("url", ""),
                            "impact": "Market trend"
                        })
            except Exception as e:
                logger.error(f"Error processing result in parallel: {e}")

        # Use ThreadPoolExecutor for parallel processing with timeout protection
        # Reduce workers to avoid API rate limiting
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Process results with timeout
            future_to_result = {executor.submit(process_single_result, result): result for result in results[:5]}
            
            # Wait for completion with timeout
            for future in concurrent.futures.as_completed(future_to_result, timeout=60):
                try:
                    future.result(timeout=30)  # Individual task timeout
                except concurrent.futures.TimeoutError:
                    logger.warning("Task timed out, skipping...")
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        
        logger.info(f"Categorized results: {len(solutions)} solutions, {len(competitors)} competitors, {len(trends)} trends")
        
        return {
            "solutions": solutions,
            "competitors": competitors,
            "trends": trends,
            "all_sources": all_sources
        }
    
    def _summarize_with_ai(self, title: str, content: str, category: str = "general", idea: str = "") -> str:
        """Use Azure GPT-4o to generate comprehensive summary - NO RESTRICTIONS on what to extract"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            # Define comprehensive prompts that extract EVERYTHING useful
            if category == "competitor":
                template = """Analyze this company/competitor information in detail.
                
Extract ALL useful information including:
- What they do (core business, products, services)
- Financial data (revenue, funding, valuation, growth rates, market cap)
- Market position (market share, ranking, competitive advantages)
- Strategic initiatives (current projects, goals, expansion plans)
- Technology stack (if mentioned)
- Customer base (who uses their products/services)
- Recent news or developments
- ANY other relevant business intelligence

Title: {title}
Content: {content}

Return a comprehensive, detailed summary (NO length restrictions). Include ALL numbers, statistics, and specific details found. Use professional business language."""
                
            elif category == "solution":
                template = """Analyze this solution/product information in detail.

Extract ALL useful information including:
- Who is implementing this (companies, organizations, users)
- Implementation details (how it works, architecture, features)
- Pros and Cons (benefits and drawbacks)
- Cost information (pricing, investment required, ROI data)
- Timeline (implementation time, time to value)
- Success metrics (KPIs, results achieved, case study data)
- Technology details (platforms, integrations, requirements)
- Market adoption (usage statistics, growth trends)
- ANY other relevant implementation intelligence

Title: {title}
Content: {content}
User's Idea Context: {idea}

Return a comprehensive, detailed summary (NO length restrictions). Include ALL numbers, case studies, and specific examples found. Focus on actionable insights."""
                
            elif category == "trend":
                template = """Analyze this market trend/report in detail.

Extract ALL useful information including:
- Key market insights and findings
- Market size data (TAM, SAM, SOM, growth rates)
- Financial statistics (ROI, investment amounts, revenue projections)
- Growth trends (historical and projected)
- Industry forecasts and predictions
- Adoption rates and timelines
- Competitive landscape insights
- Regulatory or technology changes
- ANY other relevant market intelligence

Title: {title}
Content: {content}

Return a comprehensive, detailed summary (NO length restrictions). Include ALL statistics, projections, and data points found. Preserve exact numbers and percentages."""
                
            else:
                template = """Analyze this web content and extract ALL useful business intelligence.

Extract EVERYTHING that could be valuable including:
- Core value proposition and key points
- Financial data (any numbers, statistics, metrics)
- Strategic insights (plans, goals, initiatives)
- Market information (trends, opportunities, challenges)
- Technical details (if relevant)
- Case studies or examples
- Expert opinions or analysis
- ANY other actionable intelligence

Title: {title}
Content: {content}

Return a comprehensive, detailed summary (NO length restrictions). Do NOT filter or limit information. Include ALL relevant details, numbers, and insights."""
            
            prompt = PromptTemplate(
                input_variables=["title", "content", "idea"] if category == "solution" else ["title", "content"],
                template=template
            )
            
            if category == "solution":
                summary = self.llm.invoke(prompt.format(title=title, content=content[:32000], idea=idea)).content
            else:
                summary = self.llm.invoke(prompt.format(title=title, content=content[:32000])).content
            
            return summary.strip()
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            # NO FALLBACK - Return error message
            return f"[AI summarization failed: {str(e)}]"

    def _classify_with_ai(self, result: Dict, title: str, idea: str, content: str = "") -> str:
        """Use Azure GPT-4o to classify result - NO FALLBACK"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            # Use full content (maximum for GPT-4o)
            text_to_analyze = content[:32000] if content else result.get("snippet", "")
            
            prompt = PromptTemplate(
                input_variables=["title", "content", "idea"],
                template="""Classify this search result as: solution, competitor, or trend.
                
- solution: Products, tools, platforms, software, services, implementations, or methods that solve the problem.
- competitor: Companies, vendors, organizations, or entities that offer similar solutions or services.
- trend: Market reports, research, forecasts, industry analysis, general insights, or news.

If it describes a company or product doing something similar to the idea, classify as 'competitor' or 'solution'.
Only use 'trend' if it is purely informational or statistical.

Title: {title}
Content: {content}
Our idea: {idea}

Return ONLY the word: solution, competitor, or trend"""
            )
            
            result_text = self.llm.invoke(prompt.format(title=result.get("title", ""), content=text_to_analyze, idea=idea)).content
            
            category = result_text.strip().lower().split()[0]
            if category in ["solution", "competitor", "trend"]:
                return category
            else:
                # Default to trend if unclear
                return "trend"
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            # Default to trend on error
            return "trend"
    

    
    def _extract_opportunities_smart(self, answer: str, idea: str) -> List[str]:
        """Extract opportunities using Azure GPT-4o - NO RESTRICTIONS, NO FALLBACK"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            prompt = PromptTemplate(
                input_variables=["answer", "idea"],
                template="""From this market research, extract ALL market opportunities relevant to this idea.

Idea: {idea}

Research: {answer}

Extract EVERY opportunity mentioned including:
- Market gaps and unmet needs
- Growth areas and emerging trends
- Expansion possibilities
- Technology opportunities
- Customer segments
- Revenue opportunities
- Strategic advantages
- ANY other opportunities

Return as bullet points. NO LIMIT on number of opportunities. Be comprehensive:"""
            )
            
            result_text = self.llm.invoke(prompt.format(answer=answer[:32000], idea=idea)).content
            
            opportunities = [line.strip().lstrip('-•*').strip() for line in result_text.split("\n") if line.strip() and len(line) > 20]
            logger.info(f"AI extracted {len(opportunities)} opportunities")
            
            return opportunities  # NO LIMIT
        except Exception as e:
            logger.error(f"AI opportunity extraction failed: {str(e)}")
            return []
    
    def _extract_challenges_smart(self, answer: str, idea: str) -> List[str]:
        """Extract challenges using Azure GPT-4o - NO RESTRICTIONS, NO FALLBACK"""
        try:
            from langchain_core.prompts import PromptTemplate
            
            prompt = PromptTemplate(
                input_variables=["answer", "idea"],
                template="""From this market research, extract ALL challenges and risks relevant to this idea.

Idea: {idea}

Research: {answer}

Extract EVERY challenge mentioned including:
- Market barriers and obstacles
- Competitive threats
- Implementation challenges
- Technical difficulties
- Regulatory or compliance issues
- Cost concerns
- Resource constraints
- Risk factors
- ANY other challenges or concerns

Return as bullet points. NO LIMIT on number of challenges. Be comprehensive:"""
            )
            
            result_text = self.llm.invoke(prompt.format(answer=answer[:32000], idea=idea)).content
            
            challenges = [line.strip().lstrip('-•*').strip() for line in result_text.split("\n") if line.strip() and len(line) > 20]
            logger.info(f"AI extracted {len(challenges)} challenges")
            
            return challenges  # NO LIMIT
        except Exception as e:
            logger.error(f"AI challenge extraction failed: {str(e)}")
            return []

# Lazy initialization - create instance only when first accessed
_research_agent_instance = None

def get_research_agent():
    """Get or create the research agent instance (lazy initialization)"""
    global _research_agent_instance
    if _research_agent_instance is None:
        logger.info("Initializing research agent...")
        _research_agent_instance = ResearchAgent()
    return _research_agent_instance

# For backward compatibility, create a property-like access
class ResearchAgentProxy:
    """Proxy to ensure lazy initialization"""
    def __getattr__(self, name):
        # logger.info(f"ResearchAgentProxy: accessing attribute '{name}', triggering initialization if needed")
        return getattr(get_research_agent(), name)

research_agent = ResearchAgentProxy()
