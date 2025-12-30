import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load variables from .env file into os.environ (only for local development)
# On Render, environment variables are set directly, so this won't override them
load_dotenv()

# Set LANGCHAIN environment variables (optional - only if API key is available)
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
# Disabled LangSmith tracing to prevent Forbidden errors with invalid keys
# if langsmith_api_key:
#     os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_PROJECT"] = "ai_idea_to_reality_poc_streamlit"

# Set GROQ (optional - only if API key is available)
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key

# GPT-4o Azure setup
gpt_4o_api_key = os.getenv("GPT_4O_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Database configuration - REQUIRED for production
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "i2poc")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "ideas")

# Validate required environment variables
if not MONGODB_URL:
    error_msg = (
        "MONGODB_URL environment variable is not set!\n"
        "Please set MONGODB_URL in your environment variables.\n"
        "For Render: Go to Dashboard → Your Service → Environment → Add MONGODB_URL\n"
        "For local: Create a .env file with MONGODB_URL=your_connection_string"
    )
    logger.error(error_msg)
    # Don't raise exception here - let the app start and show error in UI
    # This allows the app to start even if MongoDB isn't configured yet
else:
    # Safety check: Reject localhost URLs (not allowed in production/cloud)
    if "localhost" in MONGODB_URL.lower() or "127.0.0.1" in MONGODB_URL:
        error_msg = (
            f"ERROR: MONGODB_URL contains localhost/127.0.0.1 which is not allowed!\n"
            f"Current URL: {MONGODB_URL[:50]}...\n"
            f"For Render/Cloud deployment, you MUST use MongoDB Atlas connection string.\n"
            f"Format: mongodb+srv://username:password@cluster.mongodb.net/..."
        )
        logger.error(error_msg)
        # Set to None to prevent connection attempts
        MONGODB_URL = None
    else:
        # Log that MongoDB URL is configured (but don't log the full URL for security)
        url_preview = MONGODB_URL[:30] + "..." if len(MONGODB_URL) > 30 else MONGODB_URL
        logger.info(f"MongoDB URL configured: {url_preview}")
        logger.info(f"MongoDB Database: {MONGODB_DATABASE}, Collection: {MONGODB_COLLECTION}")

# App configuration
APP_TITLE = "AI Idea to Reality POC"
APP_DESCRIPTION = "Streamlit-based platform for idea submission and evaluation"
APP_PAGE_ICON = ""

# AI Model Configuration
USE_AZURE_OPENAI = bool(gpt_4o_api_key and azure_endpoint)
USE_DEEPSEEK = bool(os.getenv("DEEPSEEK_API_KEY"))
