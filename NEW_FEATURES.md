# New Features Documentation

This document describes the new features added to the AI Idea to Reality POC application.

## Overview

Two major feature sets have been added:

1. **Per-Criterion Score Reasoning with Transparency** - Detailed explanations for AI scores
2. **Innovation Portfolio Dashboard** - Executive-level analytics and insights

---

## Feature 1: Per-Criterion Reasoning & "Why This Score?"

### Description

This feature provides transparency into how ideas are scored by the AI system. Instead of just showing a single score, users can now see:

- **Per-criterion breakdown**: Innovation, Feasibility, Business Impact, Clarity (each 0-25 points)
- **Detailed reasoning**: Explanation for each criterion's score
- **Evidence citations**: Specific quotes/references from the idea that support the score
- **Confidence scores**: How confident the AI is in each assessment (0-100%)
- **Bias warnings**: Alerts for potential issues like insufficient data, domain bias, etc.

### New Files

| File | Purpose |
|------|---------|
| `services/enhanced_ai_score_service.py` | Enhanced AI scoring with detailed analysis |
| `utils/score_explanation_ui.py` | UI components for displaying score explanations |
| `utils/enhanced_idea_display.py` | Enhanced idea display with score buttons |
| `pages/enhanced_idea_catalog.py` | Catalog page with "Why this score?" feature |

### How to Use

1. Navigate to the **Enhanced Catalog** tab
2. Find an idea and click **"🔍 Why this score?"**
3. In the dialog, click **"🔬 Analyze Score Details"**
4. View the detailed breakdown including:
   - Score for each criterion with progress bars
   - Reasoning text explaining the score
   - Confidence indicators
   - Any bias warnings or data quality notes

### UI Components

```python
from utils.score_explanation_ui import render_score_explanation_section

# Render the full "Why this score?" expandable section
render_score_explanation_section(explanation_data, "Idea Title")

# Render a compact score badge for list views
render_compact_score_badge(score=75, confidence=0.8)
```

---

## Feature 2: Innovation Portfolio Dashboard

### Description

An executive-level dashboard providing portfolio-wide intelligence:

- **Idea Clusters**: Group ideas by domain/department, impact level, and risk profile
- **Department Heatmap**: Visualize innovation activity across departments
- **Budget & ROI Projections**: Financial forecasting for approved ideas
- **Strategic Recommendations**: AI-generated action items and insights

### New Files

| File | Purpose |
|------|---------|
| `services/portfolio_analytics_service.py` | Analytics engine for portfolio metrics |
| `pages/portfolio_dashboard.py` | Dashboard UI for executives |

### Dashboard Sections

#### 1. Executive Summary
- Total ideas, average score, approval rate
- High-potential idea count
- Estimated portfolio value
- Ideas by status breakdown

#### 2. Idea Clusters Tab
- **By Domain**: Ideas grouped by department with health indicators
- **By Impact**: High/Medium/Low impact groupings
- **By Risk**: Risk profile distribution

#### 3. Department Heatmap Tab
- Innovation index per department
- Success rates
- Heat visualization (hot/warm/cool)
- Detailed department breakdowns

#### 4. Budget & ROI Tab
- Total estimated investment
- Projected returns and net value
- Per-idea financial projections
- Risk-adjusted confidence levels
- Implementation timelines

#### 5. Recommendations Tab
- High priority actions
- Opportunities identified
- Portfolio health warnings
- Strategic suggestions

### Access Control

The Portfolio Dashboard is only accessible to users with Manager or Director roles.

---

## Running the Enhanced Application

### Option 1: Run Enhanced Version

```bash
streamlit run app_enhanced.py
```

This launches the application with all new features while keeping the original `app.py` unchanged.

### Option 2: Original Application

```bash
streamlit run app.py
```

The original application continues to work as before.

---

## API Reference

### EnhancedAIScoreService

```python
from services.enhanced_ai_score_service import enhanced_ai_score_service

# Get enhanced score with detailed analysis
result = enhanced_ai_score_service.score_idea_enhanced({
    "title": "Idea Title",
    "original_idea": "Description...",
    "metadata": {"department": "Engineering"},
    "research_data": {...}
})

# Format for UI display
explanation = enhanced_ai_score_service.get_score_explanation(result)
```

### PortfolioAnalyticsService

```python
from services.portfolio_analytics_service import portfolio_analytics_service

# Get full portfolio analysis
analytics = portfolio_analytics_service.analyze_portfolio(ideas_list)

# Access specific metrics
summary = analytics["summary"]
clusters = analytics["clusters"]
heatmap = analytics["department_heatmap"]
roi_projections = analytics["budget_roi_projections"]
recommendations = analytics["recommendations"]
```

---

## Configuration

The enhanced AI scoring uses the same API configuration as the original:

```env
# Azure OpenAI (primary)
GPT_4O_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint

# DeepSeek (fallback)
DEEPSEEK_API_KEY=your_key
```

---

## Data Models

### EnhancedIdeaScore

```python
class EnhancedIdeaScore:
    total_score: int                    # 0-100
    criterion_scores: List[CriterionScore]
    overall_confidence: float           # 0.0-1.0
    bias_warnings: List[BiasWarning]
    feedback: str
    strengths: List[str]
    improvements: List[str]
    data_quality_notes: str
```

### CriterionScore

```python
class CriterionScore:
    criterion_name: str      # e.g., "Innovation"
    score: int               # 0-25
    max_score: int           # 25
    reasoning: str           # Detailed explanation
    evidence: List[str]      # Supporting quotes
    confidence: float        # 0.0-1.0
```

### BiasWarning

```python
class BiasWarning:
    warning_type: str    # e.g., "insufficient_data"
    severity: str        # "low", "medium", "high"
    description: str     # Detailed description
    mitigation: str      # Suggested action
```

---

## Screenshots

### "Why This Score?" Section
- Expandable panel showing full score breakdown
- Color-coded progress bars for each criterion
- Confidence indicators with labels
- Bias warnings with severity icons

### Portfolio Dashboard
- Executive summary with key metrics
- Interactive cluster visualizations
- Department heatmap with innovation indices
- ROI projection tables with filtering

---

## Future Enhancements

Potential additions for future versions:

1. **Trend Analysis**: Historical tracking of portfolio metrics
2. **Export Reports**: PDF/Excel export of dashboard data
3. **Custom Scoring Weights**: Adjustable criterion weights
4. **Comparative Analysis**: Benchmark against industry standards
5. **Integration with Project Management**: Link to Jira/Azure DevOps
