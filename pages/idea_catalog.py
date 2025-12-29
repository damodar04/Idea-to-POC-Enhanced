"""Idea Catalog Module - Handles displaying and managing saved ideas"""

import streamlit as st
import logging
from services.idea_service import idea_service
from models import IdeaStatus
from utils.helpers import format_datetime

logger = logging.getLogger(__name__)


@st.dialog("Idea Details", width="large")
def show_idea_details_dialog(idea):
    # AI Analysis Section
    col_detail1, col_detail2 = st.columns(2)
    
    with col_detail1:
        if idea.rephrased_idea:
            st.markdown("**Rephrased Idea:**")
            st.write(idea.rephrased_idea)
        
        if idea.ai_feedback:
            st.markdown("**AI Feedback:**")
            st.write(idea.ai_feedback)
    
    with col_detail2:
        if idea.ai_strengths:
            st.markdown("**Strengths:**")
            for strength in idea.ai_strengths:
                st.write(f"- {strength}")
        
        if idea.ai_improvements:
            st.markdown("**Areas for Improvement:**")
            for improvement in idea.ai_improvements:
                st.write(f"- {improvement}")
    
    st.markdown("---")
    
    # Research Data Section (if available)
    if idea.research_data:
        st.subheader("Research Data")
        
        # Create tabs for research data
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

def show_idea_catalog():
    """Show saved ideas catalog with enhanced UI"""
    st.header("Idea Catalog")
    st.markdown("Browse, filter, and manage all submitted ideas in one place.")
    
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
                key="status_filter_select",
                horizontal=True
            )
        
        with col2:
            sort_by = st.radio(
                "Sort by",
                ["Latest", "Highest Score", "Title"],
                horizontal=True,
                key="sort_by_radio"
            )
        
        with col3:
            search_term = st.text_input(
                "Search Ideas",
                placeholder="Search by title...",
                key="search_input"
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
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Total Ideas", len(ideas))
        with col_stats2:
            st.metric("Displayed", len(filtered_ideas))
        with col_stats3:
            avg_score = sum([i.ai_score or 0 for i in filtered_ideas]) / len(filtered_ideas) if filtered_ideas else 0
            st.metric("Avg Score", f"{avg_score:.1f}/100")
        
        st.divider()
        
        # Display ideas with enhanced cards
        if not filtered_ideas:
            st.warning("No ideas match your search criteria.")
            return
        
        for idx, idea in enumerate(filtered_ideas):
            with st.container(border=True):
                # Header with title and score
                col_title, col_score = st.columns([4, 1])
                
                with col_title:
                    st.subheader(idea.title)
                
                with col_score:
                    if idea.ai_score:
                        st.metric("AI Score", f"{idea.ai_score}/100", label_visibility="collapsed")
                
                # Metadata row
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    submitted_by = getattr(idea.metadata, 'submitted_by', 'Unknown') if idea.metadata else 'Unknown'
                    st.caption(f"Author: {submitted_by}")
                with col_b:
                    department = getattr(idea.metadata, 'department', 'N/A') if idea.metadata else 'N/A'
                    st.caption(f"Department: {department}")
                with col_c:
                    created_at = getattr(idea.metadata, 'created_at', None) if idea.metadata else None
                    st.caption(f"Submitted: {format_datetime(created_at) if created_at else 'N/A'}")
                with col_d:
                    st.caption(f"Status: {idea.status.upper()}")
                
                # Idea preview
                if idea.original_idea:
                    st.markdown(f"**Overview:** {idea.original_idea[:250]}..." if len(idea.original_idea) > 250 else f"**Overview:** {idea.original_idea}")
                
                # Expandable details
                if st.button("View Details", key=f"view_{idea.session_id}"):
                    show_idea_details_dialog(idea)


    
    except Exception as e:
        st.error(f"Error loading ideas: {str(e)}")
        logger.error(f"Failed to load ideas: {e}")
