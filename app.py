"""Main Streamlit Application - Modularized version"""

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
    get_current_user
)
from pages.idea_submission import show as show_submit_idea
from pages.idea_catalog import show_idea_catalog
from pages.reviewer_dashboard import show_reviewer_dashboard
from services.database import Database

# Page config
st.set_page_config(
    page_title="AI Idea to Reality POC",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
initialize_session()

# Initialize MongoDB connection at startup
@st.cache_resource
def init_database():
    """Initialize and verify MongoDB connection at startup"""
    try:
        logger.info("Initializing MongoDB connection...")
        if Database.connect_db():
            logger.info("✅ MongoDB connection initialized successfully")
            return True
        else:
            logger.error("❌ Failed to initialize MongoDB connection")
            return False
    except Exception as e:
        logger.error(f"❌ Error initializing MongoDB: {e}")
        return False

# Initialize database connection
if 'db_initialized' not in st.session_state:
    db_status = init_database()
    st.session_state.db_initialized = db_status
    if not db_status:
        logger.warning("Database connection failed at startup. Will retry on first use.")

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
        # Try to display philosophy.svg logo
        try:
            st.image("assets/6866b1d280bd0335ad8ab8ca_Augent-Philosophy.svg", width=120, caption="")
        except FileNotFoundError:
            # Fallback to text if logo not available
            st.markdown("<h1 style='text-align: center; color: #792a85; font-weight: 600;'>Augent Innovation Hub</h1>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>AI-Powered Idea Development & Evaluation</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Use empty values for production, or keep pre-filled for demo
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
        # Display philosophy.svg logo with further increased size
        try:
            st.image("assets/6866b1d280bd0335ad8ab8ca_Augent-Philosophy.svg", width=120, caption="")
        except:
            st.markdown("### Augent")
    
    with col2:
        st.markdown("<h3 style='text-align: center; color: #792a85; margin-top: 10px; font-weight: 600;'>Innovation Hub</h3>", unsafe_allow_html=True)
    
    with col3:
        if st.button(f"Logout", use_container_width=False, key="logout_btn"):
            logout_user()
            st.rerun()

def main():
    # Main application logic
    
    # Check if user is authenticated
    if not is_authenticated():
        show_login_page()
        return
    
    # Check database connection status
    if not st.session_state.get('db_initialized', False):
        # Try to reconnect
        if not Database.verify_connection():
            if not Database.connect_db():
                st.error("⚠️ **Database Connection Issue**: Unable to connect to MongoDB. Please check your connection settings and ensure MongoDB Atlas allows connections from this server.")
                st.info("**Troubleshooting**: Check Render logs for detailed error messages. Verify MongoDB Atlas Network Access settings.")
                return
    
    # Show top navigation with logo
    show_top_nav()
    
    # Main menu - tabs at the top
    selected = None
    if option_menu:
        # Get current tab from session state
        current_tab = st.session_state.get("active_tab", "Submit Idea")
        default_index = ["Submit Idea", "Idea Catalog", "Reviewer Dashboard"].index(current_tab) if current_tab in ["Submit Idea", "Idea Catalog", "Reviewer Dashboard"] else 0
        default_index = ["Submit Idea", "Idea Catalog", "Reviewer Dashboard"].index(current_tab) if current_tab in ["Submit Idea", "Idea Catalog", "Reviewer Dashboard"] else 0
        
        selected = option_menu(
            menu_title=None,
            options=["Submit Idea", "Idea Catalog", "Reviewer Dashboard"],
            icons=["pencil", "book", "people"],
            orientation="horizontal",
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#f9f5fa"},
                "icon": {"color": "#792a85", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#e6d6ea"},
                "nav-link-selected": {"background-color": "#792a85", "font-weight": "600"}
            }
        )
        

        # Update active tab in session state when menu selection changes
        if selected:
            st.session_state.active_tab = selected
    else:
        # Fallback to tabs if option_menu is not available
        tab1, tab2, tab3 = st.tabs(["Submit Idea", "Idea Catalog", "Reviewer Dashboard"])
        with tab1:
            st.session_state.active_tab = "Submit Idea"
            show_submit_idea()
        with tab2:
            st.session_state.active_tab = "Idea Catalog"
            show_idea_catalog()
        with tab3:
            st.session_state.active_tab = "Reviewer Dashboard"
            show_reviewer_dashboard()
        return
    
    # Show selected page
    # Show selected page
    if selected == "Submit Idea":
        show_submit_idea()
    elif selected == "Idea Catalog":
        show_idea_catalog()
    elif selected == "Reviewer Dashboard":
        show_reviewer_dashboard()



if __name__ == "__main__":
    main()
