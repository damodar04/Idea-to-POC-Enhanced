"""Enhanced Idea Details Dialog with 'Why this score?' section"""

import streamlit as st
import logging
from typing import Any, Dict
from services.enhanced_ai_score_service import enhanced_ai_score_service
from utils.score_explanation_ui import (
    render_score_explanation_section,
    render_compact_score_badge,
    render_quick_bias_indicator
)

logger = logging.getLogger(__name__)


@st.dialog("Enhanced Idea Analysis", width="large")
def show_enhanced_idea_details(idea: Any):
    """
    Display enhanced idea details with 'Why this score?' section
    
    Args:
        idea: IdeaDocument object
    """
    st.markdown(f"## {idea.title}")
    
    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        if idea.metadata:
            st.caption(f"**Department:** {getattr(idea.metadata, 'department', 'General')}")
            st.caption(f"**Submitted by:** {getattr(idea.metadata, 'submitted_by', 'Unknown')}")
    with col2:
        if idea.ai_score:
            st.metric("AI Score", f"{idea.ai_score}/100")
    
    st.divider()
    
    # Idea content
    if idea.rephrased_idea:
        st.markdown("### 📝 Idea Summary")
        st.write(idea.rephrased_idea)
    elif idea.original_idea:
        st.markdown("### 📝 Original Idea")
        st.write(idea.original_idea)
    
    st.divider()
    
    # Enhanced Score Analysis Section
    st.markdown("### 🔍 AI Score Analysis")
    
    # Check if we have enhanced score data
    enhanced_data = getattr(idea, 'enhanced_ai_score', None)
    
    if enhanced_data:
        # Use existing enhanced data
        explanation = enhanced_ai_score_service.get_score_explanation(enhanced_data)
        render_score_explanation_section(explanation, idea.title)
    else:
        # Show option to generate enhanced analysis
        st.info("Enhanced score analysis provides detailed reasoning, confidence levels, and bias warnings.")
        
        if st.button("🔬 Generate Detailed Analysis", key=f"gen_enhanced_{idea.session_id}"):
            with st.spinner("Analyzing idea with enhanced AI scoring..."):
                # Prepare idea data
                idea_data = {
                    "title": idea.title,
                    "original_idea": idea.original_idea,
                    "rephrased_idea": idea.rephrased_idea,
                    "metadata": {
                        "department": getattr(idea.metadata, 'department', 'General') if idea.metadata else 'General'
                    },
                    "research_data": idea.research_data,
                    "drafts": idea.drafts
                }
                
                # Get enhanced score
                enhanced_result = enhanced_ai_score_service.score_idea_enhanced(idea_data)
                
                if enhanced_result.get("success"):
                    explanation = enhanced_ai_score_service.get_score_explanation(enhanced_result)
                    render_score_explanation_section(explanation, idea.title)
                else:
                    st.error(f"Analysis failed: {enhanced_result.get('error', 'Unknown error')}")
    
    st.divider()
    
    # Standard AI Analysis (existing features)
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        if idea.ai_feedback:
            st.markdown("**AI Feedback:**")
            st.write(idea.ai_feedback)
    
    with col_detail2:
        if idea.ai_strengths:
            st.markdown("**Strengths:**")
            for strength in idea.ai_strengths:
                st.write(f"✅ {strength}")
        
        if idea.ai_improvements:
            st.markdown("**Areas for Improvement:**")
            for improvement in idea.ai_improvements:
                st.write(f"🔧 {improvement}")
    
    # Research Data Section (if available)
    if idea.research_data:
        st.divider()
        st.markdown("### 📊 Research Data")
        
        tabs = []
        tab_names = []
        
        if idea.research_data.get('company_research'):
            tab_names.append("Company Research")
        if idea.research_data.get('idea_research'):
            tab_names.append("Market Research")
        if idea.research_data.get('resource_estimation'):
            tab_names.append("Resource Estimation")
            
        if tab_names:
            tabs = st.tabs(tab_names)
            
            for i, name in enumerate(tab_names):
                with tabs[i]:
                    if name == "Company Research":
                        data = idea.research_data['company_research']
                        if data.get('what_company_does'):
                            st.write(f"**Overview:** {data['what_company_does']}")
                        if data.get('opportunities'):
                            st.markdown("**Opportunities:**")
                            for item in data['opportunities'][:5]:
                                st.write(f"- {item}")
                                
                    elif name == "Market Research":
                        data = idea.research_data['idea_research']
                        if data.get('market_overview'):
                            st.write(f"**Overview:** {data['market_overview']}")
                        if data.get('competitors'):
                            st.markdown("**Competitors:**")
                            for item in data['competitors'][:5]:
                                if isinstance(item, dict):
                                    st.write(f"- {item.get('name', 'Unknown')}")
                                else:
                                    st.write(f"- {item}")

                    elif name == "Resource Estimation":
                        data = idea.research_data['resource_estimation']
                        if data.get('team_resources'):
                            st.markdown("**Team Resources:**")
                            for item in data['team_resources'][:5]:
                                if isinstance(item, dict):
                                    st.write(f"- {item.get('role', 'Role')}: {item.get('description', '')}")
                                else:
                                    st.write(f"- {item}")


def render_idea_card_with_score_button(idea: Any, idx: int):
    """
    Render an idea card with a 'Why this score?' button
    
    Args:
        idea: IdeaDocument object
        idx: Index for unique keys
    """
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {idea.title}")
            if idea.original_idea:
                preview = idea.original_idea[:150] + "..." if len(idea.original_idea) > 150 else idea.original_idea
                st.caption(preview)
        
        with col2:
            if idea.ai_score:
                render_compact_score_badge(idea.ai_score, confidence=0.7)
        
        with col3:
            status = getattr(idea, 'status', 'submitted')
            if hasattr(status, 'value'):
                status = status.value
            status_colors = {
                "submitted": "🔵",
                "under_review": "🟡",
                "approved": "🟢",
                "rejected": "🔴"
            }
            st.write(f"{status_colors.get(status, '⚪')} {status.replace('_', ' ').title()}")
        
        # Action buttons
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            if st.button("📄 View Details", key=f"view_{idx}_{idea.session_id}"):
                show_enhanced_idea_details(idea)
        
        with bcol2:
            if st.button("🔍 Why this score?", key=f"why_{idx}_{idea.session_id}"):
                show_enhanced_idea_details(idea)
