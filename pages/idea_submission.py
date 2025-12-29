"""New Idea Submission Page with Company Research Integration"""

import streamlit as st
from services.workflow_orchestrator import workflow_orchestrator
from services.idea_service import idea_service
from services.ai_score_service import ai_score_service
from services.research_document_generator import research_document_generator
import uuid


def show():
    st.title("Submit New Idea")
    st.markdown("Submit your business idea with comprehensive company research and market analysis")
    
    # Initialize session state for workflow
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = None # None, starting, company_research, idea_research, resource_estimation, questions, completed
    if 'workflow_inputs' not in st.session_state:
        st.session_state.workflow_inputs = {}
    
    # Idea submission form
    with st.form("idea_submission_form"):
        st.subheader("Idea Information")
        
        company_name = st.text_input(
            "Target Company Name *",
            placeholder="e.g., Microsoft, Google, Amazon..."
        )
        
        idea_title = st.text_input(
            "Idea Title *",
            placeholder="e.g., AI-Powered Customer Support Automation"
        )
        
        idea_description = st.text_area(
            "Idea Description *",
            placeholder="Describe your idea in detail...\n\nWhat problem does it solve?\nHow does it work?\nWhat value does it create?",
            height=150
        )
        
        submit_button = st.form_submit_button("Start Research & Analysis")
    
    # Handle form submission
    if submit_button:
        if not company_name or not idea_title or not idea_description:
            st.error("Please fill in all required fields marked with *")
        else:
            st.session_state.workflow_inputs = {
                "company_name": company_name,
                "idea_title": idea_title,
                "idea_description": idea_description
            }
            st.session_state.workflow_step = "starting"
            st.rerun()

    # Workflow State Machine
    if st.session_state.workflow_step == "starting":
        st.session_state.workflow_results = {
            "success": True,
            "company_name": st.session_state.workflow_inputs["company_name"],
            "idea_title": st.session_state.workflow_inputs["idea_title"],
            "company_research": None,
            "idea_research": None,
            "resource_estimation": None,
            "development_questions": [],
            "errors": []
        }
        st.session_state.workflow_step = "company_research"
        st.rerun()

    elif st.session_state.workflow_step == "company_research":
        with st.spinner(f"Researching {st.session_state.workflow_inputs['company_name']}..."):
            res = workflow_orchestrator.perform_company_research(st.session_state.workflow_inputs["company_name"])
            st.session_state.workflow_results["company_research"] = res
            if not res.get("success"):
                st.session_state.workflow_results["errors"].append(res.get("error"))
            st.session_state.workflow_step = "idea_research"
            st.rerun()

    elif st.session_state.workflow_step == "idea_research":
        with st.spinner(f"Researching market for: {st.session_state.workflow_inputs['idea_title']}..."):
            res = workflow_orchestrator.perform_idea_research(
                st.session_state.workflow_inputs["idea_title"],
                st.session_state.workflow_inputs["idea_description"]
            )
            st.session_state.workflow_results["idea_research"] = res
            if not res.get("success"):
                st.session_state.workflow_results["errors"].append(res.get("error"))
            st.session_state.workflow_step = "resource_estimation"
            st.rerun()

    elif st.session_state.workflow_step == "resource_estimation":
        with st.spinner(f"Estimating resources for: {st.session_state.workflow_inputs['idea_title']}..."):
            res = workflow_orchestrator.perform_resource_estimation(
                st.session_state.workflow_inputs["company_name"],
                st.session_state.workflow_inputs["idea_title"],
                st.session_state.workflow_inputs["idea_description"],
                st.session_state.workflow_results["company_research"],
                st.session_state.workflow_results["idea_research"]
            )
            st.session_state.workflow_results["resource_estimation"] = res
            if not res.get("success"):
                st.session_state.workflow_results["errors"].append(res.get("error"))
            st.session_state.workflow_step = "questions"
            st.rerun()


    elif st.session_state.workflow_step == "questions":
        with st.spinner("Generating development questions..."):
            res = workflow_orchestrator.generate_development_questions(
                st.session_state.workflow_results["company_research"],
                st.session_state.workflow_results["idea_research"],
                st.session_state.workflow_inputs["company_name"],
                st.session_state.workflow_inputs["idea_title"],
                st.session_state.workflow_inputs["idea_description"]
            )
            st.session_state.workflow_results["development_questions"] = res
            st.session_state.workflow_step = "completed"
            st.rerun()
            
    if st.session_state.workflow_step == "completed":
        st.success("Research workflow completed successfully!")
    
    # Show workflow results if available (Partial or Complete)
    if st.session_state.workflow_results:
        workflow_results = st.session_state.workflow_results
        
        st.markdown("---")
        st.markdown("## Research Results")
        
        # ==================== COMPANY RESEARCH SECTION ====================
        if workflow_results.get('company_research'):
            company_research = workflow_results['company_research']
            
            st.markdown("## Company Research")
            
            # Two-column layout: Details on left, Sources on right
            col_details, col_sources = st.columns([2, 1])
            
            with col_details:
                # Business Overview
                if company_research.get('what_company_does'):
                    st.markdown("#### Business Overview")
                    st.write(company_research['what_company_does'])
                    st.markdown("")
                
                # Financial Context
                if company_research.get('financials', {}).get('annual_revenue') or company_research.get('financials', {}).get('recent_performance'):
                    st.markdown("#### Financial Context")
                    financials = company_research.get('financials', {})
                    if financials.get('annual_revenue'):
                        st.write(f"**Annual Revenue:** {financials['annual_revenue']}")
                    if financials.get('recent_performance'):
                        st.write(financials['recent_performance'])
                    st.markdown("")
                
                # Current Initiatives
                if company_research.get('current_initiatives_and_goals'):
                    st.markdown("#### Current Initiatives & Goals")
                    initiatives = company_research['current_initiatives_and_goals']
                    if isinstance(initiatives, list):
                        for i, initiative in enumerate(initiatives[:8], 1):
                            st.markdown(f"**{i}.** {initiative}")
                    else:
                        st.write(initiatives)
                    st.markdown("")
                
                # Growth Opportunities
                if company_research.get('opportunities'):
                    st.markdown("#### Growth Opportunities")
                    for i, opportunity in enumerate(company_research['opportunities'][:8], 1):
                        st.markdown(f"**{i}.** {opportunity}")
                    st.markdown("")
                
                # Business Challenges
                if company_research.get('challenges'):
                    st.markdown("#### Business Challenges")
                    for i, challenge in enumerate(company_research['challenges'][:8], 1):
                        st.markdown(f"**{i}.** {challenge}")
                    st.markdown("")
                
                # Competitors
                if company_research.get('competitors'):
                    st.markdown("#### Key Competitors")
                    competitors = company_research['competitors']
                    if isinstance(competitors, list):
                        for competitor in competitors[:8]:
                            if isinstance(competitor, dict):
                                name = competitor.get('name', 'Unknown')
                                desc = competitor.get('description', '')
                                st.markdown(f"**{name}**")
                                if desc:
                                    st.write(f"_{desc}_")
                            else:
                                st.markdown(f"- {competitor}")
                    st.markdown("")
            
            with col_sources:
                # Display Sources in a box
                if company_research.get('sources'):
                    st.markdown("#### Research Sources")
                    sources_html = '<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;">'
                    for idx, source in enumerate(company_research['sources'][:5], 1):
                        url = source.get('url')
                        title = source.get('source', 'Source')
                        if url and url != 'N/A':
                            sources_html += f'<p style="margin: 10px 0;"><strong>{idx}.</strong> <a href="{url}" target="_blank" style="color: #1f77b4; text-decoration: none;">{title}</a></p>'
                    sources_html += '</div>'
                    st.markdown(sources_html, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # ==================== IDEA RESEARCH SECTION ====================
        if workflow_results.get('idea_research') and workflow_results['idea_research'].get('success'):
            idea_research = workflow_results['idea_research']
            
            st.markdown("## 📊 POC Analysis Dashboard")
            
            # ==================== MAIN VERDICT BOX (TOP CENTER) ====================
            workability = idea_research.get('workability_assessment', {})
            if workability:
                verdict = workability.get('verdict', 'WORKABLE')
                is_workable = workability.get('is_workable', True)
                confidence = workability.get('confidence', 'Medium')
                reasoning = workability.get('reasoning', '')
                
                # Color based on verdict
                if verdict == "WORKABLE" or is_workable:
                    bg_color = "#d4edda"
                    border_color = "#28a745"
                    icon = "✅"
                    verdict_text = "WORKABLE"
                elif verdict == "NOT WORKABLE":
                    bg_color = "#f8d7da"
                    border_color = "#dc3545"
                    icon = "❌"
                    verdict_text = "NOT WORKABLE"
                else:
                    bg_color = "#fff3cd"
                    border_color = "#ffc107"
                    icon = "⚠️"
                    verdict_text = "NEEDS VALIDATION"
                
                # Large prominent verdict box
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {bg_color} 0%, #ffffff 100%); 
                            padding: 30px; border-radius: 15px; border: 3px solid {border_color}; 
                            margin-bottom: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h1 style="margin: 0; color: {border_color}; font-size: 2.5em;">{icon} {verdict_text}</h1>
                    <p style="margin: 15px 0 10px 0; font-size: 1.2em; color: #555;">
                        <strong>Confidence Level:</strong> 
                        <span style="background-color: {border_color}; color: white; padding: 5px 15px; border-radius: 20px;">{confidence}</span>
                    </p>
                    <p style="margin: 15px 0 0 0; color: #333; font-size: 1.1em; line-height: 1.6;">{reasoning}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== THREE COLUMN SUMMARY ====================
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3; height: 100%;">
                    <h4 style="margin: 0 0 10px 0; color: #1565C0;">🔍 Similar Solutions</h4>
                </div>
                """, unsafe_allow_html=True)
                similar = workability.get('similar_implementations', []) if workability else []
                if similar:
                    for impl in similar[:4]:
                        st.markdown(f"• {impl}")
                else:
                    st.info("No similar implementations found - this could be innovative!")
            
            with col2:
                st.markdown("""
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800; height: 100%;">
                    <h4 style="margin: 0 0 10px 0; color: #E65100;">⚡ Key Challenges</h4>
                </div>
                """, unsafe_allow_html=True)
                challenges = workability.get('key_challenges', []) if workability else []
                if challenges:
                    for challenge in challenges[:4]:
                        st.markdown(f"• {challenge}")
                else:
                    st.success("No major challenges identified!")
            
            with col3:
                st.markdown("""
                <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; height: 100%;">
                    <h4 style="margin: 0 0 10px 0; color: #2E7D32;">🎯 Success Factors</h4>
                </div>
                """, unsafe_allow_html=True)
                success_factors = workability.get('success_factors', []) if workability else []
                if success_factors:
                    for factor in success_factors[:4]:
                        st.markdown(f"• {factor}")
                else:
                    st.info("Focus on solving the core problem well")
            
            st.markdown("")
            
            # ==================== HOW TO IMPROVE SECTION ====================
            improvements = idea_research.get('improvement_suggestions', {})
            if improvements and improvements.get('overall_recommendation'):
                st.markdown("---")
                st.markdown("## 💡 How to Improve This Idea")
                
                # Overall recommendation box
                st.markdown(f"""
                <div style="background-color: #e7f3ff; padding: 15px; border-radius: 10px; border-left: 4px solid #0066cc; margin-bottom: 15px;">
                    <p style="margin: 0; color: #333; font-size: 1.1em;"><strong>💡 Recommendation:</strong> {improvements.get('overall_recommendation', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick wins and differentiation in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    quick_wins = improvements.get('quick_wins', [])
                    if quick_wins:
                        st.markdown("#### ⚡ Quick Wins")
                        for win in quick_wins[:4]:
                            st.markdown(f"- {win}")
                    
                    add_features = improvements.get('add_these_features', [])
                    if add_features:
                        st.markdown("#### ➕ Add These Features")
                        for feature in add_features[:4]:
                            st.markdown(f"- {feature}")
                
                with col2:
                    diff_tips = improvements.get('differentiation_tips', [])
                    if diff_tips:
                        st.markdown("#### 🌟 Stand Out From Others")
                        for tip in diff_tips[:4]:
                            st.markdown(f"- {tip}")
                    
                    learn_from = improvements.get('learn_from_others', [])
                    if learn_from:
                        st.markdown("#### 📚 Learn From Others")
                        for lesson in learn_from[:4]:
                            st.markdown(f"- {lesson}")
                
                # Mistakes to avoid
                avoid = improvements.get('avoid_these_mistakes', [])
                if avoid:
                    st.markdown("#### ⚠️ Common Mistakes to Avoid")
                    for mistake in avoid[:4]:
                        st.warning(mistake)
                
                # Alternative approaches if needed
                do_instead = improvements.get('do_this_instead', [])
                if do_instead:
                    st.markdown("#### 🔄 Consider These Alternatives")
                    for alt in do_instead[:3]:
                        st.info(alt)
                
                st.markdown("---")
            
            # Create tabs for Idea Research (including new POC Approaches tab)
            workability_tab, approaches_tab, companies_tab, pros_cons_tab, insights_tab, metrics_tab, sources_tab = st.tabs([
                "📊 Workability Details",
                "🛠️ POC Approaches",
                "🏢 Implementing Companies",
                "⚖️ Pros & Cons",
                "💡 Market Insights",
                "📈 Metrics",
                "📚 Sources"
            ])
            
            # Workability Details Tab
            with workability_tab:
                if workability:
                    st.markdown("#### Detailed Workability Analysis")
                    st.write(workability.get('reasoning', 'No detailed analysis available.'))
                    
                    # All challenges
                    all_challenges = workability.get('key_challenges', [])
                    if all_challenges:
                        st.markdown("#### All Identified Challenges")
                        for i, challenge in enumerate(all_challenges, 1):
                            st.markdown(f"**{i}.** {challenge}")
                    
                    # All success factors
                    all_factors = workability.get('success_factors', [])
                    if all_factors:
                        st.markdown("#### All Success Factors")
                        for i, factor in enumerate(all_factors, 1):
                            st.markdown(f"**{i}.** {factor}")
                else:
                    st.info("Workability assessment not available.")
            
            # POC Approaches Tab
            with approaches_tab:
                poc_approaches = idea_research.get('poc_approaches', [])
                if poc_approaches:
                    st.markdown("#### Different Ways to Build This POC")
                    
                    for i, approach in enumerate(poc_approaches, 1):
                        complexity = approach.get('complexity', 'Medium')
                        complexity_color = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545"}.get(complexity, "#6c757d")
                        
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid {complexity_color};">
                            <h4 style="margin: 0; color: #333;">Approach {i}: {approach.get('approach_name', f'Option {i}')}</h4>
                            <p style="margin: 5px 0; color: #666;"><strong>Complexity:</strong> <span style="color: {complexity_color}; font-weight: bold;">{complexity}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(approach.get('description', ''))
                        
                        # Tools and Technologies
                        tools = approach.get('tools_and_technologies', [])
                        if tools:
                            st.markdown("**🔧 Tools & Technologies:**")
                            tools_html = " ".join([f'<span style="background-color: #e9ecef; padding: 3px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.9em;">{tool}</span>' for tool in tools])
                            st.markdown(tools_html, unsafe_allow_html=True)
                        
                        # Architecture
                        arch = approach.get('architecture', '')
                        if arch:
                            st.markdown(f"**🏗️ Architecture:** {arch}")
                        
                        # Pros and Cons in columns
                        col1, col2 = st.columns(2)
                        with col1:
                            pros = approach.get('pros', [])
                            if pros:
                                st.markdown("**✅ Pros:**")
                                for pro in pros:
                                    st.markdown(f"- {pro}")
                        with col2:
                            cons = approach.get('cons', [])
                            if cons:
                                st.markdown("**❌ Cons:**")
                                for con in cons:
                                    st.markdown(f"- {con}")
                        
                        # Best for
                        best_for = approach.get('best_for', '')
                        if best_for:
                            st.info(f"**Best for:** {best_for}")
                        
                        st.markdown("---")
                else:
                    st.info("No POC implementation approaches available.")
            
            # Companies Tab
            with companies_tab:
                if idea_research.get('who_is_implementing'):
                    st.markdown("#### Companies Implementing This Idea")
                    for i, implementer in enumerate(idea_research['who_is_implementing'], 1):
                        name = implementer.get('name', 'Company')
                        desc = implementer.get('description', '')
                        st.markdown(f"**{i}. {name}**")
                        if desc:
                            st.write(f"_{desc}_")
                        st.markdown("")
                else:
                    st.info("No information on implementing companies available.")

            # Pros & Cons Tab
            with pros_cons_tab:
                pros_cons = idea_research.get('pros_and_cons', {})
                col1, col2 = st.columns(2)
                
                with col1:
                    if pros_cons.get('pros'):
                        st.markdown("#### Implementation Benefits")
                        for i, pro in enumerate(pros_cons['pros'], 1):
                            st.markdown(f"**{i}.** {pro}")
                    else:
                        st.info("No benefits listed.")
                        
                with col2:
                    if pros_cons.get('cons'):
                        st.markdown("#### Implementation Challenges")
                        for i, con in enumerate(pros_cons['cons'], 1):
                            st.markdown(f"**{i}.** {con}")
                    else:
                        st.info("No challenges listed.")

            # Market Insights Tab
            with insights_tab:
                if idea_research.get('useful_insights'):
                    st.markdown("#### Market Insights")
                    for i, insight in enumerate(idea_research['useful_insights'], 1):
                        insight_type = insight.get('type', 'Insight')
                        insight_text = insight.get('insight', '')
                        details = insight.get('details', '')
                        st.markdown(f"**{i}. {insight_type}**")
                        st.write(insight_text)
                        if details:
                            st.write(f"_{details}_")
                        st.markdown("")
                else:
                    st.info("No market insights available.")

            # Metrics Tab
            with metrics_tab:
                metrics = idea_research.get('implementation_metrics', {})
                if any(metrics.values()):
                    st.markdown("#### Implementation Metrics")
                    
                    if metrics.get('implementation_timelines'):
                        st.markdown("**Timelines:**")
                        for timeline in metrics['implementation_timelines']:
                            st.write(f"- {timeline}")
                        st.markdown("")
                    
                    if metrics.get('scale_metrics'):
                        st.markdown("**Scale Metrics:**")
                        for metric in metrics['scale_metrics']:
                            st.write(f"- {metric}")
                        st.markdown("")
                    
                    if metrics.get('adoption_rates'):
                        st.markdown("**Adoption Rates:**")
                        for rate in metrics['adoption_rates']:
                            st.write(f"- {rate}")
                        st.markdown("")
                    
                    if metrics.get('technology_maturity'):
                        st.markdown("**Technology Maturity:**")
                        for maturity in metrics['technology_maturity']:
                            st.write(f"- {maturity}")
                        st.markdown("")
                else:
                    st.info("No implementation metrics available.")

            # Sources Tab
            with sources_tab:
                if idea_research.get('sources'):
                    st.markdown("#### Research Sources")
                    sources_html = '<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 4px solid #2ca02c;">'
                    for idx, source in enumerate(idea_research['sources'], 1):
                        url = source.get('url')
                        title = source.get('title', source.get('source', 'Source'))
                        if url and url != 'N/A':
                            sources_html += f'<p style="margin: 10px 0;"><strong>{idx}.</strong> <a href="{url}" target="_blank" style="color: #2ca02c; text-decoration: none;">{title}</a></p>'
                    sources_html += '</div>'
                    st.markdown(sources_html, unsafe_allow_html=True)
                else:
                    st.info("No sources available.")
            
            st.markdown("---")
        
        # ==================== RESOURCE ESTIMATION SECTION ====================
        if workflow_results.get('resource_estimation') and workflow_results['resource_estimation'].get('success'):
            resource_est = workflow_results['resource_estimation']
            
            st.markdown("## Resource Estimation")
            st.info("AI-powered analysis of resources needed to implement this idea")
            
            # Create tabs for Resource Estimation
            team_tab, timeline_tab, infra_tab, risk_tab, metrics_tab = st.tabs([
                "Team Resources", 
                "Timeline", 
                "Infrastructure", 
                "Risks", 
                "Success Metrics"
            ])
            
            # Team Resources Tab
            with team_tab:
                team_resources = resource_est.get('team_resources', [])
                
                if team_resources:
                    for i, resource in enumerate(team_resources, 1):
                        st.markdown(f"**{i}.** {resource.get('description', 'Team Member')}")
                        if resource.get('role') or resource.get('number_of_people') or resource.get('allocation'):
                            details = []
                            if resource.get('role'):
                                details.append(f"Role: {resource['role']}")
                            if resource.get('number_of_people'):
                                details.append(f"Count: {resource['number_of_people']}")
                            if resource.get('allocation'):
                                details.append(f"Allocation: {resource['allocation']}")
                            st.markdown(" | ".join(details))
                        if resource.get('required_skills'):
                            st.markdown(f"Skills: {resource['required_skills']}")
                        st.markdown("")
                else:
                    # Show raw response if structured parsing failed
                    raw_response = resource_est.get('raw_response', '')
                    if raw_response and '## 1. TEAM RESOURCES' in raw_response:
                        team_section = raw_response.split('## 1. TEAM RESOURCES')[1].split('## 2.')[0] if '## 2.' in raw_response else raw_response.split('## 1. TEAM RESOURCES')[1]
                        st.markdown(team_section)
                    else:
                        st.info("No team resource details available")
            
            # Implementation Timeline Tab
            with timeline_tab:
                timeline = resource_est.get('timeline', [])
                
                if timeline:
                    for i, phase in enumerate(timeline, 1):
                        st.markdown(f"#### Phase {i}: {phase.get('phase', 'Implementation Phase')}")
                        
                        if phase.get('duration'):
                            st.markdown(f"Duration: {phase['duration']}")
                        if phase.get('key_deliverables'):
                            st.markdown(f"Deliverables: {phase['key_deliverables']}")
                        if phase.get('dependencies'):
                            st.markdown(f"Dependencies: {phase['dependencies']}")
                        if phase.get('resources'):
                            st.markdown(f"Resources: {phase['resources']}")
                        st.markdown("")
                else:
                    # Show raw response if structured parsing failed
                    raw_response = resource_est.get('raw_response', '')
                    if raw_response and '## 2. IMPLEMENTATION TIMELINE' in raw_response:
                        timeline_section = raw_response.split('## 2. IMPLEMENTATION TIMELINE')[1].split('## 3.')[0] if '## 3.' in raw_response else raw_response.split('## 2. IMPLEMENTATION TIMELINE')[1]
                        st.markdown(timeline_section)
                    else:
                        st.info("No timeline details available")
            
            # Technical Infrastructure Tab
            with infra_tab:
                infrastructure = resource_est.get('technical_infrastructure', [])
                
                if infrastructure:
                    for i, item in enumerate(infrastructure, 1):
                        st.markdown(f"{i}. {item}")
                else:
                    # Show raw response if structured parsing failed
                    raw_response = resource_est.get('raw_response', '')
                    if raw_response and '## 3. TECHNICAL INFRASTRUCTURE' in raw_response:
                        infra_section = raw_response.split('## 3. TECHNICAL INFRASTRUCTURE')[1].split('## 4.')[0] if '## 4.' in raw_response else raw_response.split('## 3. TECHNICAL INFRASTRUCTURE')[1]
                        st.markdown(infra_section)
                    else:
                        st.info("No infrastructure details available")
            
            # Risk Assessment Tab
            with risk_tab:
                risks = resource_est.get('risks', [])
                
                if risks:
                    for i, risk in enumerate(risks, 1):
                        risk_desc = risk.get('risk', 'Risk identified').replace('**', '').replace('__', '')
                        impact = risk.get('impact_level', risk.get('impact', 'Medium'))
                        mitigation = risk.get('mitigation_strategy', risk.get('mitigation', 'N/A'))
                        
                        # Color code by impact
                        if 'high' in impact.lower():
                            color = "#ffebee"
                        elif 'low' in impact.lower():
                            color = "#e8f5e9"
                        else:
                            color = "#fff9e6"
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {color}; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #666;">
                                <p style="margin: 0; font-weight: bold;">{risk_desc}</p>
                                <p style="margin: 5px 0 0 0; font-size: 0.9em;"><strong>Impact:</strong> {impact}</p>
                                <p style="margin: 5px 0 0 0; font-size: 0.9em;"><strong>Mitigation:</strong> {mitigation}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    # Show raw response if structured parsing failed
                    raw_response = resource_est.get('raw_response', '')
                    if raw_response and '## 4. RISK ASSESSMENT' in raw_response:
                        risk_section = raw_response.split('## 4. RISK ASSESSMENT')[1].split('## 5.')[0] if '## 5.' in raw_response else raw_response.split('## 4. RISK ASSESSMENT')[1]
                        st.markdown(risk_section)
                    else:
                        st.info("No risk assessment details available")
            
            # Success Metrics Tab
            with metrics_tab:
                metrics = resource_est.get('success_metrics', [])
                
                if metrics:
                    for i, metric in enumerate(metrics, 1):
                        metric_name = metric.get('metric', 'Success Metric')
                        target = metric.get('target_value', metric.get('target', 'N/A'))
                        frequency = metric.get('measurement_frequency', metric.get('frequency', 'N/A'))
                        
                        st.markdown(f"**{i}.** {metric_name}")
                        st.markdown(f"Target: {target} | Frequency: {frequency}")
                        st.markdown("")
                else:
                    # Show raw response if structured parsing failed
                    raw_response = resource_est.get('raw_response', '')
                    if raw_response and '## 5. SUCCESS METRICS' in raw_response:
                        metrics_section = raw_response.split('## 5. SUCCESS METRICS')[1]
                        st.markdown(metrics_section)
                    else:
                        st.info("No success metrics available")
        

        # Show development questions
        if workflow_results.get('development_questions'):
            st.markdown("## Development Questions")
            st.info("These AI-generated questions will help you refine your idea during the development phase")
            
            questions = workflow_results['development_questions']
            
            # Initialize answers in session state if not present
            if 'submission_answers' not in st.session_state:
                st.session_state.submission_answers = {}
            
            for i, question in enumerate(questions, 1):
                section = question.get('section', 'General')
                question_text = question.get('question', '')
                # Use the same key logic as idea_development.py to ensure persistence
                key = question.get('key', f"q_{i-1}")
                
                st.markdown(f"**{i}. {section}**")
                st.write(question_text)
                
                # Input for answer
                answer = st.text_area(
                    f"Your answer for Question {i}",
                    value=st.session_state.submission_answers.get(key, ''),
                    key=key,
                    height=100,
                    placeholder="Provide your answer here..."
                )
                st.session_state.submission_answers[key] = answer
                
                if i < len(questions):
                    st.markdown("---")
        
        
        # Download POC Document button
        if st.session_state.workflow_step == "completed":
            st.markdown("---")
            st.subheader("Download POC Document")
            st.info("Download a comprehensive Word document with all research findings and analysis")
            
            if st.button("Download POC Document (DOCX)", type="secondary", key="download_doc_btn"):
                with st.spinner("Generating comprehensive POC document..."):
                    try:
                        # Prepare document data
                        doc_data = {
                            'idea_title': st.session_state.workflow_inputs.get('idea_title', 'Untitled Idea'),
                            'company_name': st.session_state.workflow_inputs.get('company_name', 'Unknown Company'),
                            'idea_description': st.session_state.workflow_inputs.get('idea_description', ''),
                            'company_research': workflow_results.get('company_research'),
                            'idea_research': workflow_results.get('idea_research'),
                            'resource_estimation': workflow_results.get('resource_estimation'),
                            'development_questions': workflow_results.get('development_questions', []),
                            'development_answers': st.session_state.get('submission_answers', {})
                        }
                        
                        # Generate document
                        doc_bytes = research_document_generator.generate_comprehensive_document(doc_data)
                        
                        if doc_bytes:
                            # Create filename
                            safe_title = st.session_state.workflow_inputs.get('idea_title', 'idea').replace(' ', '_')
                            filename = f"POC_{safe_title}.docx"
                            
                            # Provide download button
                            st.download_button(
                                label="Click to Download",
                                data=doc_bytes,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="download_docx_btn"
                            )
                            st.success("Document generated successfully! Click the button above to download.")
                        else:
                            st.error("Failed to generate document. Please try again.")
                            
                    except Exception as e:
                        st.error(f"Error generating document: {str(e)}")
        
        # Save to catalog button
        st.markdown("---")
        st.subheader("Save to Catalog")
        
        if st.button("Save Idea to Catalog", type="primary", key="save_to_catalog_btn"):
            with st.spinner("Saving idea and generating AI score..."):
                try:
                    # Generate a unique session ID
                    session_id = str(uuid.uuid4())

                    # Prepare idea data for saving
                    idea_data = {
                        "session_id": session_id,
                        "title": idea_title,
                        "original_idea": idea_description,
                        "rephrased_idea": idea_description,
                        "metadata": {
                            "submitted_by": "User",
                            "department": "General",
                            "company_name": company_name
                        },
                        "research_data": {
                            "company_research": workflow_results.get('company_research'),
                            "idea_research": workflow_results.get('idea_research'),
                            "resource_estimation": workflow_results.get('resource_estimation'),
                            "development_questions": workflow_results.get('development_questions'),
                        },
                        "drafts": {
                            "development_answers": st.session_state.get('submission_answers', {})
                        }
                    }

                    # Generate AI score (ONLY at save time as requested)
                    ai_score_result = ai_score_service.score_idea(idea_data)
                    
                    if ai_score_result and ai_score_result.get('success'):
                        idea_data['ai_score'] = ai_score_result.get('score', 0)
                        idea_data['ai_feedback'] = ai_score_result.get('feedback', '')
                        idea_data['ai_strengths'] = ai_score_result.get('strengths', [])
                        idea_data['ai_improvements'] = ai_score_result.get('improvements', [])
                        
                        # Save to database
                        saved_idea_id = idea_service.save_or_update_idea(session_id, idea_data)
                        
                        if saved_idea_id:
                            st.success("Idea saved to catalog successfully!")
                            st.balloons()
                            
                            # Reset session state
                            st.session_state.workflow_results = None
                            st.session_state.workflow_step = None
                            st.session_state.workflow_inputs = {}
                            
                            # Show next steps
                            st.info("""
                            **Next Steps:**
                            1. Go to **Idea Development** page to answer the development questions
                            2. View your idea in the **Idea Catalog**
                            3. Check the **Reviewer Dashboard** for detailed analysis
                            """)
                        else:
                            st.error("Failed to save idea to database")
                    else:
                        st.error("Failed to generate AI score for the idea")
                        
                except Exception as e:
                    st.error(f"Error saving idea: {str(e)}")
    
