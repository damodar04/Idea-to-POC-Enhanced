"""Company Research Agent - Researches target companies for personalized analysis"""

import logging
import json
import tempfile
import os
import re
from typing import Dict, List, Optional
from services.research_agent import research_agent
from services.text_cleaner import clean_html_content, extract_clean_sentences, truncate_smart

logger = logging.getLogger(__name__)

class CompanyResearchAgent:
    """Agent that researches target companies for personalized analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.research_agent = research_agent
    
    def research_company(self, company_name: str) -> Optional[Dict]:
        """
        Research a company to understand their business, financials, and market position
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Dict containing comprehensive company research data
        """
        # Initialize company_data early to avoid "not associated with a value" errors
        # self.logger.info(f"Initializing company_data for {company_name}")
        company_data = {
            "success": False,
            "company_name": company_name,
            "answer": "",
            "what_company_does": "",
            "financials": {},
            "current_initiatives_and_goals": []
        }
        
        try:
            self.logger.info(f"Starting company research for: {company_name}")
            
            # Enhanced research query with specific requirements for completeness
            research_query = f"""
            Research {company_name} company thoroughly and provide comprehensive information:
            
            1. What does the company do (provide complete business description):
               - Core business and main products/services (minimum 3-4 complete sentences)
               - Business model and revenue streams
               - Key value proposition and competitive advantages
               - Industry sector and market position
               - Target customers and geographic reach
            
            2. Financial information (capture complete sentences with context):
               - Annual revenue (latest available with full context)
               - Revenue growth rate and historical trends
               - Market capitalization and stock performance
               - Profitability status and margins
               - Recent financial performance and key metrics
               - Debt levels and financial health indicators
            
            3. Current initiatives and future goals (minimum 3-5 initiatives with details):
               - Current strategic projects and initiatives (provide complete descriptions)
               - Technology investments and digital transformation efforts
               - Market expansion plans and geographic targets
               - Sustainability and ESG initiatives
               - Innovation pipeline and R&D focus areas
               - Future vision and strategic goals for next 3-5 years
            
            IMPORTANT: Provide complete sentences, not just numbers. Ensure no data is truncated.
            Include specific numbers, facts, and high-quality sources. Avoid single-word responses.
            """
            
            # Perform comprehensive company research
            self.logger.info(f"Researching company: {company_name}")
            research_results = self.research_agent.research_idea(research_query, f"Company Research: {company_name}")
            
            if not research_results or not research_results.get('success'):
                self.logger.warning(f"Failed to research company: {company_name}")
                return research_results
            
            # Structure the company research data with AI-powered extraction
            company_data.update({
                "success": True,
                "research_timestamp": research_results.get('timestamp'),
                "what_company_does": self._extract_company_description(research_results, company_name),
                "financials": self._extract_financial_data(research_results, company_name),
                "current_initiatives_and_goals": self._extract_initiatives_and_goals(research_results),
                "sources": self._extract_sources(research_results)
            })
            
            # Save to temporary file for persistence
            self._save_company_research(company_name, company_data)
            
            self.logger.info(f"Company research completed for: {company_name}")
            return company_data
            
        except Exception as e:
            self.logger.error(f"Error in company research: {str(e)}")
            
            # Safety check: ensure company_data exists even if error occurred before initialization
            if 'company_data' not in locals():
                company_data = {
                    "success": False,
                    "company_name": company_name,
                    "answer": "",
                    "what_company_does": "",
                    "financials": {},
                    "current_initiatives_and_goals": []
                }
                
            company_data.update({
                "success": False,
                "answer": f"Error in company research: {str(e)}"
            })
            return company_data
    
    def _extract_company_description(self, research_results: Dict, company_name: str) -> str:
        """Extract what the company does using Azure GPT-4o - comprehensive, no restrictions"""
        
        # Get the full research content - Prefer full_content for maximum context
        content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '') or research_results.get('market_overview', '')
        
        if not content_to_analyze:
            return f"Limited information available about {company_name}."
        
        # Use AI to extract comprehensive business description
        try:
            from langchain_core.prompts import PromptTemplate
            
            # Get LLM from research agent
            llm = self.research_agent.llm
            
            prompt = PromptTemplate(
                input_variables=["company_name", "content"],
                template="""Extract a brief, high-level business summary for {company_name} from this research.

Research Content:
{content}

Extract:
- Core business and main products/services
- Key value proposition

Return a concise summary (max 2 paragraphs). Focus on the most important information."""
            )
            
            description = llm.invoke(prompt.format(company_name=company_name, content=content_to_analyze[:32000])).content
            
            return description.strip()
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for company description: {e}")
            return f"Error extracting company description: {str(e)}"
    
    def _extract_financial_data(self, research_results: Dict, company_name: str) -> Dict:
        """Extract financial data using Azure GPT-4o - comprehensive, no restrictions"""
        
        # Get the full research content - Prefer full_content for maximum context
        content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '') or research_results.get('market_overview', '')
        
        if not content_to_analyze:
            return {
                "annual_revenue": "",
                "revenue_growth": "",
                "market_cap": "",
                "profitability": "",
                "recent_performance": ""
            }
        
        # Use AI to extract ALL financial information
        try:
            from langchain_core.prompts import PromptTemplate
            import json
            
            # Get LLM from research agent
            llm = self.research_agent.llm
            
            prompt = PromptTemplate(
                input_variables=["company_name", "content"],
                template="""Extract key financial highlights for {company_name} from this research.

Research Content:
{content}

Extract ONLY the most recent:
- Annual revenue
- Revenue growth
- Market cap
- Profitability

Return as JSON with these fields:
{{
  "annual_revenue": "Brief revenue data",
  "revenue_growth": "Brief growth data",
  "market_cap": "Brief market cap data",
  "profitability": "Brief profitability data",
  "recent_performance": "Brief summary of recent performance"
}}

Keep text fields brief. If data not found, use empty string."""
            )
            
            result = llm.invoke(prompt.format(company_name=company_name, content=content_to_analyze[:32000])).content
            
            # Parse JSON response using robust parser
            from utils.json_parser import extract_json_from_text
            financials = extract_json_from_text(result, default={
                "annual_revenue": "",
                "revenue_growth": "",
                "market_cap": "",
                "profitability": "",
                "recent_performance": ""
            })
            return financials
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for financial data: {e}")
            return {
                "annual_revenue": "",
                "revenue_growth": "",
                "market_cap": "",
                "profitability": "",
                "recent_performance": f"Error extracting financial data: {str(e)}"
            }
    
    def _extract_initiatives_and_goals(self, research_results: Dict) -> List[str]:
        """Extract current initiatives and future goals using Azure GPT-4o - comprehensive, no restrictions"""
        
        # Get the full research content - Prefer full_content for maximum context
        content_to_analyze = research_results.get('full_content', '') or research_results.get('answer', '') or research_results.get('market_overview', '')
        
        if not content_to_analyze:
            return []
        
        # Use AI to extract ALL initiatives and goals
        try:
            from langchain_core.prompts import PromptTemplate
            
            # Get LLM from research agent
            llm = self.research_agent.llm
            
            prompt = PromptTemplate(
                input_variables=["content"],
                template="""Extract the top 3-5 key initiatives for {company_name} from this research.

Research Content:
{content}

Extract ONLY the most important strategic initiatives.

Return as a list of bullet points. Limit to 3-5 key items. Keep each concise (max 1 sentence)."""
            )
            
            result = llm.invoke(prompt.format(content=content_to_analyze[:32000])).content
            
            # Parse bullet points
            initiatives = [line.strip().lstrip('-•*').strip() for line in result.split("\n") if line.strip() and len(line.strip()) > 30]
            
            self.logger.info(f"AI extracted {len(initiatives)} initiatives and goals")
            return initiatives  # NO LIMIT
            
        except Exception as e:
            self.logger.error(f"AI extraction failed for initiatives: {e}")
            return []
    
    def _extract_sources(self, research_results: Dict) -> List[Dict]:
        """Extract research sources with quality ranking and attribution"""
        sources = []
        seen_urls = set()
        
        # Extract from existing solutions
        existing_solutions = research_results.get('existing_solutions', [])
        for solution in existing_solutions:  # No limit
            url = solution.get('url')
            title = solution.get('title', 'Company Information')
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Company Information",
                    "title": clean_html_content(title)[:150],
                    "url": url,
                    "quality_score": self._calculate_source_quality(url, title),
                    "domain": self._extract_domain(url),
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        # Extract from trends
        trends = research_results.get('trends', [])
        for trend in trends:  # No limit
            url = trend.get('url') or trend.get('source')
            title = trend.get('trend', 'Market Analysis')
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Market Analysis",
                    "title": clean_html_content(title)[:150],
                    "url": url,
                    "quality_score": self._calculate_source_quality(url, title),
                    "domain": self._extract_domain(url),
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        # Extract from main sources list
        main_sources = research_results.get('sources', [])
        for source in main_sources:  # No limit
            url = source.get('url')
            title = source.get('title', source.get('snippet', 'Research Source'))
            if url and url not in ['', 'N/A'] and url not in seen_urls:
                sources.append({
                    "type": "Research Source",
                    "title": clean_html_content(title)[:150],
                    "url": url,
                    "quality_score": self._calculate_source_quality(url, title),
                    "domain": self._extract_domain(url),
                    "date_accessed": research_results.get('timestamp', 'Unknown')
                })
                seen_urls.add(url)
        
        # Sort by quality score and filter low-quality sources
        sources = [s for s in sources if s.get('quality_score', 0) >= 2]  # Filter out very low quality
        sources.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        # Check source diversity
        domains = [s.get('domain', '') for s in sources]
        unique_domains = set(domains)
        if len(unique_domains) < 3:
            self.logger.warning(f"Low source diversity: only {len(unique_domains)} unique domains")
        
        return sources  # No limit
    
    def _calculate_source_quality(self, url: str, title: str) -> int:
        """Calculate source quality score (1-5) based on authority and relevance"""
        score = 3  # Default medium quality
        
        url_lower = url.lower() if url else ''
        title_lower = title.lower() if title else ''
        
        # Authority scoring
        if any(domain in url_lower for domain in ['.gov', '.edu', 'wikipedia.org']):
            score = 5  # Government, education, Wikipedia
        elif any(domain in url_lower for domain in ['forbes.com', 'bloomberg.com', 'reuters.com', 'wsj.com']):
            score = 5  # Major financial news
        elif any(domain in url_lower for domain in ['company.com', 'corporate.', 'official.', 'inc.com']):
            score = 5  # Company official sites
        elif any(domain in url_lower for domain in ['techcrunch.com', 'venturebeat.com', 'businessinsider.com']):
            score = 4  # Tech and business news
        elif any(domain in url_lower for domain in ['medium.com', 'blog.', 'substack.com']):
            score = 2  # Blogs and personal sites
        elif any(domain in url_lower for domain in ['reddit.com', 'forum.', 'quora.com']):
            score = 1  # Forums and social media
        
        # Relevance scoring based on title
        if any(keyword in title_lower for keyword in ['annual report', 'financial statement', 'earnings', 'quarterly']):
            score = min(score + 1, 5)  # Boost for financial documents
        elif any(keyword in title_lower for keyword in ['case study', 'implementation', 'roi', 'return on investment']):
            score = min(score + 1, 5)  # Boost for case studies
        
        # Penalize low-quality indicators
        if any(keyword in title_lower for keyword in ['sponsored', 'advertisement', 'promoted']):
            score = max(score - 2, 1)  # Penalize sponsored content
        
        return score
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for diversity checking"""
        if not url:
            return 'unknown'
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'unknown'
    
    def _save_company_research(self, company_name: str, company_data: Dict):
        """Save company research to temporary file"""
        try:
            temp_dir = tempfile.gettempdir()
            company_dir = os.path.join(temp_dir, "i2poc_company_research")
            os.makedirs(company_dir, exist_ok=True)
            
            filename = f"{company_name.replace(' ', '_').lower()}_research.json"
            filepath = os.path.join(company_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Company research saved to: {filepath}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save company research: {str(e)}")
    
    def load_company_research(self, company_name: str) -> Optional[Dict]:
        """Load company research from temporary file"""
        try:
            temp_dir = tempfile.gettempdir()
            company_dir = os.path.join(temp_dir, "i2poc_company_research")
            filename = f"{company_name.replace(' ', '_').lower()}_research.json"
            filepath = os.path.join(company_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to load company research: {str(e)}")
            return None


# Lazy initialization - create instance only when first accessed
_company_research_agent_instance = None

def get_company_research_agent():
    """Get or create the company research agent instance (lazy initialization)"""
    global _company_research_agent_instance
    if _company_research_agent_instance is None:
        logger.info("Initializing company research agent...")
        _company_research_agent_instance = CompanyResearchAgent()
    return _company_research_agent_instance

# For backward compatibility
class CompanyResearchAgentProxy:
    """Proxy to ensure lazy initialization"""
    def __getattr__(self, name):
        return getattr(get_company_research_agent(), name)

company_research_agent = CompanyResearchAgentProxy()
