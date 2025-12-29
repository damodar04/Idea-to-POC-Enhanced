"""Workflow Orchestrator - Coordinates company research, idea research, and question generation (ROI removed)"""

import logging
import json
import tempfile
import os

from typing import Dict, List, Optional, Any

from services.company_research_agent import company_research_agent
from services.idea_research_agent import idea_research_agent
from services.resource_estimation_agent import resource_estimation_agent
from services.question_generator import question_generator


logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the complete idea development workflow without ROI analysis."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def start_workflow(self, company_name: str, idea_title: str, idea_description: str, 
                      on_company_complete=None, on_idea_complete=None, on_resource_complete=None) -> Dict:
        """Run the full workflow: company research → idea research → resource estimation → development questions.
        
        Args:
            company_name: Name of the company
            idea_title: Title of the idea
            idea_description: Description of the idea
            on_company_complete: Optional callback function(company_research_data) called after company research completes
            on_idea_complete: Optional callback function(idea_research_data) called after idea research completes
            on_resource_complete: Optional callback function(resource_estimation_data) called after resource estimation completes

        Returns a dictionary containing all results and any errors.
        """
        self.logger.info(f"Starting workflow for: {idea_title} (Company: {company_name})")
        results: Dict[str, Any] = {
            "success": True,
            "company_name": company_name,
            "idea_title": idea_title,
            "company_research": None,
            "idea_research": None,
            "resource_estimation": None,
            "development_questions": [],
            "errors": [],
            "current_step": "completed"
        }

        # Step 1 – Company Research
        try:
            self.logger.info(f"Starting company research for: {company_name}")
            results["current_step"] = "company_research"
            
            company_research = company_research_agent.research_company(company_name)
            if not company_research or not company_research.get("success"):
                error_msg = company_research.get("answer", "Failed to research company.")
                results["errors"].append(f"Company Research Failed: {error_msg}")
                results["success"] = False
                return results
            
            results["company_research"] = company_research
            self.logger.info(f"Company research completed for: {company_name}")
            
            # Call callback to display company research results on UI
            if on_company_complete:
                on_company_complete(company_research)
                
        except Exception as e:
            self.logger.error(f"Error in company research: {str(e)}")
            results["errors"].append(f"Company research error: {str(e)}")
            results["success"] = False
            return results

        # Step 2 – Idea Research
        try:
            self.logger.info(f"Starting idea research for: {idea_title}")
            results["current_step"] = "idea_research"
            
            idea_research = idea_research_agent.research_idea_market(idea_title, idea_description)
            if not idea_research or not idea_research.get("success"):
                error_msg = idea_research.get("answer", "Failed to research idea.")
                results["errors"].append(f"Idea Research Failed: {error_msg}")
                results["success"] = False
                return results
            
            results["idea_research"] = idea_research
            self.logger.info(f"Idea research completed for: {idea_title}")
            
            # Call callback to display idea research results on UI
            if on_idea_complete:
                on_idea_complete(idea_research)
                
        except Exception as e:
            self.logger.error(f"Error in idea research: {str(e)}")
            results["errors"].append(f"Idea research error: {str(e)}")
            results["success"] = False
            return results

        # Step 3 – Resource Estimation
        try:
            self.logger.info(f"Starting resource estimation for: {idea_title}")
            results["current_step"] = "resource_estimation"
            
            resource_estimation = resource_estimation_agent.estimate_resources(
                company_name,
                idea_title,
                idea_description,
                results["company_research"],
                results["idea_research"]
            )
            
            if not resource_estimation or not resource_estimation.get("success"):
                error_msg = resource_estimation.get("error", "Failed to estimate resources.")
                results["errors"].append(f"Resource Estimation Failed: {error_msg}")
                results["success"] = False
                return results
            
            results["resource_estimation"] = resource_estimation
            self.logger.info(f"Resource estimation completed for: {idea_title}")
            
            # Call callback to display resource estimation results on UI
            if on_resource_complete:
                on_resource_complete(resource_estimation)
                
        except Exception as e:
            self.logger.error(f"Error in resource estimation: {str(e)}")
            results["errors"].append(f"Resource estimation error: {str(e)}")
            results["success"] = False
            return results

        # Step 4 – Generate Development Questions (no ROI data)
        try:
            self.logger.info("Generating AI-powered development questions")
            results["current_step"] = "question_generation"
            
            questions = question_generator.generate_questions(
                results["company_research"],
                results["idea_research"],
                company_name,
                idea_title,
                idea_description
            )
            if not questions:
                self.logger.warning("AI failed to generate development questions")
                results["errors"].append("Failed to generate development questions")
                results["success"] = False
                return results
            results["development_questions"] = questions
            self.logger.info(f"AI generated {len(questions)} personalized development questions")
        except Exception as e:
            self.logger.error(f"Error generating questions: {str(e)}")
            results["errors"].append(f"Question generation error: {str(e)}")
            results["success"] = False
            return results

        # Save workflow state for later retrieval
        results["current_step"] = "completed"
        self._save_workflow_state(company_name, idea_title, results)
        self.logger.info("Workflow completed successfully")
        return results

    # Optional helper methods – kept for backward compatibility
    def perform_company_research(self, company_name: str) -> Dict:
        try:
            self.logger.info(f"Starting company research for: {company_name}")
            import concurrent.futures
            # Add timeout protection for company research
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(company_research_agent.research_company, company_name)
                return future.result(timeout=120)  # 2 minute timeout
        except concurrent.futures.TimeoutError:
            self.logger.error(f"Company research timed out for: {company_name}")
            return {"success": False, "error": "Company research timed out after 2 minutes"}
        except Exception as e:
            self.logger.error(f"Error in company research: {str(e)}")
            return {"success": False, "error": str(e)}

    def perform_idea_research(self, idea_title: str, idea_description: str) -> Dict:
        try:
            self.logger.info(f"Starting idea research for: {idea_title}")
            return idea_research_agent.research_idea_market(idea_title, idea_description)
        except Exception as e:
            self.logger.error(f"Error in idea research: {str(e)}")
            return {"success": False, "error": str(e)}

    def perform_resource_estimation(self, company_name: str, idea_title: str, 
                                   idea_description: str, company_research: Dict, 
                                   idea_research: Dict) -> Dict:
        """Perform resource estimation for an idea"""
        try:
            self.logger.info(f"Starting resource estimation for: {idea_title}")
            return resource_estimation_agent.estimate_resources(
                company_name,
                idea_title,
                idea_description,
                company_research,
                idea_research
            )
        except Exception as e:
            self.logger.error(f"Error in resource estimation: {str(e)}")
            return {"success": False, "error": str(e)}

    def generate_development_questions(self, company_research: Dict, idea_research: Dict, 
                                     company_name: str, idea_title: str, idea_description: str) -> List[Dict]:
        """Generate development questions using the question generator"""
        try:
            self.logger.info("Generating development questions")
            questions = question_generator.generate_questions(
                company_research,
                idea_research,
                company_name,
                idea_title,
                idea_description
            )
            return questions
        except Exception as e:
            self.logger.error(f"Error generating development questions: {str(e)}")
            return []

    def _save_workflow_state(self, company_name: str, idea_title: str, results: Dict):
        """Persist workflow results to a temporary JSON file."""
        try:
            temp_dir = tempfile.gettempdir()
            workflow_dir = os.path.join(temp_dir, "i2poc_workflows")
            os.makedirs(workflow_dir, exist_ok=True)
            filename = f"{company_name.replace(' ', '_').lower()}_{idea_title.replace(' ', '_').lower()}_workflow.json"
            filepath = os.path.join(workflow_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Workflow state saved to: {filepath}")
        except Exception as e:
            self.logger.warning(f"Failed to save workflow state: {str(e)}")

    def load_workflow_state(self, company_name: str, idea_title: str) -> Optional[Dict]:
        """Load a previously saved workflow state, if it exists."""
        try:
            temp_dir = tempfile.gettempdir()
            workflow_dir = os.path.join(temp_dir, "i2poc_workflows")
            filename = f"{company_name.replace(' ', '_').lower()}_{idea_title.replace(' ', '_').lower()}_workflow.json"
            filepath = os.path.join(workflow_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.warning(f"Failed to load workflow state: {str(e)}")
            return None


# Global instance for Streamlit imports
workflow_orchestrator = WorkflowOrchestrator()
