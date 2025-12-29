"""Innovation Portfolio Dashboard - Executive-level portfolio intelligence"""

import streamlit as st
import logging
from typing import Dict, Any, List
from services.idea_service import idea_service
from services.portfolio_analytics_service import portfolio_analytics_service
from utils.auth import is_reviewer, get_current_user

logger = logging.getLogger(__name__)


def _format_amount(amount: float) -> str:
    """Format amount in K or M format for readability"""
    if amount >= 1000000:
        return f"${amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"${amount/1000:.0f}K"
    else:
        return f"${amount:.0f}"


def show_portfolio_dashboard():
    """Display the Innovation Portfolio Dashboard for executives"""
    st.header("🎯 Innovation Portfolio Dashboard")
    st.markdown("Executive-level insights into your organization's innovation portfolio.")
    
    # Check access (Directors and Managers only)
    if not is_reviewer():
        st.error("Access restricted. This dashboard is available to Managers and Directors only.")
        return
    
    try:
        # Fetch all ideas
        ideas = idea_service.get_all_ideas(limit=500)
        
        if not ideas:
            st.info("No ideas in the portfolio yet. Start by encouraging teams to submit ideas!")
            return
        
        # Generate portfolio analytics
        analytics = portfolio_analytics_service.analyze_portfolio(ideas)
        
        # Render dashboard sections
        _render_executive_summary(analytics.get("summary", {}))
        
        st.divider()
        
        # Main dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Idea Clusters",
            "🗺️ Department Heatmap", 
            "💰 Budget & ROI",
            "📋 Recommendations"
        ])
        
        with tab1:
            _render_idea_clusters(analytics.get("clusters", []))
        
        with tab2:
            _render_department_heatmap(analytics.get("department_heatmap", {}))
        
        with tab3:
            _render_budget_roi_projections(analytics.get("budget_roi_projections", []))
        
        with tab4:
            _render_recommendations(analytics.get("recommendations", []))
        
    except Exception as e:
        st.error(f"Error loading portfolio dashboard: {str(e)}")
        logger.error(f"Portfolio dashboard error: {e}")


def _render_executive_summary(summary: Dict[str, Any]):
    """Render the executive summary section"""
    st.subheader("📈 Portfolio Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Ideas",
            summary.get("total_ideas", 0),
            help="Total number of ideas in the portfolio"
        )
    
    with col2:
        st.metric(
            "Avg Score",
            f"{summary.get('avg_score', 0):.1f}",
            help="Average AI evaluation score across all ideas"
        )
    
    with col3:
        st.metric(
            "Approval Rate",
            f"{summary.get('approval_rate', 0):.1f}%",
            help="Percentage of reviewed ideas that were approved"
        )
    
    with col4:
        st.metric(
            "High Potential",
            summary.get("high_potential_count", 0),
            help="Ideas with score >= 75"
        )
    
    with col5:
        estimated_value = summary.get("estimated_total_value", 0)
        if estimated_value >= 1000000:
            value_str = f"${estimated_value/1000000:.1f}M"
        elif estimated_value >= 1000:
            value_str = f"${estimated_value/1000:.0f}K"
        else:
            value_str = f"${estimated_value:.0f}"
        st.metric(
            "Est. Portfolio Value",
            value_str,
            help="Estimated total value of the innovation portfolio"
        )
    
    # Status breakdown
    st.markdown("#### Ideas by Status")
    status_counts = summary.get("ideas_by_status", {})
    
    if status_counts:
        cols = st.columns(len(status_counts))
        status_colors = {
            "submitted": "#17a2b8",
            "under_review": "#ffc107",
            "approved": "#28a745",
            "rejected": "#dc3545",
            "in_progress": "#6f42c1",
            "completed": "#20c997"
        }
        
        for idx, (status, count) in enumerate(status_counts.items()):
            with cols[idx]:
                color = status_colors.get(status, "#6c757d")
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: {color}15; 
                            border-radius: 10px; border-left: 4px solid {color};'>
                    <h3 style='margin: 0; color: {color};'>{count}</h3>
                    <p style='margin: 0; color: #666; text-transform: capitalize;'>{status.replace('_', ' ')}</p>
                </div>
                """, unsafe_allow_html=True)


def _render_idea_clusters(clusters: List[Dict[str, Any]]):
    """Render idea clusters visualization"""
    st.subheader("Idea Clusters")
    st.markdown("Ideas grouped by domain, impact level, and risk profile.")
    
    if not clusters:
        st.info("No clusters available. Add more ideas to see clustering.")
        return
    
    # Group clusters by type
    domain_clusters = [c for c in clusters if c.get("cluster_type") == "domain"]
    impact_clusters = [c for c in clusters if c.get("cluster_type") == "impact"]
    risk_clusters = [c for c in clusters if c.get("cluster_type") == "risk"]
    
    # Domain clusters
    st.markdown("### 🏢 By Department/Domain")
    if domain_clusters:
        cols = st.columns(min(4, len(domain_clusters)))
        for idx, cluster in enumerate(domain_clusters[:4]):
            with cols[idx]:
                health = cluster.get("health_indicator", "moderate")
                health_colors = {"healthy": "#28a745", "moderate": "#ffc107", "needs_attention": "#dc3545"}
                color = health_colors.get(health, "#6c757d")
                
                st.markdown(f"""
                <div style='padding: 15px; background-color: #f8f9fa; border-radius: 10px; 
                            border-top: 4px solid {color}; margin-bottom: 10px;'>
                    <h4 style='margin: 0 0 10px 0;'>{cluster.get("name", "Unknown")}</h4>
                    <p style='margin: 5px 0;'>📊 <strong>{cluster.get("idea_count", 0)}</strong> ideas</p>
                    <p style='margin: 5px 0;'>⭐ Avg Score: <strong>{cluster.get("avg_score", 0)}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show ideas in expander
                with st.expander("View Ideas"):
                    for idea in cluster.get("ideas", [])[:5]:
                        st.markdown(f"- {idea.get('title', 'Untitled')} (Score: {idea.get('score', 'N/A')})")
    
    # Impact clusters
    st.markdown("### 💥 By Impact Level")
    if impact_clusters:
        cols = st.columns(3)
        for idx, cluster in enumerate(impact_clusters[:3]):
            with cols[idx]:
                color = cluster.get("color", "#6c757d")
                st.markdown(f"""
                <div style='padding: 15px; background-color: {color}15; border-radius: 10px;
                            border-left: 4px solid {color};'>
                    <h4 style='margin: 0; color: {color};'>{cluster.get("name", "Unknown")}</h4>
                    <p style='margin: 10px 0;'><strong>{cluster.get("idea_count", 0)}</strong> ideas</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Risk clusters
    st.markdown("### ⚠️ By Risk Profile")
    if risk_clusters:
        cols = st.columns(3)
        for idx, cluster in enumerate(risk_clusters[:3]):
            with cols[idx]:
                color = cluster.get("color", "#6c757d")
                icon = {"Low Risk": "🟢", "Medium Risk": "🟡", "High Risk": "🔴"}.get(cluster.get("name"), "⚪")
                st.markdown(f"""
                <div style='padding: 15px; background-color: {color}15; border-radius: 10px;'>
                    <h4 style='margin: 0;'>{icon} {cluster.get("name", "Unknown")}</h4>
                    <p style='margin: 10px 0;'><strong>{cluster.get("idea_count", 0)}</strong> ideas</p>
                    <small>Avg Score: {cluster.get("avg_score", 0)}</small>
                </div>
                """, unsafe_allow_html=True)


def _render_department_heatmap(heatmap: Dict[str, Dict[str, Any]]):
    """Render department innovation heatmap"""
    st.subheader("Department Innovation Heatmap")
    st.markdown("Visualize innovation activity and success rates across departments.")
    
    if not heatmap:
        st.info("No department data available.")
        return
    
    # Sort departments by innovation index
    sorted_depts = sorted(heatmap.items(), key=lambda x: x[1].get("innovation_index", 0), reverse=True)
    
    # Heatmap grid
    for dept_name, dept_data in sorted_depts:
        heat_color = dept_data.get("heat_color", "#6c757d")
        heat_level = dept_data.get("heat_level", "cool")
        heat_icons = {"hot": "🔥", "warm": "☀️", "cool": "❄️"}
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style='padding: 10px; background-color: {heat_color}20; border-radius: 8px;
                            border-left: 5px solid {heat_color};'>
                    <h4 style='margin: 0;'>{heat_icons.get(heat_level, "⚪")} {dept_name}</h4>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Ideas", dept_data.get("idea_count", 0))
            
            with col3:
                st.metric("Avg Score", dept_data.get("avg_score", 0))
            
            with col4:
                st.metric("Success Rate", f"{dept_data.get('success_rate', 0)}%")
            
            with col5:
                st.metric("Innovation Index", dept_data.get("innovation_index", 0))
            
            # Progress bar for innovation index
            innovation_index = dept_data.get("innovation_index", 0)
            st.progress(min(innovation_index / 100, 1.0))
            
            # Expandable details
            with st.expander(f"Details for {dept_name}"):
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    st.markdown(f"✅ Approved: **{dept_data.get('approved_count', 0)}**")
                    st.markdown(f"❌ Rejected: **{dept_data.get('rejected_count', 0)}**")
                    st.markdown(f"⏳ In Progress: **{dept_data.get('in_progress_count', 0)}**")
                
                with dcol2:
                    st.markdown("**Top Ideas:**")
                    for idea_title in dept_data.get("top_ideas", [])[:3]:
                        st.markdown(f"- {idea_title}")
            
            st.markdown("")  # Spacing


def _render_budget_roi_projections(projections: List[Dict[str, Any]]):
    """Render budget vs ROI projections with detailed breakdowns"""
    st.subheader("💰 Budget & ROI Projections")
    st.markdown("Financial projections based on actual resource estimation and market research data.")
    
    if not projections:
        st.info("No projections available. Submit ideas with research data to see detailed projections.")
        return
    
    # Summary metrics
    total_budget = sum([p.get("budget_estimate", 0) for p in projections])
    total_roi = sum([p.get("roi_projection", 0) for p in projections])
    total_net = sum([p.get("net_value", 0) for p in projections])
    avg_roi_pct = sum([p.get("roi_percentage", 0) for p in projections]) / len(projections) if projections else 0
    
    # Count ideas with real data vs estimates
    with_real_data = len([p for p in projections if p.get("has_budget_data") or p.get("has_roi_data")])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Est. Investment",
            _format_amount(total_budget),
            help="Sum of all project budgets including team, infrastructure, and contingency"
        )
    
    with col2:
        st.metric(
            "Projected Returns",
            _format_amount(total_roi),
            help="Projected value based on market research and implementation data"
        )
    
    with col3:
        st.metric(
            "Net Value",
            _format_amount(total_net),
            delta=f"{avg_roi_pct:.0f}% avg ROI" if total_budget > 0 else "N/A"
        )
    
    with col4:
        high_conf = len([p for p in projections if p.get("confidence") == "high"])
        st.metric("High Confidence", f"{high_conf}/{len(projections)}")
    
    with col5:
        st.metric(
            "With Research Data",
            f"{with_real_data}/{len(projections)}",
            help="Ideas with actual resource estimation data"
        )
    
    st.divider()
    
    # Individual projections
    st.markdown("### 📊 Idea-Level Financial Analysis")
    
    # Filter options
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        confidence_filter = st.selectbox(
            "Filter by Confidence",
            ["All", "High", "Medium", "Low"],
            key="roi_confidence_filter"
        )
    with col_f2:
        sort_by = st.selectbox(
            "Sort by",
            ["Net Value (High to Low)", "ROI % (High to Low)", "Budget (Low to High)", "Score (High to Low)"],
            key="roi_sort_by"
        )
    with col_f3:
        data_filter = st.selectbox(
            "Data Quality",
            ["All", "With Research Data", "Estimates Only"],
            key="roi_data_filter"
        )
    
    # Apply filters
    filtered = projections
    if confidence_filter != "All":
        filtered = [p for p in filtered if p.get("confidence", "").lower() == confidence_filter.lower()]
    
    if data_filter == "With Research Data":
        filtered = [p for p in filtered if p.get("has_budget_data") or p.get("has_roi_data")]
    elif data_filter == "Estimates Only":
        filtered = [p for p in filtered if not p.get("has_budget_data") and not p.get("has_roi_data")]
    
    # Apply sorting
    if "Net Value" in sort_by:
        filtered = sorted(filtered, key=lambda x: x.get("net_value", 0), reverse=True)
    elif "ROI %" in sort_by:
        filtered = sorted(filtered, key=lambda x: x.get("roi_percentage", 0), reverse=True)
    elif "Budget" in sort_by:
        filtered = sorted(filtered, key=lambda x: x.get("budget_estimate", 0))
    elif "Score" in sort_by:
        filtered = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)
    
    if not filtered:
        st.info("No ideas match your filter criteria.")
        return
    
    # Display projections with detailed breakdown
    for idx, proj in enumerate(filtered[:10]):
        _render_detailed_projection_card(proj, idx)


def _render_detailed_projection_card(proj: Dict[str, Any], idx: int):
    """Render a detailed projection card with budget breakdown"""
    risk_colors = {"low": "#28a745", "medium": "#ffc107", "high": "#dc3545"}
    risk_color = risk_colors.get(proj.get("risk_level", "medium"), "#6c757d")
    
    has_real_data = proj.get("has_budget_data") or proj.get("has_roi_data")
    data_badge = "📊 Research Data" if has_real_data else "📐 Estimated"
    data_badge_color = "#28a745" if has_real_data else "#ffc107"
    
    with st.container(border=True):
        # Header
        col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
        
        with col_h1:
            st.markdown(f"### {proj.get('title', 'Untitled')}")
            st.caption(f"🏢 {proj.get('department', 'General')} • ⭐ Score: {proj.get('score', 'N/A')}")
        
        with col_h2:
            st.markdown(f"""
            <div style='text-align: center; padding: 5px; background-color: {risk_color}20; 
                        border-radius: 8px; border: 1px solid {risk_color};'>
                <small style='color: {risk_color}; font-weight: bold;'>
                    {proj.get("risk_level", "medium").upper()} RISK
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_h3:
            st.markdown(f"""
            <div style='text-align: center; padding: 5px; background-color: {data_badge_color}20; 
                        border-radius: 8px;'>
                <small style='color: {data_badge_color};'>{data_badge}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Main metrics
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
        
        with mcol1:
            budget = proj.get("budget_estimate", 0)
            st.metric("💵 Total Budget", _format_amount(budget))
        
        with mcol2:
            roi = proj.get("roi_projection", 0)
            st.metric("📈 Projected Value", _format_amount(roi))
        
        with mcol3:
            roi_pct = proj.get('roi_percentage', 0)
            st.metric("📊 ROI", f"{roi_pct:.0f}%")
        
        with mcol4:
            net = proj.get("net_value", 0)
            st.metric("💰 Net Value", _format_amount(net))
        
        with mcol5:
            st.metric("⏱️ Timeline", f"{proj.get('timeline_months', 6)} months")
        
        # Industry Comparison & Differentiators
        industry_comp = proj.get("industry_comparison", {})
        differentiators = proj.get("differentiators", [])
        
        if industry_comp or differentiators:
            ind_col1, ind_col2 = st.columns([1, 1])
            
            with ind_col1:
                if industry_comp:
                    industry_name = industry_comp.get("industry", "General")
                    industry_avg = industry_comp.get("industry_avg_roi", 100)
                    industry_range = industry_comp.get("industry_roi_range", "40% - 200%")
                    vs_industry = industry_comp.get("vs_industry_label", "")
                    
                    vs_color = "#28a745" if "above" in vs_industry.lower() else "#ffc107" if "par" in vs_industry.lower() else "#dc3545"
                    
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: #f0f8ff; border-radius: 8px; border-left: 3px solid #17a2b8;'>
                        <small style='color: #666;'>🏭 {industry_name} Industry Benchmark</small><br>
                        <span>Avg ROI: <strong>{industry_avg}%</strong> | Range: {industry_range}</span><br>
                        <span style='color: {vs_color}; font-weight: bold;'>{vs_industry}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col2:
                if differentiators:
                    st.markdown("**🌟 What Makes This POC Different:**")
                    for diff in differentiators[:3]:
                        st.markdown(f"<small style='color: #28a745;'>✓ {diff}</small>", unsafe_allow_html=True)
        
        # Confidence indicator with details
        conf = proj.get("confidence", "medium")
        conf_score = proj.get("confidence_score", 0)
        conf_icons = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        
        st.markdown(f"**Confidence:** {conf_icons.get(conf, '⚪')} {conf.title()} ({conf_score}% certainty)")
        
        # Expandable details section
        with st.expander("📋 View Detailed Breakdown", expanded=False):
            tab1, tab2, tab3, tab4 = st.tabs(["💵 Budget Details", "📈 ROI Factors", "⏱️ Timeline", "ℹ️ Confidence"])
            
            with tab1:
                _render_budget_breakdown(proj)
            
            with tab2:
                _render_roi_factors(proj)
            
            with tab3:
                _render_timeline_details(proj)
            
            with tab4:
                _render_confidence_details(proj)


def _render_budget_breakdown(proj: Dict[str, Any]):
    """Render detailed budget breakdown"""
    breakdown = proj.get("budget_breakdown", {})
    
    st.markdown("#### Cost Categories")
    
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
    
    with bcol1:
        team = breakdown.get("team_costs", 0)
        st.metric("👥 Team Costs", _format_amount(team))
    
    with bcol2:
        infra = breakdown.get("infrastructure_costs", 0)
        st.metric("☁️ Infrastructure", _format_amount(infra))
    
    with bcol3:
        tools = breakdown.get("tools_costs", 0)
        st.metric("🔧 Tools & Software", _format_amount(tools))
    
    with bcol4:
        contingency = breakdown.get("contingency", 0)
        st.metric("🛡️ Contingency (15%)", _format_amount(contingency))
    
    # Team breakdown if available
    team_details = breakdown.get("team_details", [])
    if team_details:
        st.markdown("---")
        st.markdown("##### 👥 Team Resource Breakdown")
        
        for member in team_details[:5]:
            role = member.get("role", "Developer")
            count = member.get("count", 1)
            rate = member.get("rate_per_month", 0)
            duration = member.get("duration_months", 6)
            allocation = member.get("allocation_pct", 100)
            total = member.get("total_cost", 0)
            
            st.markdown(f"""
            - **{role}**: {count} person(s) × ${rate:,.0f}/month × {duration} months 
              {"("+str(allocation)+"% allocation)" if allocation < 100 else ""} = **{_format_amount(total)}**
            """)
    
    # Infrastructure breakdown if available
    infra_details = breakdown.get("infrastructure_details", [])
    if infra_details:
        st.markdown("---")
        st.markdown("##### ☁️ Infrastructure & Services")
        
        for item in infra_details[:5]:
            name = item.get("item", "Service")
            monthly = item.get("monthly_cost", 0)
            total = item.get("total_cost", 0)
            
            st.markdown(f"- **{name}**: ${monthly}/month = **{_format_amount(total)}** total")


def _render_roi_factors(proj: Dict[str, Any]):
    """Render ROI value drivers, factors, and industry comparison"""
    value_drivers = proj.get("value_drivers", [])
    industry_comp = proj.get("industry_comparison", {})
    
    # Industry Comparison Section
    if industry_comp:
        st.markdown("#### 🏭 Industry Benchmark Comparison")
        
        icol1, icol2 = st.columns(2)
        with icol1:
            st.markdown(f"**Industry:** {industry_comp.get('industry', 'General')}")
            st.markdown(f"**Industry Avg ROI:** {industry_comp.get('industry_avg_roi', 100)}%")
        with icol2:
            st.markdown(f"**Industry Range:** {industry_comp.get('industry_roi_range', '40% - 200%')}")
            st.markdown(f"**Typical Payback:** {industry_comp.get('typical_payback_months', 18)} months")
        
        vs_label = industry_comp.get('vs_industry_label', '')
        if vs_label:
            vs_color = "#28a745" if "above" in vs_label.lower() else "#ffc107" if "par" in vs_label.lower() else "#6c757d"
            st.markdown(f"<span style='font-size: 1.2em; color: {vs_color}; font-weight: bold;'>📊 {vs_label}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    st.markdown("#### 📈 Value Drivers")
    
    if value_drivers:
        for driver in value_drivers:
            st.markdown(f"✅ {driver}")
    else:
        st.info("No specific value drivers identified. ROI is based on general scoring.")
    
    st.markdown("---")
    st.markdown("#### 💰 Financial Summary")
    
    fcol1, fcol2 = st.columns(2)
    
    with fcol1:
        st.markdown(f"**Investment Required:** {_format_amount(proj.get('budget_estimate', 0))}")
        st.markdown(f"**Projected Returns:** {_format_amount(proj.get('roi_projection', 0))}")
    
    with fcol2:
        st.markdown(f"**Net Value:** {_format_amount(proj.get('net_value', 0))}")
        st.markdown(f"**Payback Period:** ~{proj.get('payback_months', 12)} months")


def _render_timeline_details(proj: Dict[str, Any]):
    """Render timeline phases"""
    phases = proj.get("timeline_phases", [])
    total_months = proj.get("timeline_months", 6)
    
    st.markdown(f"#### ⏱️ Implementation Timeline: {total_months} Months")
    
    if phases:
        for i, phase in enumerate(phases):
            name = phase.get("name", f"Phase {i+1}")
            weeks = phase.get("duration_weeks", 4)
            deliverables = phase.get("deliverables", "")
            
            st.markdown(f"""
            **{i+1}. {name}** ({weeks} weeks)
            - Deliverables: {deliverables}
            """)
    else:
        st.info("Detailed timeline not available. Showing estimated duration.")


def _render_confidence_details(proj: Dict[str, Any]):
    """Render confidence factors and missing data"""
    factors = proj.get("confidence_factors", [])
    missing = proj.get("missing_data", [])
    conf_score = proj.get("confidence_score", 0)
    
    st.markdown(f"#### Confidence Score: {conf_score}%")
    
    # Progress bar
    st.progress(conf_score / 100)
    
    if factors:
        st.markdown("##### ✅ Positive Factors")
        for factor in factors:
            st.markdown(f"- {factor}")
    
    if missing:
        st.markdown("##### ⚠️ Missing Data / Uncertainties")
        for item in missing:
            st.markdown(f"- {item}")


def _render_recommendations(recommendations: List[Dict[str, Any]]):
    """Render portfolio recommendations"""
    st.subheader("Strategic Recommendations")
    st.markdown("AI-generated insights and action items for your innovation portfolio.")
    
    if not recommendations:
        st.success("✅ Your portfolio is in great shape! No recommendations at this time.")
        return
    
    # Group by priority
    high_priority = [r for r in recommendations if r.get("priority") == "high"]
    medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
    low_priority = [r for r in recommendations if r.get("priority") == "low"]
    
    if high_priority:
        st.markdown("### 🔴 High Priority")
        for rec in high_priority:
            _render_recommendation_card(rec, "#dc3545")
    
    if medium_priority:
        st.markdown("### 🟡 Medium Priority")
        for rec in medium_priority:
            _render_recommendation_card(rec, "#ffc107")
    
    if low_priority:
        st.markdown("### 🟢 Suggestions")
        for rec in low_priority:
            _render_recommendation_card(rec, "#28a745")


def _render_recommendation_card(rec: Dict[str, Any], color: str):
    """Render a single recommendation card"""
    icon = rec.get("icon", "💡")
    rec_type = rec.get("type", "insight")
    type_labels = {"action": "Action Required", "warning": "Warning", "opportunity": "Opportunity", "insight": "Insight"}
    
    st.markdown(f"""
    <div style='padding: 15px; background-color: {color}10; border-radius: 10px; 
                margin: 10px 0; border-left: 4px solid {color};'>
        <div style='display: flex; align-items: flex-start; gap: 10px;'>
            <span style='font-size: 24px;'>{icon}</span>
            <div>
                <h4 style='margin: 0 0 5px 0;'>{rec.get("title", "Recommendation")}</h4>
                <p style='margin: 0; color: #666;'>{rec.get("description", "")}</p>
                <small style='color: {color}; font-weight: bold;'>{type_labels.get(rec_type, "Insight").upper()}</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
