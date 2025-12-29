import streamlit as st
from models import DexKoDepartment, IdeaStatus

# Sample users for authentication (in production, use SSO)
SAMPLE_USERS = {
    "user@example.com": {
        "password": "password123",
        "name": "John Doe",
        "role": "Employee",
        "department": "Engineering"
    },
    "manager@example.com": {
        "password": "password123",
        "name": "Manager User",
        "role": "Manager",
        "department": "Operations"
    },
    "director@example.com": {
        "password": "password123",
        "name": "Director User",
        "role": "Director",
        "department": "Executive"
    }
}

def initialize_session():
    """Initialize session state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_idea" not in st.session_state:
        st.session_state.current_idea = None
    if "ideas_cache" not in st.session_state:
        st.session_state.ideas_cache = None
    if "idea_drafts" not in st.session_state:
        st.session_state.idea_drafts = {}
    if "perform_research" not in st.session_state:
        st.session_state.perform_research = False
    if "research_results" not in st.session_state:
        st.session_state.research_results = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Submit Idea"
    if "testing_max_questions" not in st.session_state:
        st.session_state.testing_max_questions = 5

def login_user(email: str, password: str):
    """Authenticate user"""
    if email in SAMPLE_USERS:
        user_data = SAMPLE_USERS[email]
        if user_data["password"] == password:
            st.session_state.authenticated = True
            st.session_state.user = {
                "email": email,
                "name": user_data["name"],
                "role": user_data["role"],
                "department": user_data["department"]
            }
            return True
    return False

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_session_id = None
    st.session_state.current_idea = None
    st.session_state.idea_drafts = {}
    st.session_state.research_results = None
    st.session_state.perform_research = False
    st.session_state.active_tab = "Submit Idea"

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)

def is_reviewer() -> bool:
    """Check if user is a reviewer (Manager or Director)"""
    if not is_authenticated():
        return False
    role = st.session_state.user.get("role", "")
    return role in ["Manager", "Director"]

def get_current_user():
    """Get current user data"""
    return st.session_state.get("user")

def get_idea_sections():
    """Get standard idea sections"""
    return [
        {
            "section_heading": "Executive Summary",
            "section_purpose": "Brief overview of the idea and its value proposition",
            "subsections": [
                {"subsection_heading": "Problem Statement", "subsection_definition": "What problem does this idea solve?"},
                {"subsection_heading": "Proposed Solution", "subsection_definition": "How does your idea address the problem?"}
            ]
        },
        {
            "section_heading": "Business Value",
            "section_purpose": "Explain the potential business impact and benefits",
            "subsections": [
                {"subsection_heading": "Value Proposition", "subsection_definition": "What value does this provide?"},
                {"subsection_heading": "Expected Outcomes", "subsection_definition": "What benefits will result from implementation?"}
            ]
        },
        {
            "section_heading": "Implementation Plan",
            "section_purpose": "Outline how the idea will be implemented",
            "subsections": [
                {"subsection_heading": "Key Steps", "subsection_definition": "What are the main implementation steps?"},
                {"subsection_heading": "Resource Requirements", "subsection_definition": "What resources are needed?"}
            ]
        },
        {
            "section_heading": "Risk Analysis",
            "section_purpose": "Identify and mitigate potential risks",
            "subsections": [
                {"subsection_heading": "Potential Risks", "subsection_definition": "What could go wrong?"},
                {"subsection_heading": "Mitigation Strategies", "subsection_definition": "How will you address these risks?"}
            ]
        }
    ]
