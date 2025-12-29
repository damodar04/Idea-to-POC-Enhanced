"""Reviewer Dashboard Module - Handles reviewer functionality for managers/directors"""

import streamlit as st
import logging
from services.idea_service import idea_service
from models import IdeaStatus
from utils.auth import is_reviewer
from utils.helpers import format_datetime
from datetime import datetime

logger = logging.getLogger(__name__)

def show_reviewer_dashboard():
    """Show reviewer dashboard for managers/directors with enhanced UI"""
    st.header("Reviewer Dashboard")
    st.markdown("Review and manage submitted ideas with detailed evaluation tools.")
    
    if not is_reviewer():
        st.error("You don't have access to this section. Only Managers and Directors can review ideas.")
        return
    
    try:
        # idea_service is imported from services
        ideas = idea_service.get_all_ideas(limit=100)
        
        st.divider()
        
        # Enhanced dashboard statistics
        submitted = len([i for i in ideas if i.status == IdeaStatus.SUBMITTED])
        under_review = len([i for i in ideas if i.status == IdeaStatus.UNDER_REVIEW])
        approved = len([i for i in ideas if i.status == IdeaStatus.APPROVED])
        rejected = len([i for i in ideas if i.status == IdeaStatus.REJECTED])
        avg_score = sum([i.ai_score or 0 for i in ideas]) / len(ideas) if ideas else 0
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Pending", submitted, delta=f"{submitted} waiting")
        with col2:
            st.metric("In Review", under_review)
        with col3:
            st.metric("Approved", approved)
        with col4:
            st.metric("Rejected", rejected)
        with col5:
            st.metric("Avg Score", f"{avg_score:.1f}")
        with col6:
            st.metric("Total", len(ideas))
        
        st.divider()
        
        # Search and filter
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_term = st.text_input(
                "Search ideas",
                placeholder="Search by title or author..."
            )
        
        with col_search2:
            review_filter = st.radio(
                "Show",
                ["All Pending", "All Ideas", "Under Review", "Approved", "Rejected"],
                horizontal=True,
                key="review_filter_radio"
            )
        
        st.divider()
        
        # Ideas list with enhanced display
        st.subheader("Ideas Awaiting Review")
        
        # Apply filters
        filtered_ideas = ideas
        if review_filter == "All Pending":
            filtered_ideas = [i for i in ideas if i.status == IdeaStatus.SUBMITTED]
        elif review_filter == "All Ideas":
            filtered_ideas = ideas
        elif review_filter == "Under Review":
            filtered_ideas = [i for i in ideas if i.status == IdeaStatus.UNDER_REVIEW]
        elif review_filter == "Approved":
            filtered_ideas = [i for i in ideas if i.status == IdeaStatus.APPROVED]
        elif review_filter == "Rejected":
            filtered_ideas = [i for i in ideas if i.status == IdeaStatus.REJECTED]
        
        # Apply search
        if search_term:
            filtered_ideas = [
                i for i in filtered_ideas
                if search_term.lower() in i.title.lower() or 
                   (i.metadata and search_term.lower() in getattr(i.metadata, 'submitted_by', '').lower())
            ]
        
        if not filtered_ideas:
            st.info("All ideas have been reviewed!" if review_filter == "All Pending" else "No ideas match your search criteria.")
            return
        
        # Display ideas for review
        for idx, idea in enumerate(filtered_ideas):
            with st.container(border=True):
                # Idea header
                col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
                
                with col_header1:
                    st.subheader(idea.title)
                
                with col_header2:
                    if idea.ai_score:
                        st.metric("AI Score", f"{idea.ai_score}")
                
                with col_header3:
                    status_text = {"submitted": "Pending", "under_review": "In Review", "approved": "Approved", "rejected": "Rejected"}
                    st.metric("Status", status_text.get(idea.status, "Unknown"))
                
                # Metadata
                col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
                with col_meta1:
                    submitted_by = getattr(idea.metadata, 'submitted_by', 'Unknown') if idea.metadata else 'Unknown'
                    st.caption(f"**Author:** {submitted_by}")
                with col_meta2:
                    department = getattr(idea.metadata, 'department', 'N/A') if idea.metadata else 'N/A'
                    st.caption(f"**Department:** {department}")
                with col_meta3:
                    created_at = getattr(idea.metadata, 'created_at', None) if idea.metadata else None
                    st.caption(f"**Submitted:** {format_datetime(created_at) if created_at else 'N/A'}")
                with col_meta4:
                    st.caption(f"**Session ID:** {idea.session_id[:8]}...")
                
                # Idea content preview
                st.markdown(f"**Idea:** {idea.original_idea[:300]}..." if len(idea.original_idea) > 300 else f"**Idea:** {idea.original_idea}")
                

                # Review section
                if idea.status == IdeaStatus.SUBMITTED:
                    # Create a unique form key using session_id and index
                    form_key = f"review_form_{idx}_{idea.session_id}"
                    
                    with st.form(key=form_key):
                        col_form1, col_form2 = st.columns(2)
                        
                        with col_form1:
                            action = st.radio(
                                "Action",
                                ["Approve", "Request Changes", "Reject"],
                                key=f"action_{form_key}",
                                horizontal=True
                            )
                        
                        with col_form2:
                            score = st.slider(
                                "Evaluation Score",
                                0, 100, idea.ai_score or 75,
                                key=f"score_{form_key}"
                            )
                        
                        feedback = st.text_area(
                            "Feedback (Optional)",
                            placeholder="Provide constructive feedback to help improve this idea...",
                            height=80,
                            key=f"feedback_{form_key}"
                        )
                        
                        col_submit1, col_submit2 = st.columns(2)
                        with col_submit1:
                            if st.form_submit_button("Submit Review", use_container_width=True):
                                # Determine status based on action
                                status_map = {
                                    "Approve": IdeaStatus.APPROVED,
                                    "Reject": IdeaStatus.REJECTED,
                                    "Request Changes": IdeaStatus.UNDER_REVIEW
                                }
                                
                                idea_service.update_idea(idea.session_id, {
                                    "status": status_map.get(action, IdeaStatus.SUBMITTED).value,
                                    "evaluation_score": score,
                                    "reviewer_feedback": feedback,
                                    "metadata.updated_at": datetime.utcnow()
                                })
                                
                                st.success(f"Review submitted for '{idea.title}'")
                                st.rerun()
                else:
                    # Show review history for already reviewed ideas
                    status_badges = {
                        "approved": "Approved",
                        "rejected": "Rejected",
                        "under_review": "Awaiting Changes"
                    }
                    st.info(f"**Status:** {status_badges.get(idea.status, idea.status)}")
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Failed to load reviewer dashboard: {e}")

