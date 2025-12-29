"""Enhanced Idea Catalog Module - Includes 'Why this score?' functionality"""

import streamlit as st
import logging
from services.idea_service import idea_service
from services.enhanced_ai_score_service import enhanced_ai_score_service
from models import IdeaStatus
from utils.helpers import format_datetime
from utils.score_explanation_ui import render_score_explanation_section

logger = logging.getLogger(__name__)


@st.dialog("Idea Details with Score Explanation", width="large")
def show_enhanced_idea_details_dialog(idea):
    """Enhanced idea details dialog with 'Why this score?' section"""
    
    st.markdown(f"## {idea.title}")
    
    # Basic info header
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        submitted_by = getattr(idea.metadata, 'submitted_by', 'Unknown') if idea.metadata else 'Unknown'
        st.caption(f"**Author:** {submitted_by}")
    with col_info2:
        department = getattr(idea.metadata, 'department', 'N/A') if idea.metadata else 'N/A'
        st.caption(f"**Department:** {department}")
    with col_info3:
        if idea.ai_score:
            score_color = "#28a745" if idea.ai_score >= 75 else "#ffc107" if idea.ai_score >= 50 else "#dc3545"
            st.markdown(f"""
            <div style='text-align: center; padding: 5px; background-color: {score_color}20; border-radius: 10px;'>
                <h3 style='margin: 0; color: {score_color};'>{idea.ai_score}/100</h3>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # AI Analysis Section
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        if idea.rephrased_idea:
            st.markdown("**📝 Refined Idea:**")
            st.write(idea.rephrased_idea)
        elif idea.original_idea:
            st.markdown("**📝 Original Idea:**")
            st.write(idea.original_idea)
        
        if idea.ai_feedback:
            st.markdown("**💬 AI Feedback:**")
            st.write(idea.ai_feedback)
    
    with col_detail2:
        if idea.ai_strengths:
            st.markdown("**✅ Strengths:**")
            for strength in idea.ai_strengths:
                st.write(f"- {strength}")
        
        if idea.ai_improvements:
            st.markdown("**🔧 Areas for Improvement:**")
            for improvement in idea.ai_improvements:
                st.write(f"- {improvement}")
    
    st.divider()
    
    # "Why this score?" Section - The new feature
    st.markdown("### 🔍 Why This Score?")
    st.caption("Get detailed per-criterion reasoning, confidence levels, and potential bias warnings.")
    
    # Check for cached enhanced score
    enhanced_score_key = f"enhanced_score_{idea.session_id}"
    
    if enhanced_score_key in st.session_state:
        # Display cached enhanced score
        explanation = st.session_state[enhanced_score_key]
        render_score_explanation_section(explanation, idea.title)
    else:
        # Show button to generate enhanced analysis
        if st.button("🔬 Analyze Score Details", key=f"analyze_{idea.session_id}", use_container_width=True):
            with st.spinner("Generating detailed score analysis..."):
                try:
                    # Prepare idea data for enhanced scoring
                    idea_data = {
                        "title": idea.title,
                        "original_idea": idea.original_idea,
                        "rephrased_idea": idea.rephrased_idea,
                        "metadata": {
                            "department": getattr(idea.metadata, 'department', 'General') if idea.metadata else 'General'
                        },
                        "research_data": idea.research_data if idea.research_data else {},
                        "drafts": idea.drafts if idea.drafts else {}
                    }
                    
                    # Get enhanced score
                    enhanced_result = enhanced_ai_score_service.score_idea_enhanced(idea_data)
                    
                    if enhanced_result.get("success"):
                        explanation = enhanced_ai_score_service.get_score_explanation(enhanced_result)
                        # Cache the result
                        st.session_state[enhanced_score_key] = explanation
                        render_score_explanation_section(explanation, idea.title)
                    else:
                        st.error(f"Analysis failed: {enhanced_result.get('error', 'Unknown error')}")
                        st.info("Please try again or check your AI service configuration.")
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
                    logger.error(f"Enhanced score analysis failed: {e}")
    
    st.divider()
    
    # Research Data Section (if available)
    if idea.research_data:
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


def show_enhanced_idea_catalog():
    """Show enhanced idea catalog with 'Why this score?' feature"""
    st.header("📚 Idea Catalog")
    st.markdown("Browse, filter, and analyze all submitted ideas with detailed score explanations.")
    
    try:
        ideas = idea_service.get_all_ideas()
        
        if not ideas:
            st.info("No ideas submitted yet. Start by submitting a new idea!")
            return
        
        st.divider()
        
        # Enhanced filter and sort controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.radio(
                "Filter by Status",
                ["All"] + [s.value for s in IdeaStatus],
                index=0,
                key="enhanced_status_filter",
                horizontal=True
            )
        
        with col2:
            sort_by = st.radio(
                "Sort by",
                ["Latest", "Highest Score", "Title"],
                horizontal=True,
                key="enhanced_sort_by"
            )
        
        with col3:
            search_term = st.text_input(
                "Search Ideas",
                placeholder="Search by title...",
                key="enhanced_search"
            )
        
        st.divider()
        
        # Filter ideas
        filtered_ideas = ideas
        if status_filter != "All":
            filtered_ideas = [i for i in filtered_ideas if i.status == status_filter]
        
        # Search filter
        if search_term:
            filtered_ideas = [
                i for i in filtered_ideas 
                if (search_term.lower() in i.title.lower()) or 
                   (i.original_idea and search_term.lower() in i.original_idea.lower())
            ]
        
        # Sort ideas
        if sort_by == "Highest Score":
            filtered_ideas = sorted(filtered_ideas, key=lambda x: x.ai_score or 0, reverse=True)
        elif sort_by == "Title":
            filtered_ideas = sorted(filtered_ideas, key=lambda x: x.title)
        
        # Display stats
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.metric("Total Ideas", len(ideas))
        with col_stats2:
            st.metric("Displayed", len(filtered_ideas))
        with col_stats3:
            avg_score = sum([i.ai_score or 0 for i in filtered_ideas]) / len(filtered_ideas) if filtered_ideas else 0
            st.metric("Avg Score", f"{avg_score:.1f}/100")
        with col_stats4:
            high_score_count = len([i for i in filtered_ideas if (i.ai_score or 0) >= 75])
            st.metric("High Potential", high_score_count)
        
        st.divider()
        
        # Display ideas with enhanced cards
        if not filtered_ideas:
            st.warning("No ideas match your search criteria.")
            return
        
        for idx, idea in enumerate(filtered_ideas):
            with st.container(border=True):
                # Header with title, score, and status
                col_title, col_score, col_status = st.columns([3, 1, 1])
                
                with col_title:
                    st.subheader(idea.title)
                
                with col_score:
                    if idea.ai_score:
                        score = idea.ai_score
                        score_color = "#28a745" if score >= 75 else "#ffc107" if score >= 50 else "#dc3545"
                        st.markdown(f"""
                        <div style='text-align: center; padding: 8px; background-color: {score_color}20; 
                                    border-radius: 10px; border: 2px solid {score_color};'>
                            <span style='font-size: 1.5em; font-weight: bold; color: {score_color};'>{score}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_status:
                    status = idea.status
                    if hasattr(status, 'value'):
                        status = status.value
                    status_colors = {
                        "submitted": "#17a2b8",
                        "under_review": "#ffc107",
                        "approved": "#28a745",
                        "rejected": "#dc3545",
                        "in_progress": "#6f42c1"
                    }
                    color = status_colors.get(status, "#6c757d")
                    st.markdown(f"""
                    <div style='text-align: center; padding: 8px; background-color: {color}20; 
                                border-radius: 10px;'>
                        <span style='color: {color}; font-weight: bold; text-transform: uppercase;'>
                            {status.replace('_', ' ')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Metadata row
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    submitted_by = getattr(idea.metadata, 'submitted_by', 'Unknown') if idea.metadata else 'Unknown'
                    st.caption(f"👤 **Author:** {submitted_by}")
                with col_b:
                    department = getattr(idea.metadata, 'department', 'N/A') if idea.metadata else 'N/A'
                    st.caption(f"🏢 **Department:** {department}")
                with col_c:
                    created_at = getattr(idea.metadata, 'created_at', None) if idea.metadata else None
                    st.caption(f"📅 **Submitted:** {format_datetime(created_at) if created_at else 'N/A'}")
                
                # Idea preview
                if idea.original_idea:
                    preview = idea.original_idea[:200] + "..." if len(idea.original_idea) > 200 else idea.original_idea
                    st.markdown(f"**Overview:** {preview}")
                
                # Quick insights (if available)
                if idea.ai_strengths:
                    st.caption(f"✅ Key strength: {idea.ai_strengths[0]}" if idea.ai_strengths else "")
                
                # Action buttons - including "Why this score?"
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
                
                with btn_col1:
                    if st.button("📄 View Details", key=f"enhanced_view_{idx}_{idea.session_id}", use_container_width=True):
                        show_enhanced_idea_details_dialog(idea)
                
                with btn_col2:
                    if st.button("🔍 Why this score?", key=f"enhanced_why_{idx}_{idea.session_id}", use_container_width=True):
                        show_enhanced_idea_details_dialog(idea)
    
    except Exception as e:
        st.error(f"Error loading ideas: {str(e)}")
        logger.error(f"Failed to load enhanced idea catalog: {e}")
