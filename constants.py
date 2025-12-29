"""
Constants and configuration values
"""

# Idea Structure Sections
SECTIONS = [
    {
        "section_heading": "Executive Summary",
        "section_purpose": "Brief overview of the idea and its value proposition",
        "subsections": [
            {
                "subsection_heading": "Problem Statement",
                "subsection_definition": "What problem does this idea solve?"
            },
            {
                "subsection_heading": "Proposed Solution",
                "subsection_definition": "How does your idea address the problem?"
            }
        ]
    },
    {
        "section_heading": "Business Value",
        "section_purpose": "Explain the potential business impact and benefits",
        "subsections": [
            {
                "subsection_heading": "Value Proposition",
                "subsection_definition": "Why is this valuable for DexKo?"
            },
            {
                "subsection_heading": "Expected Outcomes",
                "subsection_definition": "What benefits will result from implementation?"
            }
        ]
    },
    {
        "section_heading": "Implementation Plan",
        "section_purpose": "Outline how the idea will be implemented",
        "subsections": [
            {
                "subsection_heading": "Key Steps",
                "subsection_definition": "What are the main implementation steps?"
            },
            {
                "subsection_heading": "Resource Requirements",
                "subsection_definition": "What resources are needed?"
            }
        ]
    },
    {
        "section_heading": "Risk Analysis",
        "section_purpose": "Identify and mitigate potential risks",
        "subsections": [
            {
                "subsection_heading": "Potential Risks",
                "subsection_definition": "What could go wrong?"
            },
            {
                "subsection_heading": "Mitigation Strategies",
                "subsection_definition": "How will you address these risks?"
            }
        ]
    }
]

# AI Scoring Criteria
SCORING_CRITERIA = {
    "innovation": {
        "weight": 0.25,
        "description": "How novel and creative is the idea?"
    },
    "feasibility": {
        "weight": 0.25,
        "description": "How practical and implementable is the idea?"
    },
    "business_impact": {
        "weight": 0.25,
        "description": "Potential value to DexKo Group"
    },
    "clarity": {
        "weight": 0.25,
        "description": "How well-defined and structured is the idea?"
    }
}

# Idea Status
IDEA_STATUSES = [
    "submitted",
    "under_review",
    "approved",
    "rejected",
    "implemented",
    "completed",
    "in_progress"
]

# DexKo Departments
DEXKO_DEPARTMENTS = [
    "Engineering",
    "Manufacturing",
    "Sales",
    "Marketing",
    "Finance",
    "Human Resources",
    "IT",
    "Operations",
    "Supply Chain",
    "Other"
]

# User Roles
USER_ROLES = [
    "Employee",
    "Manager",
    "Director",
    "Executive"
]

# Pagination defaults
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# UI Messages
MESSAGES = {
    "success_save": "Idea saved successfully!",
    "error_save": "Error saving idea. Please try again.",
    "success_review": "Review submitted successfully!",
    "error_review": "Error submitting review. Please try again.",
    "no_ideas": "No ideas submitted yet. Start by submitting a new idea!",
    "loading": "Loading...",
    "confirm_logout": "Are you sure you want to logout?"
}
