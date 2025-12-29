"""Enhanced Main Streamlit Application - With Portfolio Dashboard and Score Explanations

This is an enhanced version of the main application that includes:
1. Per-criterion reasoning trace with confidence scores and bias warnings
2. "Why this score?" expandable sections in idea views
3. Innovation Portfolio Dashboard for executives
   - Idea clusters (by domain, impact, risk)
   - Department-wise innovation heatmap
   - Budget vs ROI projections

To run this enhanced version:
    streamlit run app_enhanced.py

The original app.py remains unchanged.
"""

import streamlit as st
import logging

try:
    from streamlit_option_menu import option_menu
except ImportError:
    option_menu = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import utilities and services
from utils.auth import (
    initialize_session, is_authenticated, login_user, logout_user, 
    get_current_user, is_reviewer
)

# Import original pages
from pages.idea_submission import show as show_submit_idea
from pages.idea_catalog import show_idea_catalog
from pages.reviewer_dashboard import show_reviewer_dashboard

# Import new enhanced pages
from pages.enhanced_idea_catalog import show_enhanced_idea_catalog
from pages.portfolio_dashboard import show_portfolio_dashboard

# Page config
st.set_page_config(
    page_title="AI Idea to Reality POC - Enhanced",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
initialize_session()

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Style file {file_name} not found. Using default styles.")

load_css("styles.css")


def show_login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            st.image("assets/6866b1d280bd0335ad8ab8ca_Augent-Philosophy.svg", width=120, caption="")
        except FileNotFoundError:
            st.markdown("<h1 style='text-align: center; color: #792a85; font-weight: 600;'>Augent Innovation Hub</h1>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>AI-Powered Idea Development & Evaluation</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #792a85; font-size: 0.9rem;'>✨ Enhanced Version with Portfolio Analytics</p>", unsafe_allow_html=True)
        
        st.divider()
        
        email = st.text_input("Email", value="manager@example.com", placeholder="user@example.com")
        password = st.text_input("Password", value="password123", type="password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", use_container_width=True):
                if login_user(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try: user@example.com / manager@example.com / director@example.com")
        
        st.markdown("---")
        st.info("Demo Credentials:\n- user@example.com (Employee)\n- manager@example.com (Manager) - Pre-filled\n- director@example.com (Director)")


def show_top_nav():
    """Display top navigation bar with logo and user info"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            st.image("assets/6866b1d280bd0335ad8ab8ca_Augent-Philosophy.svg", width=120, caption="")
        except:
            st.markdown("### Augent")
    
    with col2:
        st.markdown("<h3 style='text-align: center; color: #792a85; margin-top: 10px; font-weight: 600;'>Innovation Hub <span style='font-size: 0.6em; color: #28a745;'>Enhanced</span></h3>", unsafe_allow_html=True)
    
    with col3:
        if st.button(f"Logout", use_container_width=False, key="logout_btn"):
            logout_user()
            st.rerun()


def main():
    """Main application logic with enhanced features"""
    
    # Check if user is authenticated
    if not is_authenticated():
        show_login_page()
        return
    
    # Show top navigation with logo
    show_top_nav()
    
    # Determine available menu options based on user role
    menu_options = ["Submit Idea", "Idea Catalog", "Enhanced Catalog"]
    menu_icons = ["pencil", "book", "stars"]
    
    # Add reviewer options if user has access
    if is_reviewer():
        menu_options.extend(["Reviewer Dashboard", "Portfolio Dashboard"])
        menu_icons.extend(["people", "graph-up-arrow"])
    
    # Main menu - tabs at the top
    selected = None
    if option_menu:
        current_tab = st.session_state.get("active_tab", "Submit Idea")
        default_index = menu_options.index(current_tab) if current_tab in menu_options else 0
        
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=menu_icons,
            orientation="horizontal",
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#f9f5fa"},
                "icon": {"color": "#792a85", "font-size": "18px"}, 
                "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "--hover-color": "#e6d6ea"},
                "nav-link-selected": {"background-color": "#792a85", "font-weight": "600"}
            }
        )
        
        if selected:
            st.session_state.active_tab = selected
    else:
        # Fallback to tabs if option_menu is not available
        if is_reviewer():
            tab1, tab2, tab3, tab4, tab5 = st.tabs(menu_options)
            tabs = [tab1, tab2, tab3, tab4, tab5]
        else:
            tab1, tab2, tab3 = st.tabs(menu_options)
            tabs = [tab1, tab2, tab3]
        
        with tabs[0]:
            show_submit_idea()
        with tabs[1]:
            show_idea_catalog()
        with tabs[2]:
            show_enhanced_idea_catalog()
        if is_reviewer():
            with tabs[3]:
                show_reviewer_dashboard()
            with tabs[4]:
                show_portfolio_dashboard()
        return
    
    # Show selected page
    if selected == "Submit Idea":
        show_submit_idea()
    elif selected == "Idea Catalog":
        show_idea_catalog()
    elif selected == "Enhanced Catalog":
        show_enhanced_idea_catalog()
    elif selected == "Reviewer Dashboard":
        show_reviewer_dashboard()
    elif selected == "Portfolio Dashboard":
        show_portfolio_dashboard()


if __name__ == "__main__":
    main()
