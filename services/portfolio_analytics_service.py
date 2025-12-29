"""Portfolio Analytics Service - Provides analytics for Innovation Portfolio Dashboard"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


class PortfolioAnalyticsService:
    """Service for generating portfolio-level analytics and insights"""
    
    def __init__(self):
        self.risk_thresholds = {
            "low": (0, 33),
            "medium": (34, 66),
            "high": (67, 100)
        }
        self.impact_thresholds = {
            "low": (0, 40),
            "medium": (41, 70),
            "high": (71, 100)
        }
    
    def analyze_portfolio(self, ideas: List[Any]) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis
        
        Args:
            ideas: List of IdeaDocument objects
            
        Returns:
            Dictionary containing all portfolio analytics
        """
        if not ideas:
            return self._empty_portfolio_result()
        
        return {
            "summary": self._generate_summary(ideas),
            "clusters": self._cluster_ideas(ideas),
            "department_heatmap": self._generate_department_heatmap(ideas),
            "budget_roi_projections": self._calculate_budget_roi(ideas),
            "risk_distribution": self._analyze_risk_distribution(ideas),
            "timeline_analysis": self._analyze_timeline(ideas),
            "recommendations": self._generate_recommendations(ideas)
        }
    
    def _empty_portfolio_result(self) -> Dict[str, Any]:
        """Return empty portfolio result structure"""
        return {
            "summary": {
                "total_ideas": 0,
                "total_departments": 0,
                "avg_score": 0,
                "approval_rate": 0,
                "estimated_total_value": 0
            },
            "clusters": [],
            "department_heatmap": {},
            "budget_roi_projections": [],
            "risk_distribution": {"low": 0, "medium": 0, "high": 0},
            "timeline_analysis": {},
            "recommendations": []
        }
    
    def _generate_summary(self, ideas: List[Any]) -> Dict[str, Any]:
        """Generate portfolio summary statistics"""
        total_ideas = len(ideas)
        
        # Get unique departments
        departments = set()
        for idea in ideas:
            if hasattr(idea, 'metadata') and idea.metadata:
                dept = getattr(idea.metadata, 'department', 'General')
                departments.add(dept)
        
        # Calculate average score
        scores = [idea.ai_score for idea in ideas if idea.ai_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate approval rate
        approved = len([i for i in ideas if getattr(i, 'status', '') == 'approved'])
        total_reviewed = len([i for i in ideas if getattr(i, 'status', '') in ['approved', 'rejected']])
        approval_rate = (approved / total_reviewed * 100) if total_reviewed > 0 else 0
        
        # Estimate total portfolio value (based on scores and research data)
        estimated_value = self._estimate_portfolio_value(ideas)
        
        return {
            "total_ideas": total_ideas,
            "total_departments": len(departments),
            "departments_list": list(departments),
            "avg_score": round(avg_score, 1),
            "approval_rate": round(approval_rate, 1),
            "estimated_total_value": estimated_value,
            "ideas_by_status": self._count_by_status(ideas),
            "high_potential_count": len([i for i in ideas if (i.ai_score or 0) >= 75])
        }
    
    def _cluster_ideas(self, ideas: List[Any]) -> List[Dict[str, Any]]:
        """
        Cluster ideas by domain, impact, and risk
        
        Returns clusters with:
        - Domain clusters (by department/category)
        - Impact clusters (high/medium/low impact)
        - Risk clusters (high/medium/low risk)
        """
        clusters = []
        
        # Domain clusters (by department)
        domain_clusters = defaultdict(list)
        for idea in ideas:
            dept = "General"
            if hasattr(idea, 'metadata') and idea.metadata:
                dept = getattr(idea.metadata, 'department', 'General')
            domain_clusters[dept].append(idea)
        
        for domain, domain_ideas in domain_clusters.items():
            avg_score = sum([i.ai_score or 0 for i in domain_ideas]) / len(domain_ideas) if domain_ideas else 0
            clusters.append({
                "cluster_type": "domain",
                "name": domain,
                "idea_count": len(domain_ideas),
                "avg_score": round(avg_score, 1),
                "ideas": [{"title": i.title, "score": i.ai_score, "status": getattr(i, 'status', 'submitted')} for i in domain_ideas],
                "health_indicator": self._get_health_indicator(avg_score)
            })
        
        # Impact clusters
        impact_groups = {"High Impact": [], "Medium Impact": [], "Low Impact": []}
        for idea in ideas:
            score = idea.ai_score or 0
            if score >= 70:
                impact_groups["High Impact"].append(idea)
            elif score >= 40:
                impact_groups["Medium Impact"].append(idea)
            else:
                impact_groups["Low Impact"].append(idea)
        
        for impact_level, impact_ideas in impact_groups.items():
            if impact_ideas:
                clusters.append({
                    "cluster_type": "impact",
                    "name": impact_level,
                    "idea_count": len(impact_ideas),
                    "avg_score": round(sum([i.ai_score or 0 for i in impact_ideas]) / len(impact_ideas), 1),
                    "ideas": [{"title": i.title, "score": i.ai_score, "status": getattr(i, 'status', 'submitted')} for i in impact_ideas],
                    "color": {"High Impact": "#28a745", "Medium Impact": "#ffc107", "Low Impact": "#dc3545"}.get(impact_level, "#6c757d")
                })
        
        # Risk clusters (inverse of feasibility/clarity scores)
        risk_groups = {"Low Risk": [], "Medium Risk": [], "High Risk": []}
        for idea in ideas:
            # Estimate risk based on score and available data
            risk_score = self._calculate_risk_score(idea)
            if risk_score <= 33:
                risk_groups["Low Risk"].append(idea)
            elif risk_score <= 66:
                risk_groups["Medium Risk"].append(idea)
            else:
                risk_groups["High Risk"].append(idea)
        
        for risk_level, risk_ideas in risk_groups.items():
            if risk_ideas:
                clusters.append({
                    "cluster_type": "risk",
                    "name": risk_level,
                    "idea_count": len(risk_ideas),
                    "avg_score": round(sum([i.ai_score or 0 for i in risk_ideas]) / len(risk_ideas), 1) if risk_ideas else 0,
                    "ideas": [{"title": i.title, "score": i.ai_score, "status": getattr(i, 'status', 'submitted')} for i in risk_ideas],
                    "color": {"Low Risk": "#28a745", "Medium Risk": "#ffc107", "High Risk": "#dc3545"}.get(risk_level, "#6c757d")
                })
        
        return clusters
    
    def _generate_department_heatmap(self, ideas: List[Any]) -> Dict[str, Dict[str, Any]]:
        """
        Generate department-wise innovation heatmap
        
        Returns dictionary with department data including:
        - Idea count
        - Average score
        - Innovation index
        - Trend
        """
        department_data = defaultdict(lambda: {
            "idea_count": 0,
            "total_score": 0,
            "approved_count": 0,
            "rejected_count": 0,
            "in_progress_count": 0,
            "ideas": []
        })
        
        for idea in ideas:
            dept = "General"
            if hasattr(idea, 'metadata') and idea.metadata:
                dept = getattr(idea.metadata, 'department', 'General')
            
            department_data[dept]["idea_count"] += 1
            department_data[dept]["total_score"] += (idea.ai_score or 0)
            department_data[dept]["ideas"].append(idea.title)
            
            status = getattr(idea, 'status', 'submitted')
            if status == 'approved':
                department_data[dept]["approved_count"] += 1
            elif status == 'rejected':
                department_data[dept]["rejected_count"] += 1
            elif status in ['in_progress', 'under_review']:
                department_data[dept]["in_progress_count"] += 1
        
        # Calculate metrics for each department
        heatmap = {}
        for dept, data in department_data.items():
            count = data["idea_count"]
            avg_score = data["total_score"] / count if count > 0 else 0
            
            # Calculate innovation index (weighted combination of quantity and quality)
            innovation_index = (count * 10 + avg_score) / 2
            
            # Determine heat level
            if innovation_index >= 60:
                heat_level = "hot"
                heat_color = "#dc3545"  # Red/hot
            elif innovation_index >= 30:
                heat_level = "warm"
                heat_color = "#ffc107"  # Yellow/warm
            else:
                heat_level = "cool"
                heat_color = "#17a2b8"  # Blue/cool
            
            heatmap[dept] = {
                "idea_count": count,
                "avg_score": round(avg_score, 1),
                "approved_count": data["approved_count"],
                "rejected_count": data["rejected_count"],
                "in_progress_count": data["in_progress_count"],
                "innovation_index": round(innovation_index, 1),
                "heat_level": heat_level,
                "heat_color": heat_color,
                "success_rate": round((data["approved_count"] / count * 100) if count > 0 else 0, 1),
                "top_ideas": data["ideas"][:5]  # Top 5 idea titles
            }
        
        return heatmap
    
    def _calculate_budget_roi(self, ideas: List[Any]) -> List[Dict[str, Any]]:
        """
        Calculate budget vs ROI projections for ideas using actual research data.
        
        Returns list of projections with:
        - Detailed budget breakdown (team, infrastructure, tools)
        - Projected ROI with value drivers
        - Confidence level with reasoning
        - Timeline with phases
        """
        projections = []
        
        for idea in ideas:
            # Skip rejected ideas
            if getattr(idea, 'status', '') == 'rejected':
                continue
            
            score = idea.ai_score or 50
            
            # Get detailed budget breakdown from actual research data
            budget_data = self._estimate_budget(idea)
            
            # Calculate projected ROI based on market research
            roi_data = self._project_roi(idea, score, budget_data)
            
            # Calculate confidence with detailed reasoning
            confidence_data = self._calculate_projection_confidence(idea)
            
            # Get timeline from actual research data
            timeline_data = self._estimate_timeline(idea, score)
            
            projections.append({
                "idea_id": idea.session_id,
                "title": idea.title,
                "department": getattr(idea.metadata, 'department', 'General') if idea.metadata else 'General',
                "score": score,
                "status": getattr(idea, 'status', 'submitted'),
                
                # Budget details
                "budget_estimate": budget_data.get("total", 0),
                "budget_breakdown": {
                    "team_costs": budget_data.get("team_costs", 0),
                    "infrastructure_costs": budget_data.get("infrastructure_costs", 0),
                    "tools_costs": budget_data.get("tools_costs", 0),
                    "contingency": budget_data.get("contingency", 0),
                    "team_details": budget_data.get("details", {}).get("team_breakdown", []),
                    "infrastructure_details": budget_data.get("details", {}).get("infrastructure_items", [])
                },
                "has_budget_data": budget_data.get("has_real_data", False),
                
                # ROI details
                "roi_projection": roi_data.get("projected_value", 0),
                "roi_percentage": roi_data.get("roi_percentage", 0),
                "net_value": roi_data.get("net_value", 0),
                "value_drivers": roi_data.get("value_drivers", []),
                "payback_months": roi_data.get("payback_months", 12),
                "has_roi_data": roi_data.get("has_real_data", False),
                "industry_comparison": roi_data.get("industry_comparison", {}),
                "differentiators": roi_data.get("differentiators", []),
                
                # Confidence details
                "confidence": confidence_data.get("level", "low"),
                "confidence_score": confidence_data.get("score", 0),
                "confidence_factors": confidence_data.get("factors", []),
                "missing_data": confidence_data.get("missing_data", []),
                
                # Timeline details
                "timeline_months": timeline_data.get("total_months", 6),
                "timeline_phases": timeline_data.get("phases", []),
                "has_timeline_data": timeline_data.get("has_real_data", False),
                
                # Risk level
                "risk_level": self._get_risk_level(idea)
            })
        
        # Sort by net value (highest potential first)
        projections.sort(key=lambda x: x["net_value"], reverse=True)
        
        return projections
    
    def _analyze_risk_distribution(self, ideas: List[Any]) -> Dict[str, int]:
        """Analyze risk distribution across portfolio"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for idea in ideas:
            risk_score = self._calculate_risk_score(idea)
            if risk_score <= 33:
                distribution["low"] += 1
            elif risk_score <= 66:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution
    
    def _analyze_timeline(self, ideas: List[Any]) -> Dict[str, Any]:
        """Analyze submission and approval timelines"""
        now = datetime.utcnow()
        
        # Group by month
        monthly_submissions = defaultdict(int)
        monthly_approvals = defaultdict(int)
        
        for idea in ideas:
            if hasattr(idea, 'metadata') and idea.metadata:
                created_at = getattr(idea.metadata, 'created_at', None)
                if created_at:
                    month_key = created_at.strftime("%Y-%m")
                    monthly_submissions[month_key] += 1
                    
                    if getattr(idea, 'status', '') == 'approved':
                        monthly_approvals[month_key] += 1
        
        # Calculate trends
        months = sorted(monthly_submissions.keys())[-6:]  # Last 6 months
        
        return {
            "monthly_submissions": {m: monthly_submissions.get(m, 0) for m in months},
            "monthly_approvals": {m: monthly_approvals.get(m, 0) for m in months},
            "trend": self._calculate_trend(monthly_submissions, months),
            "avg_time_to_approval_days": self._estimate_avg_approval_time(ideas)
        }
    
    def _generate_recommendations(self, ideas: List[Any]) -> List[Dict[str, Any]]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        if not ideas:
            recommendations.append({
                "type": "action",
                "priority": "high",
                "title": "Start Innovation Program",
                "description": "No ideas submitted yet. Consider launching an innovation campaign to encourage submissions.",
                "icon": "🚀"
            })
            return recommendations
        
        # Analyze portfolio health
        avg_score = sum([i.ai_score or 0 for i in ideas]) / len(ideas)
        high_potential = len([i for i in ideas if (i.ai_score or 0) >= 75])
        pending = len([i for i in ideas if getattr(i, 'status', '') == 'submitted'])
        
        # High potential ideas recommendation
        if high_potential >= 3:
            recommendations.append({
                "type": "opportunity",
                "priority": "high",
                "title": f"{high_potential} High-Potential Ideas Identified",
                "description": "Consider fast-tracking these ideas for POC development.",
                "icon": "⭐"
            })
        
        # Pending review backlog
        if pending >= 5:
            recommendations.append({
                "type": "warning",
                "priority": "medium",
                "title": f"{pending} Ideas Awaiting Review",
                "description": "Review backlog detected. Consider allocating more reviewer resources.",
                "icon": "⏳"
            })
        
        # Department diversity
        departments = set()
        for idea in ideas:
            if hasattr(idea, 'metadata') and idea.metadata:
                departments.add(getattr(idea.metadata, 'department', 'General'))
        
        if len(departments) < 3:
            recommendations.append({
                "type": "insight",
                "priority": "low",
                "title": "Limited Department Diversity",
                "description": f"Only {len(departments)} departments are contributing. Consider cross-departmental innovation workshops.",
                "icon": "🔄"
            })
        
        # Quality improvement
        if avg_score < 50:
            recommendations.append({
                "type": "action",
                "priority": "medium",
                "title": "Quality Improvement Needed",
                "description": "Average idea score is below 50. Consider providing idea development training.",
                "icon": "📈"
            })
        
        return recommendations
    
    # Helper methods
    def _count_by_status(self, ideas: List[Any]) -> Dict[str, int]:
        """Count ideas by status"""
        counts = defaultdict(int)
        for idea in ideas:
            status = getattr(idea, 'status', 'submitted')
            if hasattr(status, 'value'):
                status = status.value
            counts[status] += 1
        return dict(counts)
    
    def _calculate_risk_score(self, idea: Any) -> int:
        """Calculate risk score for an idea (0-100, higher = riskier)"""
        base_risk = 50
        
        # Lower risk if high score
        if idea.ai_score:
            base_risk -= (idea.ai_score - 50) * 0.5
        
        # Higher risk if no research data
        if not idea.research_data:
            base_risk += 15
        
        # Lower risk if approved
        if getattr(idea, 'status', '') == 'approved':
            base_risk -= 10
        
        return max(0, min(100, int(base_risk)))
    
    def _estimate_portfolio_value(self, ideas: List[Any]) -> float:
        """Estimate total portfolio value"""
        total_value = 0
        for idea in ideas:
            score = idea.ai_score or 50
            # Base value estimation (simplified)
            base_value = score * 1000  # $1000 per score point
            
            # Boost for approved ideas
            if getattr(idea, 'status', '') == 'approved':
                base_value *= 1.5
            
            total_value += base_value
        
        return round(total_value, 2)
    
    def _estimate_budget(self, idea: Any) -> Dict[str, Any]:
        """
        Estimate budget for an idea based on actual resource estimation data.
        Returns detailed budget breakdown with team costs, infrastructure, and tools.
        """
        budget_breakdown = {
            "total": 0,
            "team_costs": 0,
            "infrastructure_costs": 0,
            "tools_costs": 0,
            "contingency": 0,
            "details": {
                "team_breakdown": [],
                "infrastructure_items": [],
                "tools_items": []
            },
            "has_real_data": False
        }
        
        # Average monthly rates by role (industry standards)
        role_rates = {
            "developer": 8000,
            "senior developer": 12000,
            "full-stack": 10000,
            "frontend": 8500,
            "backend": 9000,
            "architect": 15000,
            "tech lead": 14000,
            "project manager": 9000,
            "product manager": 10000,
            "designer": 7500,
            "ux": 8000,
            "ui": 7000,
            "qa": 6500,
            "tester": 6000,
            "devops": 11000,
            "data scientist": 13000,
            "ml engineer": 14000,
            "ai": 14000,
            "analyst": 7000,
            "consultant": 12000,
            "default": 8000
        }
        
        # Infrastructure cost estimates (monthly)
        infra_costs = {
            "aws": 500,
            "azure": 500,
            "gcp": 500,
            "cloud": 400,
            "ec2": 150,
            "s3": 50,
            "rds": 200,
            "lambda": 100,
            "kubernetes": 300,
            "docker": 50,
            "database": 150,
            "postgresql": 100,
            "mongodb": 120,
            "redis": 80,
            "elasticsearch": 200,
            "cdn": 100,
            "ssl": 20,
            "domain": 15,
            "monitoring": 100,
            "logging": 80,
            "default": 100
        }
        
        # Tool costs (monthly per user)
        tool_costs = {
            "jira": 10,
            "confluence": 5,
            "slack": 8,
            "github": 20,
            "gitlab": 19,
            "bitbucket": 15,
            "figma": 15,
            "vs code": 0,
            "intellij": 50,
            "postman": 12,
            "datadog": 30,
            "newrelic": 25,
            "sentry": 26,
            "default": 15
        }
        
        # Check if we have actual resource estimation data
        if idea.research_data and idea.research_data.get('resource_estimation'):
            res_est = idea.research_data['resource_estimation']
            budget_breakdown["has_real_data"] = True
            
            # Calculate team costs from actual data
            team_resources = res_est.get('team_resources', [])
            timeline_data = res_est.get('timeline', [])
            
            # Calculate total project duration in months
            total_months = self._parse_timeline_duration(timeline_data)
            
            for resource in team_resources:
                if isinstance(resource, dict):
                    role = resource.get('role', 'Developer').lower()
                    
                    # Parse number of people
                    num_people = self._parse_number_of_people(resource.get('number_of_people', '1'))
                    
                    # Parse allocation (percentage of time)
                    allocation = self._parse_allocation(resource.get('allocation', 'full-time'))
                    
                    # Find matching rate
                    rate = role_rates.get("default")
                    for role_key, role_rate in role_rates.items():
                        if role_key in role.lower():
                            rate = role_rate
                            break
                    
                    # Calculate cost
                    months = allocation.get('months', total_months)
                    percentage = allocation.get('percentage', 100) / 100
                    cost = rate * num_people * months * percentage
                    
                    budget_breakdown["team_costs"] += cost
                    budget_breakdown["details"]["team_breakdown"].append({
                        "role": resource.get('role', 'Developer'),
                        "count": num_people,
                        "rate_per_month": rate,
                        "duration_months": months,
                        "allocation_pct": allocation.get('percentage', 100),
                        "total_cost": round(cost, 2)
                    })
            
            # Calculate infrastructure costs
            infra_items = res_est.get('technical_infrastructure', [])
            for item in infra_items:
                if isinstance(item, str):
                    item_lower = item.lower()
                    monthly_cost = infra_costs.get("default")
                    matched_service = "Other"
                    
                    for service, cost in infra_costs.items():
                        if service in item_lower:
                            monthly_cost = cost
                            matched_service = service.upper()
                            break
                    
                    total_infra_cost = monthly_cost * total_months
                    budget_breakdown["infrastructure_costs"] += total_infra_cost
                    budget_breakdown["details"]["infrastructure_items"].append({
                        "item": item,
                        "service_type": matched_service,
                        "monthly_cost": monthly_cost,
                        "total_cost": round(total_infra_cost, 2)
                    })
            
            # Tool costs (estimate based on team size)
            total_team_size = sum([self._parse_number_of_people(r.get('number_of_people', '1')) 
                                   for r in team_resources if isinstance(r, dict)])
            estimated_tool_cost = total_team_size * 50 * total_months  # ~$50/person/month for tools
            budget_breakdown["tools_costs"] = estimated_tool_cost
            
        else:
            # Fallback estimation when no research data available
            score = idea.ai_score or 50
            
            # Base costs on idea complexity (score indicates complexity)
            if score >= 70:
                # Complex project: 4-6 developers for 6 months
                base_team = 5 * 9000 * 6  # 5 devs avg $9k/mo for 6 months
                base_infra = 800 * 6
                base_tools = 5 * 50 * 6
            elif score >= 40:
                # Medium project: 2-3 developers for 4 months
                base_team = 3 * 8500 * 4
                base_infra = 400 * 4
                base_tools = 3 * 50 * 4
            else:
                # Simple project: 1-2 developers for 3 months
                base_team = 2 * 8000 * 3
                base_infra = 200 * 3
                base_tools = 2 * 50 * 3
            
            budget_breakdown["team_costs"] = base_team
            budget_breakdown["infrastructure_costs"] = base_infra
            budget_breakdown["tools_costs"] = base_tools
        
        # Add 15% contingency
        subtotal = (budget_breakdown["team_costs"] + 
                   budget_breakdown["infrastructure_costs"] + 
                   budget_breakdown["tools_costs"])
        budget_breakdown["contingency"] = subtotal * 0.15
        budget_breakdown["total"] = round(subtotal + budget_breakdown["contingency"], 2)
        
        return budget_breakdown
    
    def _parse_number_of_people(self, text: str) -> int:
        """Extract number of people from text like '2 developers' or '1-2'"""
        if isinstance(text, int):
            return text
        if not isinstance(text, str):
            return 1
        
        import re
        # Look for patterns like "2", "2-3", "2 developers"
        numbers = re.findall(r'\d+', text)
        if numbers:
            # If range like "2-3", take average
            if len(numbers) >= 2:
                return (int(numbers[0]) + int(numbers[1])) // 2
            return int(numbers[0])
        return 1
    
    def _parse_allocation(self, text: str) -> Dict[str, Any]:
        """Parse allocation text like 'Full-time for 8 months' or '50% for 3 months'"""
        result = {"percentage": 100, "months": None}
        
        if not isinstance(text, str):
            return result
        
        text_lower = text.lower()
        
        import re
        
        # Check for percentage
        if "part-time" in text_lower or "part time" in text_lower:
            result["percentage"] = 50
        elif "half" in text_lower:
            result["percentage"] = 50
        
        # Look for explicit percentage
        pct_match = re.search(r'(\d+)\s*%', text_lower)
        if pct_match:
            result["percentage"] = int(pct_match.group(1))
        
        # Look for duration in months
        month_match = re.search(r'(\d+)\s*month', text_lower)
        if month_match:
            result["months"] = int(month_match.group(1))
        
        # Look for duration in weeks (convert to months)
        week_match = re.search(r'(\d+)\s*week', text_lower)
        if week_match and not result["months"]:
            result["months"] = max(1, int(week_match.group(1)) // 4)
        
        return result
    
    def _parse_timeline_duration(self, timeline: List[Dict]) -> int:
        """Calculate total project duration from timeline phases"""
        total_weeks = 0
        
        for phase in timeline:
            if isinstance(phase, dict):
                duration = phase.get('duration', '')
                if isinstance(duration, str):
                    import re
                    # Look for weeks
                    week_match = re.search(r'(\d+)\s*week', duration.lower())
                    if week_match:
                        total_weeks += int(week_match.group(1))
                        continue
                    
                    # Look for months
                    month_match = re.search(r'(\d+)\s*month', duration.lower())
                    if month_match:
                        total_weeks += int(month_match.group(1)) * 4
        
        # Convert to months, minimum 3 months
        return max(3, total_weeks // 4) if total_weeks > 0 else 6
    
    def _project_roi(self, idea: Any, score: int, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Project ROI based on idea research data, industry benchmarks, and market analysis.
        Uses actual data from idea_research when available with industry-specific ROI ranges.
        """
        budget = budget_data.get("total", 50000) if isinstance(budget_data, dict) else budget_data
        
        # Industry benchmark ROI ranges (based on POC/Innovation project data)
        industry_roi_benchmarks = {
            "healthcare": {"min": 120, "max": 350, "avg": 180, "typical_payback": 18},
            "clinical_trial": {"min": 150, "max": 400, "avg": 220, "typical_payback": 15},
            "ai_ml": {"min": 100, "max": 500, "avg": 200, "typical_payback": 12},
            "automation": {"min": 80, "max": 250, "avg": 150, "typical_payback": 10},
            "fintech": {"min": 130, "max": 380, "avg": 190, "typical_payback": 14},
            "saas": {"min": 90, "max": 300, "avg": 160, "typical_payback": 16},
            "manufacturing": {"min": 60, "max": 180, "avg": 110, "typical_payback": 20},
            "logistics": {"min": 70, "max": 200, "avg": 120, "typical_payback": 18},
            "retail": {"min": 50, "max": 150, "avg": 90, "typical_payback": 22},
            "general": {"min": 40, "max": 200, "avg": 100, "typical_payback": 18}
        }
        
        roi_projection = {
            "projected_value": 0,
            "roi_percentage": 0,
            "net_value": 0,
            "payback_months": 12,
            "value_drivers": [],
            "has_real_data": False,
            "industry_comparison": {},
            "differentiators": []
        }
        
        # Detect industry from idea content
        industry = self._detect_industry(idea)
        benchmarks = industry_roi_benchmarks.get(industry, industry_roi_benchmarks["general"])
        
        # Store industry comparison data
        roi_projection["industry_comparison"] = {
            "industry": industry.replace("_", " ").title(),
            "industry_avg_roi": benchmarks["avg"],
            "industry_roi_range": f"{benchmarks['min']}% - {benchmarks['max']}%",
            "typical_payback_months": benchmarks["typical_payback"]
        }
        
        # Check for actual market/implementation data
        if idea.research_data and idea.research_data.get('idea_research'):
            idea_research = idea.research_data['idea_research']
            roi_projection["has_real_data"] = True
            
            # Look for implementation metrics
            metrics = idea_research.get('implementation_metrics', {})
            insights = idea_research.get('useful_insights', [])
            pros = idea_research.get('pros_and_cons', {}).get('pros', [])
            cons = idea_research.get('pros_and_cons', {}).get('cons', [])
            
            # Base ROI calculation on multiple factors
            implementing_count = len(idea_research.get('who_is_implementing', []))
            
            # Start with industry baseline and adjust
            base_roi_pct = benchmarks["avg"]
            roi_adjustment = 0
            
            # Factor 1: Market validation (implementing companies)
            if implementing_count >= 5:
                roi_adjustment += 40
                roi_projection["value_drivers"].append(f"{implementing_count}+ companies already implementing - validated market")
                roi_projection["differentiators"].append("Higher than avg: Strong market validation")
            elif implementing_count >= 2:
                roi_adjustment += 20
                roi_projection["value_drivers"].append(f"{implementing_count} companies have validated this approach")
            else:
                roi_adjustment -= 10
                roi_projection["value_drivers"].append("Early-stage market opportunity - higher risk/reward")
            
            # Factor 2: Idea score impact
            if score >= 80:
                roi_adjustment += 35
                roi_projection["differentiators"].append("Higher than avg: Exceptional idea score (80+)")
            elif score >= 70:
                roi_adjustment += 20
                roi_projection["differentiators"].append("Higher than avg: Strong idea score (70+)")
            elif score >= 50:
                roi_adjustment += 5
            else:
                roi_adjustment -= 20
            
            # Factor 3: Number of pros vs cons
            if len(pros) > len(cons) + 2:
                roi_adjustment += 15
                roi_projection["differentiators"].append("Higher than avg: Strong benefit profile")
            elif len(cons) > len(pros):
                roi_adjustment -= 15
            
            # Factor 4: Extract efficiency/cost savings from insights
            for insight in insights[:5]:
                if isinstance(insight, str):
                    insight_lower = insight.lower()
                    # Look for quantified benefits
                    import re
                    pct_match = re.search(r'(\d+)\s*%', insight_lower)
                    if pct_match:
                        mentioned_pct = int(pct_match.group(1))
                        if any(kw in insight_lower for kw in ['reduction', 'save', 'faster', 'efficiency', 'improve']):
                            if mentioned_pct >= 50:
                                roi_adjustment += 25
                            elif mentioned_pct >= 30:
                                roi_adjustment += 15
                            elif mentioned_pct >= 10:
                                roi_adjustment += 8
            
            # Calculate final ROI percentage
            final_roi_pct = max(benchmarks["min"], min(benchmarks["max"], base_roi_pct + roi_adjustment))
            
            # Add value drivers from pros
            for pro in pros[:3]:
                if isinstance(pro, str) and len(pro) > 10:
                    roi_projection["value_drivers"].append(pro)
            
            # Calculate projected value
            roi_projection["roi_percentage"] = round(final_roi_pct, 1)
            roi_projection["projected_value"] = round(budget * (1 + final_roi_pct / 100), 2)
            
            # Compare to industry average
            if final_roi_pct > benchmarks["avg"] * 1.2:
                roi_projection["industry_comparison"]["vs_industry"] = "above_average"
                roi_projection["industry_comparison"]["vs_industry_label"] = f"+{round(final_roi_pct - benchmarks['avg'])}% above industry avg"
            elif final_roi_pct < benchmarks["avg"] * 0.8:
                roi_projection["industry_comparison"]["vs_industry"] = "below_average"
                roi_projection["industry_comparison"]["vs_industry_label"] = f"{round(benchmarks['avg'] - final_roi_pct)}% below industry avg"
            else:
                roi_projection["industry_comparison"]["vs_industry"] = "on_par"
                roi_projection["industry_comparison"]["vs_industry_label"] = "On par with industry average"
            
        else:
            # Fallback calculation based on score with industry context
            base_roi_pct = benchmarks["avg"]
            
            if score >= 75:
                roi_pct = base_roi_pct + 50
                roi_projection["value_drivers"].append("High-scoring idea with strong potential")
            elif score >= 50:
                roi_pct = base_roi_pct
                roi_projection["value_drivers"].append("Moderate potential based on AI assessment")
            else:
                roi_pct = max(20, base_roi_pct - 30)
                roi_projection["value_drivers"].append("Conservative estimate - needs more validation")
            
            roi_projection["roi_percentage"] = round(roi_pct, 1)
            roi_projection["projected_value"] = round(budget * (1 + roi_pct / 100), 2)
            roi_projection["industry_comparison"]["vs_industry"] = "estimated"
            roi_projection["industry_comparison"]["vs_industry_label"] = "Based on AI score (no research data)"
        
        # Calculate derived metrics
        roi_projection["net_value"] = round(roi_projection["projected_value"] - budget, 2)
        
        # Estimate payback period based on industry benchmarks
        if roi_projection["net_value"] > 0:
            # Use industry typical payback as baseline, adjust based on ROI
            base_payback = benchmarks["typical_payback"]
            if roi_projection["roi_percentage"] > benchmarks["avg"] * 1.3:
                payback = max(3, base_payback - 4)
            elif roi_projection["roi_percentage"] > benchmarks["avg"]:
                payback = base_payback - 2
            else:
                payback = base_payback + 2
            roi_projection["payback_months"] = max(3, min(36, payback))
        else:
            roi_projection["payback_months"] = benchmarks["typical_payback"]
        
        return roi_projection
    
    def _detect_industry(self, idea: Any) -> str:
        """Detect industry/domain from idea content for benchmark selection"""
        keywords_map = {
            "clinical_trial": ["clinical trial", "patient matching", "trial protocol", "eligibility", "patient screening", "medical trial"],
            "healthcare": ["healthcare", "medical", "hospital", "patient", "health", "diagnosis", "treatment"],
            "ai_ml": ["artificial intelligence", "machine learning", "ai", "ml", "deep learning", "neural network", "nlp", "computer vision"],
            "automation": ["automation", "automate", "workflow", "rpa", "robotic process", "automated"],
            "fintech": ["fintech", "finance", "banking", "payment", "trading", "investment", "insurance"],
            "saas": ["saas", "software as a service", "platform", "subscription", "cloud software"],
            "manufacturing": ["manufacturing", "factory", "production", "assembly", "supply chain"],
            "logistics": ["logistics", "shipping", "delivery", "warehouse", "freight", "transport"],
            "retail": ["retail", "e-commerce", "store", "shopping", "consumer", "inventory"]
        }
        
        # Combine idea title and original_idea/rephrased_idea for analysis
        idea_text = getattr(idea, 'original_idea', '') or ''
        rephrased = getattr(idea, 'rephrased_idea', '') or ''
        title = getattr(idea, 'title', '') or ''
        text = f"{title} {idea_text} {rephrased}".lower()
        
        # Check for keyword matches
        for industry, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword in text:
                    return industry
        
        return "general"
    
    def _calculate_projection_confidence(self, idea: Any) -> Dict[str, Any]:
        """
        Calculate confidence level for projections with detailed reasoning.
        """
        confidence = {
            "level": "low",
            "score": 0,
            "factors": [],
            "missing_data": []
        }
        
        # Factor 1: Research data availability
        if idea.research_data:
            if idea.research_data.get('resource_estimation'):
                confidence["score"] += 25
                confidence["factors"].append("Detailed resource estimation available")
            else:
                confidence["missing_data"].append("Resource estimation not performed")
            
            if idea.research_data.get('idea_research'):
                confidence["score"] += 20
                confidence["factors"].append("Market research completed")
            else:
                confidence["missing_data"].append("Market research not available")
            
            if idea.research_data.get('company_research'):
                confidence["score"] += 15
                confidence["factors"].append("Company context analyzed")
        else:
            confidence["missing_data"].append("No research data - estimates are rough approximations")
        
        # Factor 2: AI Score quality
        if idea.ai_score:
            if idea.ai_score >= 70:
                confidence["score"] += 20
                confidence["factors"].append(f"Strong AI score ({idea.ai_score}/100)")
            elif idea.ai_score >= 50:
                confidence["score"] += 10
                confidence["factors"].append(f"Moderate AI score ({idea.ai_score}/100)")
            else:
                confidence["missing_data"].append(f"Low AI score ({idea.ai_score}/100) indicates uncertainty")
        else:
            confidence["missing_data"].append("No AI evaluation performed")
        
        # Factor 3: Approval status
        status = getattr(idea, 'status', 'submitted')
        if status == 'approved':
            confidence["score"] += 20
            confidence["factors"].append("Idea approved by reviewers")
        elif status == 'under_review':
            confidence["score"] += 5
            confidence["factors"].append("Currently under review")
        
        # Determine level
        if confidence["score"] >= 70:
            confidence["level"] = "high"
        elif confidence["score"] >= 40:
            confidence["level"] = "medium"
        else:
            confidence["level"] = "low"
        
        return confidence
    
    def _estimate_timeline(self, idea: Any, score: int) -> Dict[str, Any]:
        """
        Estimate implementation timeline based on actual research data.
        Returns detailed timeline with phases when available.
        """
        timeline = {
            "total_months": 6,
            "phases": [],
            "has_real_data": False
        }
        
        # Check for actual timeline data
        if idea.research_data and idea.research_data.get('resource_estimation'):
            res_est = idea.research_data['resource_estimation']
            timeline_data = res_est.get('timeline', [])
            
            if timeline_data:
                timeline["has_real_data"] = True
                total_weeks = 0
                
                for phase in timeline_data:
                    if isinstance(phase, dict):
                        phase_name = phase.get('phase', 'Phase')
                        duration = phase.get('duration', '')
                        deliverables = phase.get('key_deliverables', '')
                        
                        # Parse duration
                        import re
                        weeks = 4  # default
                        if isinstance(duration, str):
                            week_match = re.search(r'(\d+)\s*week', duration.lower())
                            month_match = re.search(r'(\d+)\s*month', duration.lower())
                            if week_match:
                                weeks = int(week_match.group(1))
                            elif month_match:
                                weeks = int(month_match.group(1)) * 4
                        
                        total_weeks += weeks
                        timeline["phases"].append({
                            "name": phase_name,
                            "duration_weeks": weeks,
                            "deliverables": deliverables
                        })
                
                timeline["total_months"] = max(3, total_weeks // 4)
        
        # Fallback estimation
        if not timeline["has_real_data"]:
            if score >= 75:
                timeline["total_months"] = 4
                timeline["phases"] = [
                    {"name": "Discovery & Planning", "duration_weeks": 2, "deliverables": "Requirements, Architecture"},
                    {"name": "Development", "duration_weeks": 10, "deliverables": "Core Features"},
                    {"name": "Testing & Launch", "duration_weeks": 4, "deliverables": "QA, Deployment"}
                ]
            elif score >= 50:
                timeline["total_months"] = 6
                timeline["phases"] = [
                    {"name": "Discovery & Planning", "duration_weeks": 4, "deliverables": "Requirements, Architecture"},
                    {"name": "Development", "duration_weeks": 16, "deliverables": "Core Features"},
                    {"name": "Testing & Launch", "duration_weeks": 4, "deliverables": "QA, Deployment"}
                ]
            else:
                timeline["total_months"] = 8
                timeline["phases"] = [
                    {"name": "Discovery & Validation", "duration_weeks": 6, "deliverables": "Requirements, Proof of Concept"},
                    {"name": "Development", "duration_weeks": 20, "deliverables": "Core Features"},
                    {"name": "Testing & Launch", "duration_weeks": 6, "deliverables": "QA, Deployment"}
                ]
        
        return timeline
    
    def _get_risk_level(self, idea: Any) -> str:
        """Get risk level label"""
        risk_score = self._calculate_risk_score(idea)
        if risk_score <= 33:
            return "low"
        elif risk_score <= 66:
            return "medium"
        return "high"
    
    def _get_health_indicator(self, avg_score: float) -> str:
        """Get health indicator based on average score"""
        if avg_score >= 70:
            return "healthy"
        elif avg_score >= 50:
            return "moderate"
        return "needs_attention"
    
    def _calculate_trend(self, monthly_data: Dict[str, int], months: List[str]) -> str:
        """Calculate trend direction"""
        if len(months) < 2:
            return "stable"
        
        recent = sum([monthly_data.get(m, 0) for m in months[-2:]])
        earlier = sum([monthly_data.get(m, 0) for m in months[:-2]])
        
        if recent > earlier * 1.2:
            return "increasing"
        elif recent < earlier * 0.8:
            return "decreasing"
        return "stable"
    
    def _estimate_avg_approval_time(self, ideas: List[Any]) -> int:
        """Estimate average time to approval in days"""
        # Simplified estimation
        approved_ideas = [i for i in ideas if getattr(i, 'status', '') == 'approved']
        if not approved_ideas:
            return 14  # Default 2 weeks
        
        return 7  # Placeholder - would need actual timestamp tracking


# Global instance
portfolio_analytics_service = PortfolioAnalyticsService()
