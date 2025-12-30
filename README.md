# AI Idea to Reality POC - Streamlit Version

A Python-based Streamlit application for submitting, evaluating, and managing innovative ideas using AI-powered analysis and MongoDB for data persistence.

## Features

✨ **Key Features:**
- 💡 **Idea Submission**: Submit and develop ideas through structured sections
- 🤖 **AI Analysis**: Automatic scoring and feedback using AI
- 📚 **Idea Catalog**: Browse and view all submitted ideas
- 👥 **Reviewer Dashboard**: Manager/Director interface for reviewing and evaluating ideas
- 🔐 **Authentication**: User authentication with role-based access control
- 📊 **Filtering & Sorting**: Filter by status, department, and sort options
- 💾 **MongoDB Integration**: Persistent storage of all ideas and metadata

## Project Structure

```
Idea-to-POC-Enhanced/
├── app.py                      # Main Streamlit application
├── app_enhanced.py            # Enhanced version with additional features
├── models.py                   # Data models and schemas
├── config.py                   # Configuration settings
├── constants.py               # Application constants
├── requirements.txt            # Python dependencies
├── styles.css                  # Custom CSS styles
├── README.md                   # This file
├── ARCHITECTURE_OVERVIEW.md    # Architecture documentation
├── NEW_FEATURES.md             # New features documentation
├── RENDER_DEPLOYMENT.md        # Render deployment guide
├── MONGODB_CONNECTION_GUIDE.md # MongoDB connection guide
├── render.yaml                 # Render deployment configuration
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── test_mongodb_connection.py  # MongoDB connection test script
├── assets/                     # Static assets (logos, images)
│   ├── *.svg
├── pages/                      # Streamlit page modules
│   ├── idea_submission.py
│   ├── idea_catalog.py
│   ├── enhanced_idea_catalog.py
│   ├── idea_development.py
│   ├── reviewer_dashboard.py
│   └── portfolio_dashboard.py
├── services/                   # Business logic services
│   ├── database.py            # MongoDB connection and operations
│   ├── idea_service.py         # Idea CRUD operations
│   ├── ai_score_service.py    # AI scoring and evaluation
│   ├── enhanced_ai_score_service.py
│   ├── research_agent.py
│   ├── idea_research_agent.py
│   ├── company_research_agent.py
│   ├── resource_estimation_agent.py
│   ├── workflow_orchestrator.py
│   ├── portfolio_analytics_service.py
│   ├── research_document_generator.py
│   ├── question_generator.py
│   └── text_cleaner.py
└── utils/                      # Utility functions
    ├── auth.py                 # Authentication and session management
    ├── helpers.py              # Helper functions
    ├── ai_questions.py
    ├── api_optimizer.py
    ├── cache_manager.py
    ├── enhanced_idea_display.py
    ├── error_handler.py
    ├── json_parser.py
    └── score_explanation_ui.py
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MongoDB 4.0 or higher
- pip package manager

### 1. Clone the Project

```bash
git clone https://github.com/damodar04/Idea-to-POC-Enhanced.git
cd Idea-to-POC-Enhanced
```

### 2. Create Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=i2poc
MONGODB_COLLECTION=ideas

# Optional: AI Model Configuration (for AI scoring features)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GPT_4O_API_KEY=your_gpt4o_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/

# Optional: LangSmith Configuration (for monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Setup MongoDB

**Local MongoDB:**
```bash
# Ensure MongoDB is running on localhost:27017
mongod
```

**Or use MongoDB Atlas (Cloud):**
- Create a cluster on https://www.mongodb.com/cloud/atlas
- Get your connection string
- Update `MONGODB_URL` in `.env`

### 6. Test MongoDB Connection (Optional but Recommended)

Before running the app, test your MongoDB connection:

```bash
python test_mongodb_connection.py
```

This will verify:
- Environment variables are set correctly
- MongoDB connection string is valid
- Network access is configured properly
- Database and collection are accessible

### 7. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Usage Guide

### Demo Credentials

The application comes with pre-configured demo users for testing:

| Email | Password | Role | Department |
|-------|----------|------|-----------|
| john.doe@dexko.com | password123 | Employee | Engineering |
| manager@dexko.com | password123 | Manager | Operations |
| director@dexko.com | password123 | Director | Executive |

### Workflows

#### 1. Submit an Idea (Employee)
1. Login with employee credentials
2. Go to "Submit Idea" tab
3. Describe your innovative idea
4. Select your department
5. Click "Analyze & Structure Idea"
6. Fill in structured sections (Executive Summary, Business Value, etc.)
7. Review AI-generated score and feedback
8. Click "Submit to Catalog"

#### 2. View Idea Catalog (All Users)
1. Go to "Idea Catalog" tab
2. Filter by status, department, or search
3. Sort by latest, highest score, or title
4. Click "View Details" to see full idea content and AI feedback

#### 3. Review Ideas (Manager/Director Only)
1. Login with manager or director credentials
2. Go to "Reviewer Dashboard"
3. Review pending ideas with statistics
4. For each idea:
   - Provide an evaluation action (Approve/Reject/Request Changes)
   - Set an evaluation score (0-100)
   - Add constructive feedback
   - Submit review

## API Endpoints Overview

While the application is primarily UI-based via Streamlit, the backend services provide:

- **Database Service**: MongoDB CRUD operations for ideas
- **Idea Service**: Idea creation, retrieval, and status management
- **AI Score Service**: Automated idea evaluation and scoring

## Configuration Options

Edit `config.py` to customize:

```python
# App titles and descriptions
APP_TITLE = "AI Idea to Reality POC"
APP_PAGE_ICON = "💡"

# AI Model settings
USE_AZURE_OPENAI = bool(gpt_4o_api_key and azure_endpoint)
USE_DEEPSEEK = bool(os.getenv("DEEPSEEK_API_KEY"))

# Database settings
MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DATABASE = "i2poc"
```

## Troubleshooting

### MongoDB Connection Error
```
Error: Failed to connect to MongoDB
```

**For Local Development:**
- Ensure MongoDB is running: `mongod`
- Check `MONGODB_URL` in `.env` is correct
- Verify MongoDB is accessible on the configured port

**For Cloud Deployment (Render/MongoDB Atlas):**
- **CRITICAL**: MongoDB Atlas Network Access must allow connections from Render
  - Go to MongoDB Atlas → Network Access → Add IP Address
  - Add `0.0.0.0/0` (allow all) or Render's specific IPs
- Verify connection string format includes `retryWrites=true&w=majority`
- Check username/password are correct and URL-encoded if needed
- Run `python test_mongodb_connection.py` to diagnose issues
- Check Render logs for detailed connection error messages

### Missing Dependencies
```
ModuleNotFoundError: No module named 'streamlit'
```
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

### Port Already in Use
```
Address already in use: 0.0.0.0:8501
```
```bash
streamlit run app.py --server.port 8502
```

### AI Scoring Not Working
- Check if `DEEPSEEK_API_KEY` is set in `.env`
- If not configured, scoring will use default values
- Add your API key and restart the application

## Development

### Adding New Features

1. **New Models**: Add to `models.py`
2. **New Services**: Create files in `services/` directory
3. **New Pages**: Add functions in `app.py` and include in navigation
4. **New Utilities**: Add to `utils/` directory

### Logging

Logging is configured to show important events:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Info message")
logger.error("Error message")
```

## Performance Tips

- **Caching**: Streamlit caches decorated functions automatically
- **Session State**: Use `st.session_state` for persistent data across reruns
- **Database Indexes**: Create MongoDB indexes for frequently queried fields
- **Limits**: Default limit is 100 ideas per query

## Security Considerations

⚠️ **Important for Production:**

1. **Change Demo Credentials**: Update `SAMPLE_USERS` in `utils/auth.py`
2. **Implement SSO**: Replace demo auth with enterprise SSO (Azure AD, etc.)
3. **HTTPS**: Deploy with SSL/TLS certificates
4. **Environment Secrets**: Use environment variables for sensitive data
5. **Database Security**: 
   - Enable MongoDB authentication
   - Use IP whitelisting
   - Encrypt connections
6. **API Keys**: Never commit `.env` files with real keys

## Production Deployment

### Option 1: Render (Recommended)
See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

Quick steps:
1. Push code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables (MongoDB URL, API keys)
5. Deploy!

The `render.yaml` file is included for easy configuration.

### Option 2: Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy directly from main branch

### Option 3: Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Option 4: Self-hosted (Linux)
```bash
# Install Python and dependencies
sudo apt-get install python3 python3-pip

# Setup and run
pip install -r requirements.txt
nohup streamlit run app.py > app.log 2>&1 &
```

## Database Schema

### Ideas Collection
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "title": "string",
  "original_idea": "string",
  "rephrased_idea": "string",
  "sections": [],
  "drafts": {
    "section_name": "draft_content"
  },
  "status": "submitted|under_review|approved|rejected|implemented",
  "ai_score": 0-100,
  "ai_feedback": "string",
  "ai_strengths": [],
  "ai_improvements": [],
  "metadata": {
    "created_at": "datetime",
    "updated_at": "datetime",
    "submitted_by": "string",
    "department": "string"
  }
}
```

## Contributing

To contribute improvements:
1. Create a feature branch
2. Make changes following the code structure
3. Test thoroughly
4. Submit pull request with description



## Support

For issues or questions:
- Check the Troubleshooting section
- Review logs in the Streamlit terminal
- Contact the development team

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Python**: 3.8+
