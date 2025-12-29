import os
from dotenv import load_dotenv

# Load variables from .env file into os.environ
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

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "i2poc")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "ideas")

# App configuration
APP_TITLE = "AI Idea to Reality POC"
APP_DESCRIPTION = "Streamlit-based platform for idea submission and evaluation"
APP_PAGE_ICON = ""

# AI Model Configuration
USE_AZURE_OPENAI = bool(gpt_4o_api_key and azure_endpoint)
USE_DEEPSEEK = bool(os.getenv("DEEPSEEK_API_KEY"))
